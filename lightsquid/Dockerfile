FROM debian:bullseye-slim

RUN apt update ;\
    apt -y upgrade ;\
    apt -y install apache2 libapache2-mod-perl2 libapache2-mod-php libcgi-session-perl libgd-perl ;\
    apt -y autoremove ;\
    apt-get -y clean ;\
    a2enmod cgi perl php7.4 ssl authnz_ldap ;\
    service apache2 stop ;\
    rm -rf /var/www/html/* ;\
    rm -rf /etc/apache2/sites-enabled/*

COPY ./lightsquid-1.8/ /var/www/html/
COPY ./lightsquid-apache2.conf /etc/apache2/sites-enabled/lightsquid.conf

RUN chmod -R 0755 /var/www/html
RUN chown -R www-data:www-data /var/www/html

WORKDIR /var/www/html

RUN chmod +x *.cgi
RUN chmod +x *.pl

CMD service apache2 start; tail -f /dev/null
