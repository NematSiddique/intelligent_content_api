# The Intelligent Content API

A RESTful API service that allows users to upload text content. The system automatically processes the text using an AI model to generate a summary and sentiment analysis, then stores the results in a database.

---

## Table of Contents

## **Features:**
1. **User Authentication**
   - JWT-based authentication.
   - **POST /signup** – Register a new user.
   - **POST /login** – Authenticate and return an access token.

2. **Content Management & AI Processing**
   - **POST /contents** – Upload a text, process it with AI, and store summary & sentiment.
   - **GET /contents** – Retrieve all content for the authenticated user.
   - **GET /contents/{id}** – Retrieve a specific content entry with summary & sentiment.
   - **DELETE /contents/{id}** – Delete a specific content entry.
   - Asynchronous AI calls to prevent blocking the main thread.

3. **Logging**
   - Terminal logs for debugging and monitoring requests.
   
---

## **Tech Stack:**

- **Language:** Python 3.9+
- **Framework:** FastAPI
- **Database:** PostgreSQL (user data), SQLAlchemy ORM
- **Caching:** Redis
- **AI Integration:** OpenAI GPT-3.5 / Gemini API
- **Infrastructure:** Docker
- **Authentication:** JWT (PyJWT & python-jose)
- **Environment Management:** python-dotenv

---

## Setup Instructions

### Prerequisites

- Python 3.9+
- PostgreSQL installed locally or via Docker
- Docker (optional, for containerized setup)
- An API key for OpenAI or Gemini

### Local Setup

1. Clone the repository and navigate into the project directory:
   ```bash
   git clone https://github.com/NematSiddique/intelligent_content_api.git
   cd intelligent_content_api
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a **`.env`** file in the project root and populate it with your configuration:
   ```env
   DATABASE_URL=postgresql://<username>:<password>@localhost:5432/<dbname>
   JWT_SECRET=<your_jwt_secret>
   JWT_ALGO=HS256
   JWT_EXP_MINUTES=60
   OPENAI_API_KEY=<your_openai_api_key>
   GEMINI_API_KEY=<your_gemini_api_key>
   DATABASE_URL=<your_postgres_url>
   REDIS_HOST=redis
   REDIS_PORT=6379
   REDIS_PASSWORD=<your password>
   REDIS_CACHE_TTL=600
   ```

5. Run database migrations (or create tables manually) to set up the **Users** and **Contents** tables.

6. Start the FastAPI server (often using uvicorn):
   ```bash
   uvicorn app.main:app --reload
   ```

7. Access the **Swagger UI** for testing at: **http://127.0.0.1:8000/docs**


## Docker Setup

A simple, working `docker-compose.yml` is used so everything runs with one command.

### docker-compose.yml

```yaml
version: '3.9'

services:

  # PostgreSQL
  postgres-intelligent:
    image: postgres:18
    container_name: postgres_intelligent
    ports:
      - "5432:5432"
    environment:
      POSTGRES_PASSWORD: admin
      POSTGRES_USER: admin
      POSTGRES_DB: boot
    volumes:
      - postgres_data:/var/lib/postgresql
    networks:
      - contentdb_network

  # Adminer
  adminer:
    image: adminer
    container_name: contentdb_adminer
    restart: always
    ports:
      - "8080:8080"
    networks:
      - contentdb_network

  # Redis
  redis:
    image: redis:7
    container_name: intelligent_redis
    restart: always
    ports:
      - "6379:6379"
    command: ["redis-server", "--appendonly", "yes", "--requirepass", "${REDIS_PASSWORD}"]
    environment:
      - REDIS_PASSWORD=${REDIS_PASSWORD}
    networks:
      - contentdb_network

  # FastAPI
  fastapi-app:
    build: .
    container_name: fastapi_app
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://admin:admin@postgres-intelligent:5432/boot
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
    depends_on:
      - postgres-intelligent
      - redis
    networks:
      - contentdb_network
    volumes:
      - ./app:/app/app

# Networks
networks:
  contentdb_network:

# Volumes
volumes:
  postgres_data:

