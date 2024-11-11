Backend - FastApi + (Celery, Redis, Postgresql)

# Инструкция по запуску

Установите python, pip
Установите и запустите redis и postgresql на локальном компьютере

Конфигурационные настройки в .env и config.py

# Создайте окружение

python3.11 -m venv venv

# Активируйте окружение и Установите необходимые библиотеки

pip3 install -r reuirements.txt


# Проведите миграции

alembic --name=forms revision --autogenerate -m 'initial migration' &&
alembic --name=forms upgrade head &&


# Запустите все программы

FastApi:

    python3 main.py

Celery (Worker):

    celery -A fastapp.tasks.celery_tasks worker -l info

Celery (Beat):

    celery -A fastapp.tasks.celery_tasks beat -l info

Celery (Flower):

    celery -A fastapp.tasks.celery_tasks flower -l info
