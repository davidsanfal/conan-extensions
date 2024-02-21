FROM ubuntu

RUN apt update && apt upgrade -y
RUN apt install -y build-essential
RUN apt install -y python3-pip cmake
COPY conandocker /root/conandocker
RUN pip3 install conan
RUN rm -rf /root/.conan2
