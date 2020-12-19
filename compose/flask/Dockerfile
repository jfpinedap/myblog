# pull official base image
FROM python:3.8.3-alpine
 
ENV FLASK_APP=myblog.py
ENV FLASK_RUN_HOST=0.0.0.0

# set workdir
WORKDIR /app

# install dependencies
RUN apk add --no-cache gcc musl-dev linux-headers
RUN pip install --upgrade pip

# copy project
COPY . .

# install project
RUN pip install -e .

EXPOSE 5000

# start project
COPY ./compose/flask/start /start
RUN sed -i 's/\r//' /start
RUN chmod +x /start

