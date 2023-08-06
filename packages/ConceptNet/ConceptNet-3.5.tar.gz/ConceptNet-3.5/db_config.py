DB_ENGINE = "sqlite3" # may also be 'postgresql', 'postgresql_psycopg2', 'mysql', or 'ado_mssql'.
DB_NAME = "ConceptNet" # This should be the path to database file if using sqlite3.
#DB_HOST = "csc-sql.media.mit.edu" # Not used with sqlite3.
#DB_PORT = "5432" # Not used with sqlite3.
#DB_USER = "openmind" # Set to empty string for localhost. Not used with sqlite3.
#DB_PASSWORD = "uataimec" # Set to empty string for default. Not used with sqlite3.
DB_SCHEMAS = "public"
q="""
idea:
    have a chunk of code at the top of the script that is:
    >>>from django.conf import settings
    >>>settings.configure(DATABASE_ENGINE="sqlite3", DATABASE_NAME="ConceptNet"...

    >>>
    """
