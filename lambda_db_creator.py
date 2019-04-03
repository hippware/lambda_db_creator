import logging
import psycopg2

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Params:
# db_name
# db_user
# db_password
# db_host
# users [ { username, password, read-only } ]

def lambda_handler(event, context):
    logger.info(f"Connecting to postgres server")
    conn = psycopg2.connect(conn_string(event, "postgres"))
    conn.autocommit = True
    cursor = conn.cursor()

    db_name = event['db_name']

    # Create Database
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = %s", [db_name])
    if cursor.fetchone() == None:
        logger.info(f"Database {db_name} not found - creating")
        cursor.execute(f"CREATE DATABASE {db_name}")
    else:
        logger.info(f"Database {db_name} found - skipping creation")

    cursor.execute(f"REVOKE CONNECT ON DATABASE {db_name} FROM PUBLIC")

    # Create requested user
    for u in event['users']:
        create_user(u, db_name, event, cursor)

    cursor.close()
    conn.close()

def conn_string(event, db_name):
    return "user=" + event['db_user'] + " password=" + event['db_password'] + " host=" + event['db_host'] + " dbname=" + db_name

def create_user(u, db_name, event, cursor):
    logger.info(f"Connecting to postgres server on db {db_name}")

    username = u['username']
    password = u['password']

    cursor.execute(f"SELECT 1 FROM pg_user WHERE usename = %s", [username])
    if cursor.fetchone() == None:
        logger.info(f"User {username} not found - creating")
        cursor.execute(f"CREATE USER {username} WITH ENCRYPTED PASSWORD %s", [password]);
    else:
        logger.info(f"User {username} found - setting password")
        cursor.execute(f"ALTER USER {username} ENCRYPTED PASSWORD %s", [password]);

    if u['read-only'] == "true":
        logger.info(f"Granting READ-ONLY privileges on {db_name} to {username}")
        cursor.execute(f"GRANT CONNECT ON DATABASE {db_name} TO {username}")
        cursor.execute(f"GRANT USAGE ON SCHEMA public TO {username}")
        cursor.execute(f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {username}")
        cursor.execute(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO {username}")
    else:
        logger.info(f"Granting all privileges on {db_name} to {username}")
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {username}")

# For quick testing purposes:
def d():
    return {
        "db_name": "test_created",
        "db_user": "postgres",
        "db_password": "password",
        "db_host": "localhost",
        "users" :
        [
            {
                "username": "test_user",
                "password": "test_password",
                "read-only": "false"
            },
            {
                "username": "rouser",
                "password": "test_password",
                "read-only": "true"
            }
        ]
    }
