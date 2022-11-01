# syntax=docker/dockerfile:1
FROM python:3.11.0a6-slim-bullseye

ENV PATH /opt/conda/bin:$PATH

RUN apt-get update --fix-missing && \
    apt-get install -y \
    wget \
    git \
    vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh \
    && /bin/bash ~/miniconda.sh -b -p /opt/conda \
    && rm ~/miniconda.sh \
    && /opt/conda/bin/conda clean -tipsy \
    && ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh \
    && echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc \
    && echo "conda activate base" >> ~/.bashrc \
    && /opt/conda/bin/conda init bash

RUN conda install -c conda-forge ta-lib

RUN conda install matplotlib

RUN conda install statsmodels

RUN git clone https://github.com/salylgw/gammath_spot.git

WORKDIR /gammath_spot/gammath_spot

RUN pip install -r ../requirements.txt

VOLUME /gammath_spot/gammath_spot

