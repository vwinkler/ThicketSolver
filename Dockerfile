FROM ubuntu:bionic

RUN apt-get update && apt-get install -y git make g++
RUN git clone https://github.com/sat-group/open-wbo.git
WORKDIR open-wbo
RUN apt-get install -y zlib1g-dev libgmp3-dev python3
RUN make
WORKDIR ..
COPY generate_wcnf.py .
COPY parse_result.py .

ENTRYPOINT python3 generate_wcnf.py --width $0 --height $1 | open-wbo/open-wbo | python3 parse_result.py --width $0 --height $1
