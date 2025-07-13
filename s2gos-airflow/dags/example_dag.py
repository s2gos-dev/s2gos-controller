from airflow.sdk import DAG, task
#from airflow.providers.standard.operators.python import PythonOperator


def run_python_processor(params):
    print("task params:", params)
    return params


with DAG(
    "s2gos_example_processor",
    catchup=False,
    params={
        "b_param": False,
        "i_param": 0,
        "f_param": 0.0,
        "s_param": "",
        "a_param": [1, 2, 3],
        "o_param": {"a": 0, "b": 1},
    },
    tags=["example"]
) as dag:

    print("dag params:", dag.params)

    @task
    def s2gos_example_processor_task(params):
        print("task params:", params)
        return params
    
    s2gos_example_processor = s2gos_example_processor_task()

    #PythonOperator(
    #    task_id="s2gos_example_processor_task", 
    #    python_callable=run_python_processor
    #)
