# Lightweight Laravel runtime using PHP built-in server (sufficient for Render web service)
# For higher performance, swap to nginx+caddy/fpm setup later.

FROM php:8.2-cli AS base

# Install system dependencies and PHP extensions
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       git unzip libpq-dev libzip-dev libpng-dev libonig-dev libxml2-dev \
    && docker-php-ext-install \
       pdo_pgsql pdo_mysql gd bcmath pcntl zip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Composer
ENV COMPOSER_HOME=/tmp/composer
RUN php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');" \
    && php composer-setup.php --install-dir=/usr/local/bin --filename=composer \
    && php -r "unlink('composer-setup.php');"

WORKDIR /var/www/html

# Copy dependency definitions first to leverage Docker layer cache
COPY composer.json composer.lock ./
RUN composer install --no-dev --no-interaction --optimize-autoloader --no-scripts

# Copy application code
COPY . .

# Re-run scripts that need source present (e.g., package discovery)
RUN composer install --no-dev --no-interaction --optimize-autoloader

# Ensure storage/logs exists
RUN mkdir -p storage/logs bootstrap/cache \
    && chmod -R 755 storage bootstrap/cache

# Expose HTTP port
EXPOSE 10000

# Entrypoint handles caching, migrations, storage link, then starts server
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Default command
CMD ["php", "-S", "0.0.0.0:10000", "-t", "public"]
