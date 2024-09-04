# Price API for Shipping Routes

## Overview

This project is an HTTP-based API that returns the average daily shipping prices between ports or geographic regions. The API is built using Python and SQL, and all data is returned in JSON format.

## Features

- Supports querying prices between specific ports or entire regions.
- Provides average prices for each day between a given date range.
- Handles errors and edge cases such as insufficient data for a day (returns `null` for days with less than 3 price entries).
- Uses raw SQL queries for fetching and manipulating data.

## Project Structure

```
project_root/
├── app/
│   ├── main.py                # Entry point for running the application
│   ├── database.py            # Handles database setup and configuration
│   ├── routes.py              # Contains the API endpoints
│   ├── utils.py               # Utility functions shared across the project
│   ├── Dockerfile             # Docker configuration file
│   └── tests/                 # Unit and integration test files
│       ├── test_api.py        # Tests for API functionality
│       ├── test_database.py   # Tests for database operations
│       └── test_utils.py      # Tests for utility functions
├── database/                  # Database schema for creating tables
│   ├── Dockerfile             # Docker configuration file
│   └── rates.sql              # SQL script for creating tables
├── requirements.txt           # List of dependencies to be installed
├── README.md                  # Project documentation
├── .env                       # Environment variables for local development
└── .gitignore                 # Specifies files to ignore in version control
```

### Key Files

- **`app/main.py`**: The main entry point for running the Flask application. This file sets up the Flask server and handles the app's lifecycle.
- **`app/database.py`**: Contains the logic for database setup and connection management. This file initializes the database and provides the class to interact with the database.
- **`app/roots.py`**: Defines the API endpoints, including the logic for fetching and returning the required data.
- **`app/utils.py`**: Includes general helper functions that are used throughout the application. This can include utility functions for date validation, data formatting, etc.
- **`app/tests/`**: Contains unit and integration tests for different parts of the application. Files are organized based on what they are testing: API, database, or utilities.

## API Endpoints

### `GET /rates`

Fetches the average prices per day for the route between the origin and destination ports or regions for the given date range.

#### Parameters:
- `date_from` (required): Start date in `YYYY-MM-DD` format.
- `date_to` (required): End date in `YYYY-MM-DD` format.
- `origin` (required): Origin port code or region slug.
- `destination` (required): Destination port code or region slug.

#### Example Request:

```bash
curl "http://127.0.0.1:5000/rates?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH&destination=north_europe_main"
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

For days with fewer than 3 prices, the API returns `null` for the `average_price`.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository_url>
cd <repository_name>
```

### 2. Set Up the Virtual Environment

Set up a Python virtual environment to manage dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Dependencies

Install the necessary packages from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 4. Set Up the Database

- Create a new SQL database (PostgreSQL or SQLite).
- Apply the database schema provided in `schema.sql` to create the required tables.
- Import the data provided in the database dump file.

```bash
psql -U username -d database_name -f schema.sql  # For PostgreSQL
```

### 5. Configure Environment Variables

Set up the following environment variables in a `.env` file or export them in your shell:

- `DATABASE_URL`: Connection string to your SQL database (e.g., `postgresql://user:password@localhost:5432/dbname`).

Example `.env` file:

```
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### 6. Run the Application

Start the Flask application:

```bash
flask run
```

The API will be accessible at `http://127.0.0.1:5000`.

### 7. Run Tests

To run the provided unit tests:

```bash
python -m unittest discover app/tests/
```

## SQL Example Queries

Below are examples of raw SQL queries used in the project:

1. Fetching average price for a specific day between two ports:

```sql
SELECT price_date, AVG(price) AS average_price
FROM prices
WHERE origin_port = 'CNSGH' AND destination_port = 'north_europe_main'
AND price_date BETWEEN '2016-01-01' AND '2016-01-10'
GROUP BY price_date
HAVING COUNT(price) >= 3;
```

2. Handling regions:

You would also need to join ports and regions for queries that involve region slugs. Here's an example:

```sql
WITH recursive region_ports AS (
    SELECT port_code, region_slug FROM ports WHERE region_slug = 'north_europe_main'
    UNION
    SELECT p.port_code, r.slug FROM regions r
    JOIN ports p ON r.slug = p.region_slug
    WHERE r.parent_slug = 'north_europe_main'
)
SELECT price_date, AVG(price) AS average_price
FROM prices
WHERE origin_port IN (SELECT port_code FROM region_ports)
AND destination_port = 'CNSGH'
AND price_date BETWEEN '2016-01-01' AND '2016-01-10'
GROUP BY price_date
HAVING COUNT(price) >= 3;
```

## Error Handling

- **400 Bad Request**: Returned if required parameters are missing or invalid.
- **404 Not Found**: Returned if no data is found for the given parameters.
- **500 Internal Server Error**: For unexpected errors, the API will return a generic 500 response, and log the error for debugging.



