#!/bin/sh
# wait-for-postgres.sh

set -e
  
host="$1"
shift
export PGPASSWORD="$POSTGRES_PASSWORD"
until psql -h "$host" -d "$POSTGRES_NAME" -U "$POSTGRES_USER" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
  
>&2 echo "Postgres is up - executing command"
exec $@
