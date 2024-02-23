FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN  pip3 install --upgrade pip && pip3 install -r requirements.txt
COPY . .

EXPOSE 8501

## update app environment for local development
# ENV NEPTUNE_HOST=${NEPTUNE_HOST}
# ENV NEPTUNE_PORT=${NEPTUNE_PORT}

# ENV COGNITO_POOL_ID=${COGNITO_POOL_ID}
# ENV COGNITO_APP_CLIENT_ID=${COGNITO_APP_CLIENT_ID}
# ENV COGNITO_APP_CLIENT_SECRET=${COGNITO_APP_CLIENT_SECRET}

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
