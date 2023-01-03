# COMPILE
FROM python:3.10-slim-buster as compiler
ENV PYTHONUNBUFFERED 1

WORKDIR /project/

RUN python3 -m venv --upgrade-deps /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip3 install --no-cache-dir install wheel \
    && pip3 install --no-cache-dir -Ur requirements.txt

# RUN
FROM python:3.10-slim-buster as runner

ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

WORKDIR /project/

RUN useradd -m -r culturecloud && \
    chown culturecloud /project/

COPY --from=compiler /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . .

USER culturecloud

ENTRYPOINT ["/tini", "--"]
CMD ["python3", "-m app"]