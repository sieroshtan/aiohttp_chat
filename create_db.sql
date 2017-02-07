CREATE USER admin WITH PASSWORD '^chi_admin$';
CREATE DATABASE django_chat_db;
GRANT ALL PRIVILEGES ON DATABASE django_chat_db TO admin;
