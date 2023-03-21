FROM python:3.11.2-slim
RUN apt-get -y update
RUN apt-get -y install git
RUN pip install --upgrade pip
RUN pip install --upgrade streamlit

WORKDIR /app

# Copy File and directories
COPY ./.git/. ./.git
COPY ./.streamlit/. ./.streamlit

COPY ./config/. ./config
COPY ./data/. ./data
COPY ./images/. ./images
COPY ./src/. ./src

COPY ./requirements.txt ./
COPY ./build.properties ./

# Install python requirements
RUN pip install -r requirements.txt 


EXPOSE 8501

ENTRYPOINT ["streamlit", "run"]
CMD ["./src/app.py"]

