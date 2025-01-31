from dataactcore.config import CONFIG_DB
from dataactcore.logging import configure_logging
from dataactcore.scripts.database_setup import create_database, run_migrations
from dataactcore.scripts.setup_error_db import setup_error_db
from dataactcore.scripts.setup_job_tracker_db import setup_job_tracker_db
from dataactcore.scripts.setup_user_db import setup_user_db
from dataactcore.scripts.setup_validation_db import setup_validation_db
from dataactcore.scripts.setup_static_data import setup_static_data
from dataactcore.scripts.setup_submission_type_db import setup_submission_type_db


def setup_all_db():
    """Sets up all databases"""
    create_database(CONFIG_DB['db_name'])
    run_migrations()
    setup_job_tracker_db()
    setup_error_db()
    setup_user_db()
    setup_validation_db()
    setup_static_data()
    setup_submission_type_db()


if __name__ == '__main__':
    configure_logging()
    setup_all_db()
