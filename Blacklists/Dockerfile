FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*


RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
EXPOSE 3000
ENV FLASK_APP=app.py


CMD ["flask", "run", "--host=0.0.0.0", "--port=3000"]

##Confguración New Relic
RUN pip install newrelic
RUN apt-get update && apt-get install -y curl
ENV NEW_RELIC_APP_NAME="blacklist-app"
ENV NEW_RELIC_LOG=stdout
ENV NEW_RELIC_DISTRIBUTED_TRACING_ENABLED=true
#INGEST_License
ENV NEW_RELIC_LICENSE_KEY=da9e5eddde8aa5cfdb21bc94f5cd50e7FFFFNRAL
ENV NEW_RELIC_LOG_LEVEL=info
# etc.
RUN echo "NEW_RELIC_LICENSE_KEY=$NEW_RELIC_LICENSE_KEY"
ENTRYPOINT ["newrelic-admin", "run-program"]
