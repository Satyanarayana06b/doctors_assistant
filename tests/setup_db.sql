-- Run this file as postgres superuser to set up the database
-- Command: psql -U postgres -f setup_db.sql

-- Create user admin
CREATE USER admin WITH PASSWORD 'admin';

-- Create database
CREATE DATABASE clinic OWNER admin;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE clinic TO admin;

\c clinic

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO admin;
