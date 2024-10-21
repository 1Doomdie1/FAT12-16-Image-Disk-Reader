FROM ubuntu:latest
COPY . /fat12-16-iamge-disk-reader
WORKDIR /fat12-16-iamge-disk-reader
RUN apt update && apt upgrade -y
RUN apt install python3 python3-pip -y
RUN apt-get install libmagic1 -y
RUN pip3 install -r requirements_linux.txt --break-system-packages