#!/usr/bin/env python
import sys
import warnings

from oraclebigquerymigrationcrew.crew import OracleBigQueryMigrationCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the crew.
    """
    inputs = {
        'oracle_schema': 'nischal',
        'bq_dataset': 'nischal',
        'gcp_project': 'migration-accelerator-492716'
    }

    try:
        OracleBigQueryMigrationCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'oracle_schema': 'nischal',
        'bq_dataset': 'nischal',
        'gcp_project': 'migration-accelerator-492716'
    }

    try:
        OracleBigQueryMigrationCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        OracleBigQueryMigrationCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'oracle_schema': 'nischal',
        'bq_dataset': 'nischal',
        'gcp_project': 'migration-accelerator-492716'
    }

    try:
        OracleBigQueryMigrationCrew().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")
    
    inputs = {
        "crewai_trigger_payload": trigger_payload,
        'oracle_schema': 'nischal',
        'bq_dataset': 'nischal',
        'gcp_project': 'migration-accelerator-492716'
    }

    try:
        result = OracleBigQueryMigrationCrew().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
