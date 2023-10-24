# syntax=docker/dockerfile:1

FROM python:3.8
# Or any preferred Python version.

COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN pip3 install --upgrade pip
RUN python3 -m pip install requests
RUN pip install -r /opt/app/requirements.txt
COPY . /opt/app
CMD [“python”, “./main.py”] 

# Or enter the name of your unique directory and parameter set.