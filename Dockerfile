FROM python:3.10-slim-buster

ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

RUN pip3 install -U \
    pip \
    setuptools \
    wheel

WORKDIR /project

RUN useradd -m -r culturecloud && \
    chown culturecloud /project

COPY requirements.txt .
RUN pip3 install --no-cache-dir -Ur requirements.txt

COPY . .

USER culturecloud

ENTRYPOINT ["/tini", "--"]
CMD ["python3", "-m app"]