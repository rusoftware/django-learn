#!/bin/sh
set -e

# Espera a que la DB acepte conexiones reales
echo "⏳ Esperando a la base de datos..."
while ! mysqladmin ping -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" --silent; do
  sleep 2
done
echo "✅ DB lista, aplicando migraciones..."

# Ejecutar lo que venga como argumentos
exec "$@"

