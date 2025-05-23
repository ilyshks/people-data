import sqlalchemy
from flask import Flask, render_template
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (f'postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}'
                                         f'@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
from models import People


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


def get_people_data(num=1):
    try:
        url = f'https://randomuser.me/api/?results={num}'
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['results']
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return None


def fetch_people():
    num_people_to_fetch = 1000
    people_added = 0

    while people_added < num_people_to_fetch:
        fetched_people = get_people_data(num_people_to_fetch - people_added)

        if not fetched_people:
            print("Не удалось получить больше данных.")
            break

        commit_counter = 0
        people_added_in_transaction = 0
        for person in fetched_people:
            photo_link = person['picture']['medium']
            try:
                photo_data = requests.get(photo_link).content

                new_person = People(
                    gender=person['gender'],
                    first_name=person['name']['first'],
                    last_name=person['name']['last'],
                    phone_number=person['phone'],
                    email=person['email'],
                    location=person['location'],
                    photo=photo_data,
                    profile=None)

                db.session.add(new_person)
                db.session.flush()
                profile_url = f'http://homepage/{new_person.id}'
                new_person.profile = profile_url
                commit_counter += 1
                people_added_in_transaction += 1
                if commit_counter % 100 == 0:
                    people_added += people_added_in_transaction
                    db.session.commit()
                    people_added_in_transaction = 0

            except sqlalchemy.exc.IntegrityError as e:
                db.session.rollback()
                people_added_in_transaction = 0
                print(f"Ошибка уникальности email: {e}")
                continue

        db.session.commit()
        people_added += people_added_in_transaction


@app.cli.command("fetch-people")
def fetch_people_command():
    """Загрузить данные о 1000 человек"""
    with app.app_context():
        if not People.query.first():
            fetch_people()
            print("Успешно загружено 1000 человек")
        else:
            print("Таблица уже содержит данные. Пропускаем загрузку.")


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
