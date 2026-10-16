"""Run with python -m examples.guides.api against the local test service."""

# --8<-- [start:imports]
from gavicore.models import JobResults, JobStatus, ProcessRequest

from s2gos_client import Client, create_client

# --8<-- [end:imports]


# --8<-- [start:connect]
def connect() -> Client:
    return create_client(api_url="http://127.0.0.1:8008", auth={"auth_type": "none"})


# --8<-- [end:connect]


# --8<-- [start:inspect]
def inspect_process(client: Client, process_id: str) -> None:
    print(client.get_processes().model_dump_json(indent=2))
    print(client.get_process(process_id).model_dump_json(indent=2))


# --8<-- [end:inspect]


# --8<-- [start:submit]
def submit(client: Client, process_id: str, request: ProcessRequest) -> str:
    job = client.execute_process(process_id, request=request)
    print(job.model_dump_json(indent=2))
    return job.jobID


# --8<-- [end:submit]


# --8<-- [start:results]
def inspect_results(client: Client, job_id: str) -> JobResults | None:
    job = client.get_job(job_id)
    print(job.model_dump_json(indent=2))
    if job.status in (JobStatus.accepted, JobStatus.running):
        print("Check this job ID again later; do not submit another job.")
        return None
    if job.status != JobStatus.successful:
        print("Job did not succeed. Read its status and message before retrying.")
        return None
    results = client.get_job_results(job_id)
    print(results.model_dump_json(indent=2))
    return results


# --8<-- [end:results]


# --8<-- [start:session]
def main() -> str:
    client = connect()
    try:
        process_id = "primes_between"
        inspect_process(client, process_id)
        request = ProcessRequest(inputs={"min_val": 10, "max_val": 80})
        job_id = submit(client, process_id, request)
        inspect_results(client, job_id)
        print(f"Keep this job ID: {job_id}")
        return job_id
    finally:
        client.close()


# --8<-- [end:session]


if __name__ == "__main__":
    main()
