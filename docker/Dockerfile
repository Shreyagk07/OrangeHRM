FROM php:8.3.14-apache-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends curl unzip libicu-dev libzip-dev libpng-dev libjpeg62-turbo-dev libfreetype6-dev libonig-dev libldap2-dev libcurl4-openssl-dev \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-configure ldap --with-libdir="lib/$(dpkg-architecture --query DEB_HOST_MULTIARCH)" \
    && docker-php-ext-install -j2 pdo_mysql mysqli intl zip gd mbstring ldap curl \
    && a2enmod rewrite && rm -rf /var/lib/apt/lists/*
ARG RELEASE_SHA256=90f587f8a2328562ba8ef3ec54b984dff6446d4c9474541971caf94da784310c
RUN curl --fail --location --retry 3 https://github.com/orangehrm/orangehrm/releases/download/v5.7/orangehrm-5.7.zip -o /tmp/release.zip \
    && echo "${RELEASE_SHA256}  /tmp/release.zip" | sha256sum -c - \
    && unzip -q /tmp/release.zip -d /tmp/release \
    && cp -a /tmp/release/orangehrm-5.7/. /var/www/html/ \
    && chown -R www-data:www-data /var/www/html && rm -rf /tmp/release /tmp/release.zip
COPY docker/apache.conf /etc/apache2/conf-enabled/orangehrm.conf
COPY docker/install.php /opt/qa/install.php
RUN printf 'memory_limit=512M\nupload_max_filesize=4M\npost_max_size=8M\ndate.timezone=UTC\n' > /usr/local/etc/php/conf.d/orangehrm.ini
HEALTHCHECK --interval=10s --timeout=5s --retries=30 CMD curl --fail --silent http://localhost/web/index.php/auth/login >/dev/null || exit 1
