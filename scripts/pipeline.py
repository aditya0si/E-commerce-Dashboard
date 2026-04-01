from scripts.extract import extract_sales_data
from scripts.config import PROCESSED_DIR
from scripts.load import load_to_postgres
from scripts.transform import transform_sales_data


def run_pipeline() -> None:
    df = extract_sales_data()
    transformed_df = transform_sales_data(df)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    transformed_df.to_csv(PROCESSED_DIR / "sales_clean.csv", index=False)
    load_to_postgres(transformed_df)
    print("Pipeline completed successfully.")


if __name__ == "__main__":
    run_pipeline()
