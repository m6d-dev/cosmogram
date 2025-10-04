FROM ubuntu:latest

RUN apt update && apt install -y \
    unzip \
    p7zip-full \
    unrar \
    tar \
    lzma \
    gzip \
    bzip2

WORKDIR /bomb

COPY run.sh /run.sh
RUN chmod +x /run.sh

RUN echo "starting file run.sh"

CMD ["bash", "/run.sh"]
