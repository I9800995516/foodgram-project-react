=======
# praktikum_new_diplom

Этап 1

Тестирование произведено локально в базе mySQL
фронт запускался на localhost:3000
бэкэнд на localhost:8000

в папке frontend для локального тестирования необходимо изменить package.json строку 41 на:
"proxy": "http://localhost:8000/"

установить node.js
далее зависимости npm -i  (не обращая внимание на ошибки, зависимости установятся корректно только, если указано в package.json
    "react": "^16.6.0",
    "react-dom": "^16.6.0",)

старт фронтэнда командой npm run start

При тестировании на Docker

в папке 'infra' создать .env

в settings.py переключить значение DATABASES на postgres

В папке infra для локального развертывания Docker создан:
docker-compose.yml

Развернуть проект локально:

cd backend/
docker build -t fооdgram _backend .

cd frontend/
docker build -t fооdgram_frontend .

cd infra/
docker-compose up -d --build

После успешного запуска контейнеров выполнить миграции, собрать статику, напонить бд и создать суперюзера:
```
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --noinput
docker-compose exec backend python manage.py importcsv
docker-compose exec backend python manage.py createsuperuser
```


## Автор

