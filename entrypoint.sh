#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
while ! pg_isready -h db -p 5432 -U odoyewu; do
  sleep 1
done

echo "Database is ready!"

# Create tables
python -c "
from database import engine, Base
from models import User, Match, Message, Mission

print('Creating database tables...')
Base.metadata.create_all(bind=engine)
print('Database tables created successfully!')
"

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
