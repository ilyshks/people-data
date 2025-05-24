# People Data Service

## Назначение сервиса

**People Data Service** — сервис для получения, хранения и отображения случайных данных о людях, полученных с публичного API [randomuser.me](https://randomuser.me/).

## Технологии

* **Python 3.12**
* **Flask** - веб-фреймворк, отлично подходит для небольшого сервиса.
* **SQLAlchemy** - ORM для работы с базой данных.
* **PostgreSQL** - база данных, использую её, так как важны плюсы реляционной БД в проекте.
* **Nginx** - веб-сервер и reverse proxy.
* **Waitress** - WSGI сервер для production.
* **unittest** - библиотека для модульного тестирования.
* **Docker** - для контейнеризации.
* **Docker Compose** - для оркестрации контейнеров.
* **PgAdmin** - веб-интерфейс для администрирования PostgreSQL.

## Запуск сервиса

### Локальный запуск

1.  **Установка зависимостей:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Настройка переменных окружения:**

    Создайте файл `.env`  и настройте следующие переменные:

    ```
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_HOST=your_db_host
    DB_PORT=your_db_port
    DB_NAME=your_db_name
    SECRET_KEY=your_secret_key  # Сгенерируйте случайный ключ
    ```
3. **Генерация ключа приложения:**

   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   
4. **Выполнение миграций:**

    ```bash
    flask db upgrade
    ```

5.  **Загрузка данных о 1000 пользователей:**

    ```bash
    flask fetch-people
    ```
6.  **Запуск nginx:**
    
    Скопируйте nginx.conf в директорию, в которой лежит nginx.
    Если у Вас Windows, возможно потребуется отредактировать файл hosts.
    Добавьте туда строчку: `127.0.0.1 homepage`.

    ```bash
    start nginx
    ```
    Для остановки nginx:
    ```bash
    nginx -s quit
    ```

7.  **Запуск приложения:**

    ```bash
    waitress-serve --port=8000 app:app
    ```

### Запуск с Docker Compose

1.  **Настройка переменных окружения:**

    Создайте файл `.env` (или используйте существующий) и настройте переменные окружения, как описано выше.

2.  **Запуск контейнеров:**

    ```bash
    docker-compose up -d --build
    ```

    Это запустит приложение, базу данных PostgreSQL, Nginx и PgAdmin.

    Приложение будет доступно по адресу: `http://homepage`


## Роуты

*   `/`: Главная страница. Отображает список людей с пагинацией. Параметры запроса: `per_page` (количество людей на странице), `page` (номер страницы).
*   `/<int:user_id>`: Страница профиля пользователя. Отображает подробную информацию о пользователе.
*   `/random`: Страница случайного пользователя.  Отображает профиль случайного пользователя из базы данных.
*   `/load_random_people` (POST): Загружает указанное количество случайных пользователей в базу данных.  Параметр запроса: `people_count`.


## API Randomuser.me

Сервис использует публичный API `randomuser.me` для получения данных о людях.  Документация API доступна по ссылке: [https://randomuser.me/documentation](https://randomuser.me/documentation).


## Тестирование

Модульные тесты находятся в директории `tests`.

**Настройка переменных окружения:**

    Создайте файл `.env.testing` в директории tests и настройте следующие переменные:

    ```
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_HOST=your_db_host
    DB_PORT=your_db_port
    DB_NAME=your_test_db_name
    SECRET_KEY=your_secret_key  # Сгенерируйте случайный ключ
    ```

**Запуск тестов:**

```bash
python -m unittest discover tests
```