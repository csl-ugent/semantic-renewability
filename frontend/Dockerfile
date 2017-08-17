FROM ubuntu:16.04

# Update apt-get
RUN apt-get update

# Install libraries required
RUN apt-get install -y wget net-tools

# Install RethinkDB
RUN echo "deb http://download.rethinkdb.com/apt xenial main" | tee /etc/apt/sources.list.d/rethinkdb.list && wget -qO- https://download.rethinkdb.com/apt/pubkey.gpg | apt-key add - && apt-get update && apt-get install rethinkdb -y
COPY rethinkdb.conf /etc/rethinkdb/instances.d/instance1.conf

# Nginx installation and config
RUN apt-get install -y nginx
COPY srn_nginx /etc/nginx/sites-available/srn
COPY srn_nginx_conf /etc/nginx/nginx.conf
RUN ln -s /etc/nginx/sites-available/srn /etc/nginx/sites-enabled/srn
RUN rm /etc/nginx/sites-enabled/default

# Exposing docker web interface and data to outside
EXPOSE 8001
EXPOSE 28015
WORKDIR /opt/semantic_renewability
VOLUME /var/lib/rethinkdb/instance1
CMD service nginx restart && /etc/init.d/rethinkdb restart && tail -f /dev/null

