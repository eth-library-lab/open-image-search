###########
# BUILDER #
###########
FROM python:3.8-slim as build-stage

# set work directory
WORKDIR /usr/src/app

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


#########
# FINAL #
#########
FROM python:3.8-slim 

ENV APP_HOME=/usr/src/app
WORKDIR $APP_HOME

# write out print to console immediately without buffering
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY --from=build-stage $APP_HOME .
RUN pip install --no-cache /usr/src/app/wheels/*

# run entrypoint.prod.sh
# ENTRYPOINT ["sh","entrypoint.sh"]
