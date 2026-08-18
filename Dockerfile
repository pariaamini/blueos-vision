FROM debian:bullseye-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        gnupg \
        python3 \
        python3-pip && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg \
        | gpg --dearmor -o /usr/share/keyrings/coral-edgetpu.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/coral-edgetpu.gpg] https://packages.cloud.google.com/apt coral-edgetpu-stable main" \
        > /etc/apt/sources.list.d/coral-edgetpu.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        libedgetpu1-std \
        python3-pycoral && \
    rm -rf /var/lib/apt/lists/*

COPY app /app

RUN python3 -m pip install --upgrade pip setuptools wheel && \
    python3 -m pip install /app --extra-index-url https://www.piwheels.org/simple


EXPOSE 8000/tcp

LABEL version="0.0.3"

ARG IMAGE_NAME

LABEL permissions='\
{\
  "ExposedPorts": {\
    "8000/tcp": {}\
  },\
  "HostConfig": {\
    "Binds":["/usr/blueos/extensions/$IMAGE_NAME:/app"],\
    "ExtraHosts": ["host.docker.internal:host-gateway"],\
    "PortBindings": {\
      "8000/tcp": [\
        {\
          "HostPort": ""\
        }\
      ]\
    }\
  }\
}'

ARG AUTHOR
ARG AUTHOR_EMAIL
LABEL authors='[\
    {\
        "name": "$AUTHOR",\
        "email": "$AUTHOR_EMAIL"\
    }\
]'

ARG MAINTAINER
ARG MAINTAINER_EMAIL
LABEL company='{\
        "about": "",\
        "name": "$MAINTAINER",\
        "email": "$MAINTAINER_EMAIL"\
    }'
LABEL type="example"
ARG REPO
ARG OWNER
LABEL readme='https://raw.githubusercontent.com/$OWNER/$REPO/{tag}/README.md'
LABEL links='{\
        "source": "https://github.com/$OWNER/$REPO"\
    }'
LABEL requirements="core >= 1.1"

ENTRYPOINT litestar run --host 0.0.0.0
