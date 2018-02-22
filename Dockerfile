FROM ubuntu:14.04

LABEL maintainer "gngrbdk@gmail.com"

# Set /opt/ as working directory
WORKDIR /opt

# Copy this file into container
COPY Dockerfile /opt

# Copy Forest Tuner script
COPY forest-tuner.py /opt

# Update Ubuntu package index
RUN apt-get update

# Install common dependencies
RUN apt-get install -y \
    wget \
    unzip \
    build-essential \
    software-properties-common \
    libboost-all-dev \
    libxft-dev \
    libfreetype6-dev \
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    gfortran \
    python-pip \
    python-dev \
    python

# Download msgsteiner 1.3
RUN wget http://staff.polito.it/alfredo.braunstein/code/msgsteiner-1.3.tgz && tar xzf msgsteiner-1.3.tgz && rm msgsteiner-1.3.tgz

# Change dir into msgsteiner and compile
WORKDIR /opt/msgsteiner-1.3
RUN make

# Go back to original working directory
WORKDIR /opt

# Download Omics Integrator 0.3.1
RUN wget https://github.com/fraenkel-lab/OmicsIntegrator/archive/v0.3.1.zip && unzip v0.3.1.zip && rm v0.3.1.zip

# Install required Python packages
RUN pip install -r /opt/OmicsIntegrator-0.3.1/requirements.txt

# Fix networkx version
RUN pip uninstall -y networkx && pip install networkx==1.11
