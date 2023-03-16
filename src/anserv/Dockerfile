FROM python:3.8

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

WORKDIR /app/

# Install python packages
COPY requirements.txt ./
RUN pip install -U pip \
    && pip install --compile -r requirements.txt

# Project files
COPY . /app/

RUN chown www-data:www-data -R /app

USER www-data
EXPOSE 8000

ENTRYPOINT ["./run.sh"]
