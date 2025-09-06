
# Theater Service API

This is an API service for managing theater operations, built with **Django** and **Django REST Framework (DRF)**.
It provides functionality for managing plays, actors, genres, theater halls, performances, and ticket reservations.

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

To get the project running on your local machine, you should use Docker.

### Prerequisites

  * Python 3.8+
  * Docker and Docker Compose

### 🐳 Installing with Docker

This is the simplest way to get the project up and running.

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/<your-username>/theatre-service-api.git
    ```
2.  **Go to the project directory:**

    ```bash
    cd theatre-service-api
    ```

3.  **Configure Environment Variables:**
    Rename the sample environment file and then fill in your credentials.

    ```bash
    mv env_sample .env
    ```

    Now, open the `.env` file and set the correct values for your database connection and secret key.

4.  **Run the command to start the project:**
    ```bash
    docker-compose up -build
    ```

5.  **Load initial data (in a new terminal):**

    ```bash
    docker-compose exec theatre python manage.py loaddata theatre_db_data.json
    ```

-----


## 🔑 API Usage

Access to most endpoints requires **JWT authentication**.

The easiest and most convenient way to test and explore the API is by using the interactive **Swagger UI** documentation.
Alternatively, you can use **Postman** or any other HTTP client.

### 🚀 Recommended Method: Swagger UI

After starting the server, navigate to the interactive documentation:

**`http://127.0.0.1:8000/api/doc/swagger/`**

To get started, follow these steps:

#### 1\. Obtain User Credentials

You have two options:

  * **Create a new user:**
    Send a `POST` request to the `/api/user/register/` endpoint with your details.

  * **Use a preloaded user:**
    During migrations and data loading (`loaddata`), test users were created. You can use one of them:

      * **Regular user:**
          * **Email:** `user@user.com`
          * **Password:** `1qazcde3`
      * **Administrator:**
          * **Email:** `admin@admin.com`
          * **Password:** `1qazcde3`

#### 2\. Get an Access Token

In the Swagger UI, find the `POST /api/user/token/` endpoint.
Enter the email and password for the user you chose in the previous step and execute the request. 
In the response, you will receive `access` and `refresh` tokens:

```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Copy the value of the `"access"` key.

#### 3\. Authorize in Swagger

1.  Click the **`Authorize`** button in the top right corner of the Swagger page.
2.  In the modal window that appears, paste your `access` token into the **`Value`** field for the `jwtAuth (http, Bearer)` scheme.
3.  Click **`Authorize`** and close the window.

You are now authenticated and can send requests to protected endpoints.

-----

### 🛠️ Alternative Method: Postman

1.  Obtain an `access` token by sending a `POST` request to `http://127.0.0.1:8000/api/user/token/` with your credentials.
2.  For every request to a protected endpoint, add the following header:
      * **Key:** `Authorization`
      * **Value:** `Bearer <your_access_token>`

-----

Example request using `curl`:

```bash
curl -X GET http://127.0.0.1:8000/api/theatre/plays/ -H "Authorization: Bearer <your_access_token>"
```

-----

### ⚙️ Request Throttling

The API has rate limits to prevent abuse:

  * **Authenticated users:** **100** requests per day.
  * **Unauthenticated users:** **20** requests per day.
