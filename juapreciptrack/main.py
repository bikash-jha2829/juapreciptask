from pipeline.pipeline_manager import run_pipeline
from utils.logging_config import initialize_logging

if __name__ == "__main__":
    initialize_logging()  # Initialize logging before anything else
    run_pipeline()
