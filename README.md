# Test_Task_Django 
Тестовое задание на обработку файла и вывода отчета на страницу.
Краткое описание вашего проекта.

## Требования
Список необходимых зависимостей и инструментов для запуска проекта.

- Python 3.x 
- Docker

### Клонирование репозитория
Склонируйте репозиторий на свой компьютер:

'''git clone https://github.com/repka98/Test_Task_Django.git'''

cd название_проекта
Создание виртуального окружения (опционально)
Рекомендуется создать виртуальное окружение для изоляции зависимостей проекта:


python3 -m venv venv
source venv/bin/activate
Установка зависимостей
Установите зависимости, указанные в файле requirements.txt:


pip install -r requirements.txt
Настройка базы данных
Настройте базу данных согласно вашим предпочтениям. Пример для PostgreSQL:


CREATE DATABASE your_db_name;
CREATE USER your_username WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE your_db_name TO your_username;
Миграции и создание суперюзера
Выполните миграции и создайте суперпользователя:


python manage.py migrate
python manage.py createsuperuser
Запуск сервера разработки
Запустите сервер разработки:


python manage.py runserver
Откройте браузер и перейдите по адресу http://127.0.0.1:8000/, чтобы увидеть ваше приложение.

Развертывание на production-сервере
Инструкция по развертыванию проекта на production-серверах, например, с использованием Docker, Nginx, uWSGI и т.п.