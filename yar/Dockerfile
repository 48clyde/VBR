#
# Use the latest ubuntu, which is currently 20.04
#
FROM ubuntu:latest
MAINTAINER 48clyde
ENV DEBIAN_FRONTEND=noninteractive

#
# Get the required extras and clean up
#
RUN apt-get update -y && \
  apt-get install -qy abcde cdparanoia eject flac netcat setcd sdparm eyed3 lame && \
  apt-get remove -qy postfix && \
  apt-get -qy clean && \
  apt-get -qy purge && \
  apt-get -qy autoremove && \
  rm -rf /var/lib/apt/lists/*

#
# copy into the container the custom conf and the main
# shell script that checks for disks having been inserted
#
COPY abcde-local.conf /etc/abcde-local.conf
COPY yar.sh /usr/local/bin/yar.sh

ENTRYPOINT ["/usr/local/bin/yar.sh"]
