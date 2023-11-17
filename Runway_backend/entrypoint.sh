#!/bin/sh

echo 'Waiting for postgres...'
# echo "DB_HOSTNAME: $DB_HOSTNAME, DB_PORT: $DB_PORT"
# while ! nc -z {DB_HOSTNAME} {DB_PORT}; do
#     echo "Waiting for database connection..."
#     sleep 0.1
# done

# while ! python manage.py flush --no-input 2>&1; do
#   echo "Flusing django manage command"
#   sleep 3
# done

# echo 'PostgreSQL started'

echo 'Running migrations...'
python manage.py migrate

echo 'Collecting static files...'
python manage.py collectstatic --no-input

echo "migration and staticfile configured successfully."

exec "$@"