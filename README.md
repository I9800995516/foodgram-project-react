# Проект "Продуктовый помощник"
[![API for Foodgram project workflow](https://github.com/i9800995516/foodgram-project-react/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/i9800995516/foodgram-project-react/actions/workflows/main.yml)

### Адресa:
Проект доступен по адресу: http://158.160.17.34/  
Админ панель Django: http://158.160.17.34/admin/  
Документация ReDoc: http://158.160.17.34/api/docs/

Логин в админ панель: I9800995516@yandex.ru
Пароль: Practicum77

## Описание

Проект «Продуктовый помощник». Онлайн-сервис и API для него. Пользователи публикуют рецепты, 
подписываться на публикации других пользователей, добавляют рецепты в список «Избранное», 
скачивают сводный список продуктов, необходимых для приготовления одного 
или нескольких выбранных блюд.  
  
Проект разворачивается в Docker контейнерах (nginx, PostgreSQL и Django) 
(контейнер frontend используется  для подготовки файлов)  на сервере в Яндекс.Облаке.

## Стек технологий

![Static Badge](https://img.shields.io/badge/Python-3.8-yellowred)
![Static Badge](https://img.shields.io/badge/Django-3.2-yellowred)
![Static Badge](https://img.shields.io/badge/PostgreSQL-yellowred)
![Static Badge](https://img.shields.io/badge/Nginx-yellowred)
![Static Badge](https://img.shields.io/badge/gunicorn-yellowred)
![Static Badge](https://img.shields.io/badge/Docker-yellowred)
![Static Badge](https://img.shields.io/badge/GitHubActions-yellowred)

## Развертывание

Перед сборкой контейнеров в папке frontend после локального тестирования необходимо изменить package.json строку 41 на:
"proxy": "http://web:8000/"


В папке infra для развертывания в облаке в контейнерах Docker создан:
docker-compose.yml

Развернуть проект локально:

```shell
cd backend/
docker build -t fооdgram_backend .

cd frontend/
docker build -t fооdgram_frontend .

cd infra/
docker-compose up -d --build


После успешного запуска контейнеров выполнить миграции, собрать статику, напонить бд и создать суперюзера:
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --noinput
docker-compose exec backend python manage.py importcsv
docker-compose exec backend python manage.py createsuperuser


## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/i9800995516/foodgram-project-react.git
cd foodgram-project-react/
cd infra/
```

В директории `infra/` создать файл `.env`:

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```


## Запустить приложение в контейнерах:

*из директории `infra/`*
```
docker-compose up -d --build
```

Выполнить миграции:

*из директории `infra/`*
```
docker-compose exec backend python manage.py migrate
```

Создать суперпользователя:

*из директории `infra/`*
```
docker-compose exec backend python manage.py createsuperuser
```

Собрать статику:

*из директории `infra/`*
```
docker-compose exec backend python manage.py collectstatic --no-input
```

## Заполнить БД тестовыми данными

Для заполнения базы использовать файл `ingredietns.csv`, в директории `/data`. Выполните команду:

*из директории `infra/`*
```
docker-compose exec backend python manage.py load_ingredients
```

## Автор

Штанова Маргарита
