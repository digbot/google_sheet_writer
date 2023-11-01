# syntax=docker/dockerfile:1

FROM python:3.8
# Or any preferred Python version.

ADD requirements.txt /
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ADD main.py /
CMD [ "python", "./main.py" ]

# Or enter the name of your unique directory and parameter set.