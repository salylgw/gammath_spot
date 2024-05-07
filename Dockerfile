# syntax=docker/dockerfile:1
FROM python:3.12-bullseye

RUN apt-get update --fix-missing && \
    apt-get install -y \
    git \
    vim \
    xvfb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


RUN git clone https://github.com/salylgw/gammath_spot.git

WORKDIR /gammath_spot/gammath_spot

RUN pip install pyvirtualdisplay --prefer-binary

RUN pip install gammath-spot --prefer-binary

VOLUME /gammath_spot/gammath_spot
