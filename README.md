# FastAPI Receipt Printer Service

This project is a service built with FastAPI that receives order data 
(items, quantities, and prices) and generates receipts (also formatted).


## Tech Stack
- `Python 3.10+`
- `FastAPI` – modern web framework for APIs.
- `SQLAlchemy` – ORM for database interaction.
- `PostgreSQL` – supported database engines.
- `Pydantic` – data validation and parsing.

## Getting Started
#### 1. Clone the repository
```
git clone https://github.com/.../fastapi-checks-api.git
cd fastapi-checks-api
```

#### 2. Create and activate a virtual environment
```
python -m venv venv

source venv/bin/activate  # for Linux/macOS
venv\Scripts\activate     # for Windows
```

#### 3. Install dependencies
```
pip install -r requirements.txt
```

#### 4. Set up environment variables (.env file)
```
SECRET_KEY=secret_key_example
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db_name
SQLALCHELMY_ECHO=False
```

#### 6. Start the development server
```
uvicorn app.main:app --reload
```
