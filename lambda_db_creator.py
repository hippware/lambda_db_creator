import logging
import psycopg2

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Params:
# db_name
# db_user
# db_password
# db_host
# new_user
# new_password

def lambda_handler(event, context):
    logger.info(f"Connecting to postgres server")
    conn = psycopg2.connect(conn_string(event))
    conn.autocommit = True
    cursor = conn.cursor()

    db_name = event['db_name']
    new_user = event['new_user']
    password = event['new_password']

    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = %s", [db_name])
    if cursor.fetchone() == None:
        logger.info(f"Database {db_name} not found - creating")
        cursor.execute(f"CREATE DATABASE {db_name}")
    else:
        logger.info(f"Database {db_name} found - skipping creation")

    cursor.execute(f"SELECT 1 FROM pg_user WHERE usename = %s", [new_user])
    if cursor.fetchone() == None:
        logger.info(f"User {new_user} not found - creating")
        cursor.execute(f"CREATE USER {new_user} WITH ENCRYPTED PASSWORD %s", [password]);
    else:
        logger.info(f"User {new_user} found - setting password")
        cursor.execute(f"ALTER USER {new_user} ENCRYPTED PASSWORD %s", [password]);

    logger.info(f"Granting all privileges on {db_name} for {new_user}")
    cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {new_user}")

    cursor.close()
    conn.close()

def conn_string(event):
    return "user=" + event['db_user'] + " password=" + event['db_password'] + " host=" + event['db_host'] + " dbname=postgres"

# For quick testing purposes:
def d():
    return {
     "db_name": "test_created",
     "db_user": "postgres",
     "db_password": "password",
     "db_host": "localhost",
     "new_user": "test_user",
     "new_password": "test_password"
    }
