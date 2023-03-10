FROM python:3.11-slim

WORKDIR /app
     
COPY ./src/. ./src
COPY ./data/. ./data
COPY ./assets/. ./assets
COPY ./requirements.txt ./
COPY ./build.properties ./

RUN pip install -r requirements.txt 

EXPOSE 8501

ENTRYPOINT ["streamlit", "run"]
CMD ["./src/dashboard.py"]
