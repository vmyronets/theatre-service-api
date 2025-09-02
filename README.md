
# Theater Service API

This is an API service for managing theater operations, built with **Django** and **Django REST Framework (DRF)**.
It provides functionality for managing plays, actors, genres, theatre halls, performances, and ticket reservations.

-----

## ✨ Features

  * **JWT Authentication**: Secure API access using JSON Web Tokens.
  * **Admin Panel**: A full-featured Django admin panel to manage all system entities.
  * **API Documentation**: Interactive Swagger UI documentation for exploring and testing endpoints.
  * **Reservation and Ticket Management**: Create, view, and manage orders and tickets.
  * **Content Creation**: Ability to add plays, genres, and actors.
  * **Hall and Performance Management**: Create theater halls and schedule performances for plays.
  * **Filtering**: Flexible options to filter plays and performances by various criteria.

-----

## 🚀 Getting Started

To get the project running on your local machine, you can either use Docker (recommended) or set up the environment manually.

### Prerequisites

  * Python 3.8+
  * PostgreSQL
  * Docker and Docker Compose (for the Docker-based setup)

### 🐳 Installing with Docker (Recommended)

This is the simplest way to get the project up and running.

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/<your-username>/theatre-service-api.git
    cd theatre-service-api
    ```

2.  **Build and run the containers:**

    ```bash
    docker-compose build
    docker-compose up
    ```

    The service will be available at `http://localhost:8000`.

3.  **Apply migrations and load initial data (in a new terminal):**

    ```bash
    docker-compose exec theatre python manage.py migrate
    docker-compose exec theatre python manage.py loaddata theatre_db_data.json
    ```

### 💻 Manual Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/<your-username>/theatre-service-api.git
    cd theatre-service-api
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use: venv\Scripts\activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Rename the sample environment file and then fill in your credentials.

    ```bash
    mv env_sample .env
    ```

    Now, open the `.env` file and set the correct values for your database connection and secret key.

5.  **Apply migrations and load initial data:**

    ```bash
    python manage.py migrate
    python manage.py loaddata theatre_db_data.json
    ```

6.  **Run the development server:**

    ```bash
    python manage.py runserver
    ```

-----

## 🔑 API Usage

Access to most endpoints requires JWT authentication.
To send a request with an access token in the header, you can use Postman or use the following commands:

### 1\. Register a New User

Create a new user by sending a `POST` request to `api/user/register/`.

```bash
curl -X POST http://localhost:8000/api/user/register/ \
-H "Content-Type: application/json" \
-d '{
    "email": "user@example.com",
    "password": "YourStrongPassword123"
}'
```

### 2\. Obtain a Token

After registration, get your `access` and `refresh` tokens by sending your credentials to `api/user/token/`.

```bash
curl -X POST http://localhost:8000/api/user/token/ \
-H "Content-Type: application/json" \
-d '{
    "email": "user@example.com",
    "password": "YourStrongPassword123"
}'
```

In response, you will receive:

```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 3\. Accessing Protected Routes

Use the received `access` token by passing it in the `Authorization` header of every request.

```bash
curl -X GET http://localhost:8000/api/theatre/plays/ \
-H "Authorization: Bearer <your_access_token>"
```

-----

## 📚 API Documentation

Complete and interactive API documentation (Swagger UI) is available after starting the server at:

**`http://localhost:8000/api/doc/swagger/`**

## 👤 Admin Panel

To access the admin panel, navigate to **`/admin/`**. You can use the superuser credentials loaded from the initial data file:

  * **Email:** `admin@admin.com`
  * **Password:** `1qazcde3`
