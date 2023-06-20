<<<<<<< HEAD
## Этап 1

In the `infra` folder, the following files were created for local Docker deployment:
- `docker-compose.yml`

To deploy the project locally, follow these steps:

1. Navigate to the `backend/` directory:


2. Build the backend Docker image:

docker build -t food


3. Navigate to the `frontend/` directory:

cd frontend/


4. Build the frontend Docker image:

docker build -t foodgram_frontend .


5. Navigate to the `infra/` directory:


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

Штанова Маргарита 
Python-разработчик (Backend)
E-mail: i9800995516@yandex.ru
>>>>>>> master
