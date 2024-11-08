# Test_Task_Django 
Тестовое задание на обработку файла и вывода отчета на страницу.
Краткое описание вашего проекта.

## Требования
Список необходимых зависимостей и инструментов для запуска проекта.

- Python 3.x 
- Docker

### Клонирование репозитория и запуск проекта
Откройте терминал и склонируйте репозиторий на свой компьютер:

    git clone https://github.com/repka98/Test_Task_Django.git

    cd Test_Task_Django/app


Далее находясь в этой директории необходимо вызвать команду Docker:

    docker-compose build
Этой командой собирается контейнер.
Теперь запустим контейнер.

    docker-compose up

Откроем новый терминал.
Когда завершиться сборка приложения необходимо создать супер пользователя:

    docker-compose run --rm web-app sh -c "./manage.py creratesuperuser"  

Задать имя и пароль пользователя.

Следующий шаг, провести миграции БД командой:

    docker-compose run --rm web-app sh -c "./manage.py makemigrations"
    docker-compose run --rm web-app sh -c "./manage.py migreate"

После этого перезапустить контейнер нажав в терминале Сtrl+C.
Ввести снова команду:
    
    docker-compose up

Наше приложение запустилось.

### Работа с приложением

1. После того как запустили приложение необходимо открыть браузер и ввести адрес в 
адресную строку [127.0.0.1:8000/](http://127.0.0.1:8000/).

2. Далее необходимо нажать на кнопку "Начать работу".

3. Выполниться переход на следующую страницу приложения, Где так же необходимо
нажать на кнопку "Загрузка файла данных".

4. Следующая страница дает нам возможность загрузить файл с данными и расширение .xlsx, 
для этого необходимо ввести заголовок файла и загрузить сам файл.
После этого нажать кнопку "Загрузить файл". 

5. После нажатия на кнопку приложение перейдет на следующую страницу, 
где получим предложение записать данные в базу данных. Нажмем на кнопку "Записать данные в базу".

6. Придется немного подождать пока файл данных (видимо не маленький) обработается и 
запишется в базу данных.

7. После записи данных приложение автоматически откроет страницу с отчетами по загруженным данным.
8. Необходимо выбрать интересующий Вас период использую поля-календари.
9. После этого нажать кнопку "Сформировать отчет".
10. Если какую-то из дат Вы не ввели, сверху страницы отобразиться статус "Вы не заполнили все даты".
Если все заполнили, то увидите статус "Даты заполнены".
11. И В таблице отобразиться отчет за выбранный период.

Спасибо и продолжайте пользоваться нашими приложениями.
@korip



