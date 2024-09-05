
# Price API for Shipping Routes

## Overview

The **Price API for Shipping Routes** is a Python-based HTTP API that provides the average daily shipping prices between various ports or geographic regions. It is containerized with **Docker** and interacts with a **PostgreSQL** database. The API delivers responses in **JSON** format and is optimized using raw SQL queries to ensure high performance.

### Key Technologies:
- **Python3.12**: Main language used to build the API.
- **Docker**: Used for containerization and deployment.
- **PostgreSQL**: Manages the shipping data and handles complex queries.

## Features

- Query average prices between specific ports or regions.
- Fetch prices over a date range, with daily averages.
- Returns `null` when data is insufficient for a given day (less than 3 price entries).
- Raw SQL queries optimize the data retrieval process.

## Project Structure

```
project_root/
├── app/
│   ├── main.py                # Application entry point
│   ├── database.py            # Database setup and connection pooling
│   ├── routes.py              # API route definitions
│   ├── utils.py               # Utility functions
│   ├── Dockerfile             # Dockerfile for the API
│   └── tests/                 # Unit and integration tests
│       ├── test_api.py        # API tests
│       ├── test_database.py   # Database tests
│       └── test_utils.py      # Utility tests
├── database/                  
│   ├── Dockerfile             # Dockerfile for PostgreSQL
│   └── rates.sql              # SQL script for initial data setup
├── docker-compose.yml         # Docker Compose setup for API and database
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
```

### Key Files
- **`app/main.py`**: Launches the FastAPI application.
- **`app/database.py`**: Manages the PostgreSQL connection pool and database operations.
- **`app/routes.py`**: Contains API route definition.
- **`app/utils.py`**: Helper functions for validating inputs and formatting data.
- **`app/tests/`**: Unit and integration tests using **pytest**.

## API Endpoints

### `GET /rates`

Retrieve the average daily shipping prices for a specific route between an origin and destination port or region over a defined date range.

#### Query Parameters:
- **`date_from`** (required): The start date in `YYYY-MM-DD` format.
- **`date_to`** (required): The end date in `YYYY-MM-DD` format.
- **`origin`** (required): The origin port code or region.
- **`destination`** (required): The destination port code or region.

#### Example Request:
```bash
curl "http://127.0.0.1:80/rates?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH&destination=north_europe_main"
```

#### Example Response:
```json
[
  {
    "day": "2016-01-01",
    "average_price": 1112
  },
  {
    "day": "2016-01-02",
    "average_price": 1112
  },
  {
    "day": "2016-01-03",
    "average_price": null
  }
]
```
The API returns `null` for days with fewer than 3 price entries.

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/HenrikHub/shipping-rates-api.git
cd shipping-rates-api
```

### 2. Build and Run the Application with Docker Compose

Make sure **Docker** and **Docker Compose** are installed.

```bash
docker-compose up --build
```

This command will:
- Build the API and database containers.
- Set up the PostgreSQL database with initial data from `rates.sql`.
- Start both containers.

### 3. Accessing the API

Once the containers are running, the API can be accessed at:

```
http://127.0.0.1:80/rates
```

To test the API:
```bash
curl "http://127.0.0.1:80/rates?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH&destination=north_europe_main"
```

### 4. Running Tests

To run the tests using **pytest**:
```bash
python -m pytest .\app\tests\
```

These tests include:

- API tests for key /rates).
- Unit tests for the database connection handling (Database class).
- Utility function tests for validation logic.


## Error Handling

- **404 Not Found**: No data found for the specified route and date range.
- **422 Unprocessable Entity**: The request is well-formed, but there are semantic errors (e.g., invalid date format or wrong data type).
- **500 Internal Server Error**: An unexpected error occurred (logged on the server).


## Database Setup

The API uses **PostgreSQL** for data storage. The schema and initial data setup are handled by the `rates.sql` script.


## API Documentation

Once the API is running, interactive documentation is available:

- **Swagger UI**: `http://127.0.0.1:80/docs`
- **ReDoc**: `http://127.0.0.1:80/redoc`

Both provide a user-friendly interface for exploring the API's endpoints, parameters, and responses.
