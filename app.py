import sqlalchemy
from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from sqlalchemy import func


load_dotenv('.env', override=True)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (f'postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}'
                                         f'@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
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


def fetch_people(num_people_to_fetch=1000):
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
                    photo=photo_data)

                db.session.add(new_person)
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


@app.route('/load_random_people', methods=['POST'])
def load_random_people():
    people_count = int(request.form.get('people_count', 10))
    fetch_people(people_count)
    flash(f'Successfully loaded {people_count} people!', 'success')
    return redirect(url_for('homepage'))


@app.route('/', methods=['GET', 'POST'])
def homepage():
    per_page = int(request.args.get('per_page', 10))
    page = int(request.args.get('page', 1))

    people = People.query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'homepage.html',
        people=people,
        per_page=per_page,
        url='http://homepage/'
    )


@app.route('/<int:user_id>')
def get_profile(user_id):
    person = People.query.get_or_404(user_id)
    return render_template('profile.html', person=person)


@app.route('/random')
def get_random_profile():
    random_person = People.query.order_by(func.random()).first()
    return render_template('profile.html', person=random_person)


if __name__ == '__main__':
    app.run()
