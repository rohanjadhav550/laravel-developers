# Build frontend assets
FROM node:20-alpine AS frontend

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy frontend source files
COPY resources ./resources
COPY tsconfig.json vite.config.ts eslint.config.js ./
COPY public ./public

# Build frontend assets
RUN npm run build


# PHP application
FROM php:8.2-fpm-alpine AS app

# Install system dependencies
RUN apk add --no-cache \
    curl \
    git \
    libpng-dev \
    libxml2-dev \
    libzip-dev \
    oniguruma-dev \
    mysql-client \
    unzip \
    zip \
    nodejs \
    npm \
    supervisor \
    nginx

# Install PHP extensions (ctype, dom, fileinfo, mbstring, tokenizer, xml are already included)
RUN docker-php-ext-install \
    bcmath \
    gd \
    pdo \
    pdo_mysql \
    zip

# Install Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

WORKDIR /var/www/html

# Copy composer files first for better caching
COPY composer.json composer.lock ./

# Install PHP dependencies (without dev dependencies for production)
RUN composer install --no-dev --no-scripts --no-autoloader --prefer-dist

# Copy application code
COPY . .

# Copy built frontend assets from frontend stage
COPY --from=frontend /app/public/build ./public/build

# Generate optimized autoloader and run post-install scripts
RUN composer dump-autoload --optimize && \
    composer run-script post-autoload-dump

# Set permissions
RUN chown -R www-data:www-data /var/www/html && \
    chmod -R 775 storage bootstrap/cache

# Copy nginx configuration
COPY docker/nginx.conf /etc/nginx/http.d/default.conf

# Copy supervisor configuration
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose port
EXPOSE 80

# Start supervisor (manages nginx and php-fpm)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

RUN php artisan migrate
