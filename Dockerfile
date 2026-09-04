# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm

RUN apt-get update --fix-missing && \
    apt-get install --no-install-recommends -y \
    git \
    vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


RUN git clone https://github.com/salylgw/gammath_spot.git

WORKDIR /gammath_spot/gammath_spot

RUN pip install --prefer-binary --no-cache-dir gammath-spot

VOLUME /gammath_spot/gammath_spot
