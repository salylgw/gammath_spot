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

#RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh \
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-py310_23.5.2-0-Linux-x86_64.sh -O ~/miniconda.sh \
    && /bin/bash ~/miniconda.sh -b -p /opt/conda \
    && rm ~/miniconda.sh \
    && /opt/conda/bin/conda clean -a -y \
    && ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh \
    && echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc \
    && echo "conda activate base" >> ~/.bashrc \
    && /opt/conda/bin/conda init bash

#RUN conda install -c conda-forge ta-lib

RUN git clone https://github.com/salylgw/gammath_spot.git

WORKDIR /gammath_spot/gammath_spot

RUN pip install -r ../requirements.txt --prefer-binary

VOLUME /gammath_spot/gammath_spot

