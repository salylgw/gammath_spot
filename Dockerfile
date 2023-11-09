# syntax=docker/dockerfile:1
FROM python:3.10-slim-bullseye

ENV PATH /opt/conda/bin:$PATH

RUN apt-get update --fix-missing && \
    apt-get install -y \
    git \
    vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


RUN git clone https://github.com/salylgw/gammath_spot.git

WORKDIR /gammath_spot/gammath_spot

RUN pip install -r ../requirements.txt --prefer-binary

VOLUME /gammath_spot/gammath_spot
