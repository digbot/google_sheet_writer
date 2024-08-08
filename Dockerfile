# syntax=docker/dockerfile:1

FROM python:3.8

# Create app directory
WORKDIR /usr/src/app


# Copy the requirements file to the working directory
COPY requirements.txt ./

# Upgrade pip and install the Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy all the application code and other necessary files/folders
COPY . .

# Command to run the application
CMD ["python", "api.py"]