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


