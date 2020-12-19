FROM nginx

ENV NGINXDIR=/server

RUN mkdir $NGINXDIR
WORKDIR $NGINXDIR

RUN mkdir /etc/nginx/sites-enabled

COPY ./nginx/nginx.conf /etc/nginx/

COPY ./ssl/ $NGINXDIR/ssl
RUN rm -rf /etc/nginx/sites-*/default

COPY ./nginx/production_backend_conf /etc/nginx/sites-available/

RUN ln -s /etc/nginx/sites-available/production_backend_conf /etc/nginx/sites-enabled/

RUN mkdir -p /var/www/html

CMD ["nginx", "-g", "daemon off;"]
