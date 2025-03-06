# Postgres Utils

# Restaurar o Docker Compose
docker compose -f docker-compose-restore.yml up 

# Remover Migrações do Django
docker compose -f docker-compose-remove_migrations_django.yml up

# Fazer Dump
docker compose -f docker-compose-dumper.yml up