```

### Run Everything

To start the application and database, run:

```bash
docker compose up --build
```

The API will be available at:

[http://localhost:8000](http://localhost:8000)

---

## API Documentation
| Method     | Endpoint          | Description                          | Body Example                                               |
| ---------- | ----------------- | ------------------------------------ | ---------------------------------------------------------- |
| **POST**   | users/signup      | Register a new user                  | `{ "email": "user@example.com", "password": "Abcd@1234" }` |
| **POST**   | users/login      | Authenticate and return JWT token    | `{ "email": "user@example.com", "password": "Abcd@1234" }` |
| **POST**   | /contents         | Upload text, analyze, and save in DB | `{ "text": "Your text here" }`                             |
| **GET**    | /contents         | Retrieve all content for the user    | `No body required`                                         |
| **GET**    | /contents/{id}    | Retrieve content by ID               | `No body required`                                         |
| **DELETE** | /contents/{id}    | Delete content by ID                 | `No body required`                                         |

---

## Database Design

### Users Table:
- `id` – Primary Key
- `email` – Unique
- `password` – Hashed password
- `created_at` – Timestamp
### Contents Table:
- `id` – Primary Key
- `user_id` – Foreign Key to Users
- `text` – Original text
- `summary` – AI-generated summary
- `sentiment` – Positive/Negative/Neutral
- `created_at` – Timestamp

## AI Integration

* AI API calls are asynchronous using httpx.AsyncClient.
* Supports Gemini API for text summarization and sentiment analysis.
* Response stored in summary and sentiment fields in the database.

**Example AI Output:**
   ```json
   {
       "summary": "This article explains FastAPI basics and content API features.",
       "sentiment": "Positive"
   }
   
   ```

---

## GCP Deployment Architecture (Theoretical)
    +-------------------+
    |   Cloud Load       |
    |   Balancer/API     |
    +---------+---------+
              |
    +---------v---------+
    |   Cloud Run        | -> Runs FastAPI container
    +---------+---------+
              |
    +---------v---------+
    |   Cloud SQL        | -> PostgreSQL for users & content
    +-------------------+
- API Gateway / Load Balancer: Route requests to Cloud Run
- Cloud Run: Containerized FastAPI service
- Cloud SQL: Managed PostgreSQL database
- Secrets: Store API keys and JWT secrets in Secret Manager

## Bonus Features
* Logging: Terminal logging for requests, errors, and AI responses.
* Error Handling: Graceful handling if AI API fails or times out.
* Regex Password Validation: Strong password enforcement on signup.
* Redis caching for getting user contents.

## Swagger Usage (Documentation & Testing)

Access the interactive docs at:
http://127.0.0.1:8000/docs

How to test endpoints
- Open the docs page and find the endpoint you want to test.
- Click "Try it out".
- Enter the request body (JSON) or parameters and click "Execute".
- Inspect the request/response panels for status, body, and example schemas.

Using JWT for protected routes
1. Obtain a token
   - Call POST /users/login with JSON body, e.g.:
   ```json
   {
     "email": "user@example.com",
     "password": "Abcd@1234"
   }
   ```
   - Successful response:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6..."
   }
   ```

2. Add token to Swagger
   - Click the "Authorize" button (top right of the docs page).
   - Enter the value: Bearer <your_token_here>
   - Click "Authorize" then "Close".

3. Call protected endpoints
   - After authorizing, Swagger will include the Authorization header for secured endpoints.
   - Example curl:
   ```bash
   curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6..." \
     http://127.0.0.1:8000/contents
   ```

Notes
- Include the "Bearer " prefix when pasting the token.
- Tokens may expire based on JWT_EXP_MINUTES; re-authenticate if requests return 401.
- For debugging, check the request/response panels in the Swagger UI for headers and error messages.

## Git Repo Structure

```
intelligent-content-api/
├─ app/
│  ├─ main.py                 # Main FastAPI application and startup logic
│  ├─ logging_config.py       # Configuration for structured logging
│  ├─ config.py               # Configuration settings loaded from .env
│  ├─ routes/
│  |  ├─ contents.py          # Endpoints related to content (POST, GET, DELETE)
│  |  └─ users.py             # Endpoints related to user authentication (signup, signin)
│  ├─ service/
│  |  ├─ analyze_sentiment.py # Logic for calling the AI API (Gemini/OpenAI)
│  |  └─ auth_service.py      # Business logic for hashing, JWT creation, and validation
│  ├─ caching/
│  |  ├─ redis.py             # Redis connection for caching
│  ├─ database/
│  |  ├─ databse.py           # Database connection and session management
│  |  ├─ models.py            # SQLAlchemy ORM models (Users, Contents)
│  |  └─ schemas.py           # Pydantic models for request/response validation
│  ├─ middleware/
│  |  └─ jwt_middleware.py    # Custom middleware for JWT authentication checks
│  └─ tests/
│      └─ test_conn.py        # Basic test for database/API connectivity
├─ .env                       # Environment configuration file
├─ requirements.txt           # Python dependency list
├─ docker-compose.yml         # Docker image definition
└─ README.md                  # Project documentation (this file)
```
