#  Dockerfile describing  the steps to build a Docker image based on the Python 3.11.3-slim image. 
#  Including the necessary steps to configure componets and SSH access from the azure portal

FROM python:3.11.3-slim

# Step 1 - Install needed components
RUN apt-get -y update
RUN apt-get -y install git
RUN apt-get install -y lsb-release
RUN apt-get -y install tcpdump

RUN pip install --upgrade pip
RUN pip install --upgrade streamlit


WORKDIR /app

# Step 2 - Copy required filer and directories in WORKDIR /app
COPY ./.git/. ./.git
COPY ./.streamlit/. ./.streamlit
COPY ./conf/. ./conf
COPY ./images/. ./images
COPY ./src/. ./src

COPY ./requirements.txt ./
COPY ./build.properties ./
COPY ./README.md ./

# Step 3 - Install python requirements
RUN pip install -r requirements.txt 

# Step 4 - Enable SSH for access into container from Azure Portal 
ENV SSH_PWD "root:Docker!"
RUN apt-get update \
    && apt-get install -y --no-install-recommends dialog \
    && apt-get install -y --no-install-recommends openssh-server \
    && echo "$SSH_PWD" | chpasswd 

# Step 5 - Final Setup
COPY ./start.sh ./
COPY ./.ssh/sshd_config /etc/ssh/
RUN chmod u+x /app/start.sh

# Step 6 - Done
EXPOSE 8501 2222
ENTRYPOINT [ "/app/start.sh" ] 

# Note required
# ENTRYPOINT ["streamlit", "run"]
# CMD ["./src/app.py"]

