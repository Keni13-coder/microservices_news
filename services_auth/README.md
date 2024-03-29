# Асинхронный блог на FastAPI + Postgresql + Celery + Redis + RabbitMQ + Flower.

Этот проект был сделан в качесте ознакомлением с популярными инструментами. Для начала рассмотрим используемый стэк в приложения.

* FastAPI
* Postgresql
* Redis
* Celery
* RabbitMQ
* Flower
* PyTest
* Docker

# Работа с приложением.

## Подготовка к обычному запуску приложения.

Для начала клонируем весь репозиторий. 

`git clone https://github.com/Keni13-coder/Projects.git`

Перейдите в News_Fastapi. 

`cd ./Projects/News_Fastapi`

Создайте виртуального среду. 

`python -m venv venv` 

Перейдите в виртуальную среду. 

`venv\Scripts\activate.ps1` 

Установите зависимости. 

`pip install -r requirements.txt` 

Для дальнейшей подготовки перейдите в корневую рабочий каталог "my_blog". 

`cd my_blog` 

Создайте файл .env в подкаталоге __core__. Определите следующие переменные: 

* MY_MAIL_USERNAME = ваш email (используется в качестве имени) 
* MY_MAIL_PASSWORD = STMP пароль (посмотрите, как получить дынный пароль для внешнего подключения) 
* MY_MAIL_FROM = ваш email
* DB_HOST=localhost
* DB_PORT=5432
* DB_NAME= имя базы данных для работы (должна уже быть создана)  
* DB_USER=postgres 
* DB_PASS= ваш пароль 
* SECRET_KEY= сгенерируйте для большей безопасности (секретная строка) 
* LOG_LEVEL=info 
* LOG_FORMAT=JSON 
* LOG_DIR=./logs/ 
* LOG_FILENAME=app.log
  
Должны быть заранее запущен 

* REDIS_HOST=localhost 
* REDIS_PORT=6379 

 Должны быть заранее запущен 

* RABBITMQ_DEFAULT_USER= ваше имя 

* RABBITMQ_DEFAULT_PASS= ваш пароль 

* RABBITMQ_NODE_PORT=5672 

* RABBITMQ_DEFAULT_VHOST=/ 

* HOST_NAME_RABBIT=localhost 

* MODE=DEV 

* MEDIA=./media 

Совершенно не важно, как вы запустили Redis и RabbitMQ, главное это соответствие необходимого для подключения переменных с данными. 

Для выполнения команд перейдите в рабочую директорию my_blog. 

Команды: 

1. `alembic upgrade head` - создаёт таблицы обновляя их до последней версии миграций 

2. `celery -A background_celery.app_celery:celery worker --loglevel=INFO --logfile=./logs/celery.log` - запуск celery в режиме worker с логированием 

3. `celery -A background_celery.app_celery:celery flower` - запуск flower порт по умолчанию "5555" 

4. `uvicorn run:app` - обычный запуск приложения 

Если есть желание поиграться с отладчиком перейдите в файл run, находящийся в корневой директории. Чтобы включить режим отладки (debug) передайте в функцию create_app(True). 

`uvicorn run:app --reload` - для удобства добавляем перезагрузку 

### Запуск приложения через контейнер Docker. 

Для начала клонируем весь репозиторий. 

`git clone https://github.com/Keni13-coder/Projects.git`

Перейдите в корнивую рабочию директорию проекта 

`cd ./Projects/News_Fastapi/my_blog` 

Создайте файл .env-non-dev в подкаталоге __core__. Определите следующие переменные: 

* MY_MAIL_USERNAME = ваш email (используется в качестве имени) 

* MY_MAIL_PASSWORD = STMP пароль (посмотрите как получить дынный пароль для внешнего подключения) 

* MY_MAIL_FROM = ваш email 

 

* DB_HOST=db 

* DB_PORT=1212 

* DB_NAME=имя базы данных которая будет создана 

* DB_USER= имя пользователя 

* DB_PASS= пароль пользователя 

 

Для подключения используйте созданные вами данные 

* POSTGRES_DB= DB_NAME 

* POSTGRES_USER= DB_USER 

* POSTGRES_PASSWORD= DB_PASS 


* SECRET_KEY= сгенерируйте для большей безопасности (секретная строка) 


* LOG_LEVEL=info 

* LOG_FORMAT=JSON 

* LOG_DIR=./logs/ 

* LOG_FILENAME=app.log 


* REDIS_HOST=redis 

* REDIS_PORT=6374 



* RABBITMQ_DEFAULT_USER= ваше имя 

* RABBITMQ_DEFAULT_PASS= ваш пароль 

* RABBITMQ_NODE_PORT=5673 

* RABBITMQ_DEFAULT_VHOST=/ 

* HOST_NAME_RABBIT=rabbitmq 

* MODE=START 

* MEDIA=./media 

Перед запуском контейнера обратите внимание на файл docker-compose.yml находящийся в корневой папке приложения. В нем вы можете настроить порты если возникнут перекрытие. Так же не забывайте при изменении в данной файле поменять их в .env-non-dev 

### Поднимаем контейнер. 

Создание и поднятие контейнера docker: 

`docker-compose up --build`

### Как устроена работа приложения. 

Проект построен на принципе Union Architecture и имеет следующие слои: 

1. Entity data base 

2. Repository 

3. Unit of Work 

4. Services 

5. EndPoint 

Где номер один является центром, а номер пять началом. Так же можно выделить отдельно созданные удобства, что не входят в слои, но на прямую работает из сервисов. Это задачи celery, для задач были создание отдельные настройки и классы задач. 

В каталоге __background_celery__ возможна тщательно изучения при возникновении вопросов. 

1. Entity data base обусловлена представлением работы с базой данных. Там будут описаны основные методы взаимодействий, наследуется от абстрактного класса 

2. Repository, выходит из определения обращений к базе данных наследую класс взаимодействия с базой данных. Так же на этом слое присутствует реализация кеширования самых частых запросов. Кеш храниться в оперативной памяти, для работы с ним выбран Redis. Работает в асинхронном формате. Для правильной работы приложения была переписана настройка для кодирования и декодирования. 

В каталоге __db__/__utils__, найдите файл __cache_builder.py__. В данном файле будут надстройки касаемые кеширования. 

3. Unit of Work, отвечает за создание сессии, взаимодействия с репозиториями. Так же управляет транзакцией, а если быть точнее запрос будет удачным если все входящие запросы в транзакции не вызовет ошибок. В случае ошибки производиться rollback. Реализовано через контекст менеджера 

В каталоге __db__/__utils__, найдите файл __uow_class.py__. В данном файле реализован класс, отвечающий за данную логику. 

4. Services, основная логика по обработке данных от клиента и подготовке к работе с базой данных. Для сервисов были созданы классы Worker. Данные классы являются помощниками, разделенными по логике взаимодействия. Например, __HashePasswordWorker__ будут описаны методы исключительно для всевозможной работы с паролем. Так же сервисы запускают задачи celery. 

5. EndPoint, построенные http запросы по маршрутам. Для создание конечных точек используется FastAPI. Так же стоит обратить внимания на зависимости, переданные в данные точки. В конечных точках определяются cookie, которые помогают в дальнейшем взаимодействие с приложением. 

Все маршруты, прописанные для приложения распределены по их ролям, для просмотра перейдите в каталоге __apps__. 
