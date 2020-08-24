#
# 
#
FROM python:3.8.5-alpine3.12
MAINTAINER 48clyde

#
# Need ffmpeg to do the encoding
#
RUN apk add --no-cache ffmpeg

#
# copy into the container script to manage the mirroring
#
COPY mirror.py /mirror.py

ENTRYPOINT ["python", "/mirror.py"]
