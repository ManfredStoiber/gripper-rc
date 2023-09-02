FROM nvidia/cuda:11.6.2-base-ubuntu20.04
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Pacific/Auckland
RUN apt-get update && apt-get -y install git python3 python3-pip
RUN apt-get update && apt-get -y install vim

# install gripper requirements
RUN apt-get -y install ffmpeg libsm6 libxext6

## install cares_lib
RUN git clone https://github.com/UoA-CARES/cares_lib.git
RUN pip install -r /cares_lib/requirements.txt
RUN pip install /cares_lib

## install cares_reinforcement_learning
RUN git clone https://github.com/UoA-CARES/cares_reinforcement_learning.git
RUN pip install -r /cares_reinforcement_learning/requirements.txt
RUN pip install --editable /cares_reinforcement_learning

## install Gripper-Code
RUN git clone https://github.com/ManfredStoiber/gripper_docker.git
#COPY ./gripper_docker/Gripper-Code /Gripper-Code
RUN pip install -r /gripper_docker/cares_gripper/requirements.txt
RUN pip install --editable /gripper_docker/cares_gripper

# install gripper-rc requirements
COPY . /gripper-rc
RUN pip install -r /gripper-rc/requirements.txt
RUN pip install swig==4.1.1
RUN apt-get -y install patchelf libosmesa6-dev libegl1-mesa libgl1-mesa-glx libglfw3 libglew-dev
RUN pip install pyglet==1.5.27
RUN apt-get -y install libglib2.0-0
WORKDIR /gripper-rc
ENTRYPOINT python3 -u /gripper-rc/gripper-rc.py
