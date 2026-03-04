#!/bin/sh
set -e

# Cache config/routes/views and link storage; tolerate pre-existing links
php artisan config:cache
php artisan route:cache
php artisan view:cache
php artisan storage:link || true

# Run migrations if DB is reachable; don't crash the container on failure
php artisan migrate --force || true

exec "$@"
