FROM python:2.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /podmin
WORKDIR /podmin
ADD . /podmin/
RUN pip install -r requirements/staging.txt
