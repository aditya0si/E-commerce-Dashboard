# E-commerce Data Analytics Pipeline

This project is a starter structure for an analytics pipeline built with Python, PostgreSQL, and Streamlit.

## Project Structure

```text
.
|-- data/
|   |-- external/
|   |-- processed/
|   `-- raw/
|-- dashboard/
|   |-- pages/
|   `-- app.py
|-- notebooks/
|-- scripts/
|   |-- __init__.py
|   |-- config.py
|   |-- extract.py
|   |-- load.py
|   |-- pipeline.py
|   `-- transform.py
|-- sql/
|   |-- analytics_views.sql
|   |-- schema.sql
|   `-- seed_queries.sql
|-- .env.example
|-- requirements.txt
`-- README.md
```

## Stack

- Python with `pandas` for extraction and transformation
- PostgreSQL for storage and analytics-ready tables/views
- Streamlit for dashboarding

## Setup

1. Create a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and update your PostgreSQL credentials.
4. Create the database and run the SQL in `sql/schema.sql`.
5. Place source files in `data/raw/`.
6. Run the pipeline:

   ```bash
   python -m scripts.pipeline
   ```

7. Start the dashboard:

   ```bash
   streamlit run dashboard/app.py
   ```

## Notes

- `data/raw/` holds original source files.
- `data/processed/` holds cleaned or transformed exports.
- `data/external/` is for third-party datasets.
- `scripts/` contains pipeline logic.
- `sql/` contains schema and analytics SQL.
- `dashboard/` contains the Streamlit app.
- `notebooks/` is for exploration and prototyping.
