FROM nvidia/cuda:11.6.2-base-ubuntu20.04
VOLUME /dreamerv3-torch-logdir
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Pacific/Auckland
RUN apt-get update
RUN apt-get -y install git python3 python3-pip
RUN apt-get update && apt-get -y install vim

# install gripper requirements
RUN apt-get -y install ffmpeg libsm6 libxext6

RUN git clone https://github.com/ManfredStoiber/gripper_docker.git

## install cares_lib
#COPY ./gripper_docker/cares_lib /cares_lib
RUN pip install -r /gripper_docker/cares_lib/requirements.txt
RUN pip install /gripper_docker/cares_lib

## install cares_reinforcement_learning
#COPY ./gripper_docker/cares_reinforcement_learning /cares_reinforcement_learning
RUN pip install -r /gripper_docker/cares_reinforcement_learning/requirements.txt
RUN pip install --editable /gripper_docker/cares_reinforcement_learning

## copy Gripper-Code
#COPY ./gripper_docker/Gripper-Code /Gripper-Code
RUN pip install -r /gripper_docker/cares_gripper/requirements.txt
RUN pip install --editable /gripper_docker/cares_gripper

# install dreamer requirements
COPY ./requirements.txt /dreamerv3-torch/requirements.txt
RUN pip install -r /dreamerv3-torch/requirements.txt
RUN pip install swig==4.1.1
RUN apt-get -y install patchelf libosmesa6-dev libegl1-mesa libgl1-mesa-glx libglfw3 libglew-dev
RUN pip install pyglet==1.5.27
RUN apt-get -y install libglib2.0-0
COPY . /gripper-rc
# ENTRYPOINT python3 -u /dreamerv3-torch/dreamer.py --configs gymnasium --task gymnasium_ClassicControl_MountainCar-v0 --logdir /dreamerv3-torch-logdir/mountaincar
