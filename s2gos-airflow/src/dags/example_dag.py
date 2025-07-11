from datetime import datetime, timedelta

from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG


def hello():
    print("Hello from Airflow!")

with DAG(
    "S2GOS-Example-DAG",
    start_date=datetime(2025, 1, 1),
    schedule=timedelta(days=1),
    catchup=False,
    tags=["example"]
) as dag:
    task = PythonOperator(
        task_id="say_hello",
        python_callable=hello
    )
