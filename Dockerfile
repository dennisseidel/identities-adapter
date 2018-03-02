FROM python:3.7-rc-alpine

RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN apk add --no-cache alpine-sdk libffi-dev openssl-dev
RUN pip install -r requirements.txt

EXPOSE 9090
CMD ["python", "/code/app.py"]