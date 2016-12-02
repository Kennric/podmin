FROM python:2.7
RUN apt-get update && apt-get install -y \
  postgresql-client \
  sox \
  libsox-fmt-mp3
ENV PYTHONUNBUFFERED 1
ENV PODMIN_DEBUG=1
ENV PODMIN_MEDIA_ROOT=/podmin/podmedia/
RUN mkdir /podmin
WORKDIR /podmin
ADD . /podmin/
RUN pip install -r requirements/staging.txt
