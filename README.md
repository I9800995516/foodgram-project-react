=======
# praktikum_new_diplom

Этап 1

В папке infra для локального развертывания Docker создан:
docker-compose.yml

Развернуть проект локально:

cd backend/
docker build -t fg _backend .

cd frontend/
docker build -t fg_frontend .

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

