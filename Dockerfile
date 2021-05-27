# install ubuntu
FROM ubuntu:latest
LABEL author="Ryan Fogle"

# update and install python
RUN apt-get update -y
RUN apt-get install -y python3-pip


COPY . /resume_server
WORKDIR /resume_server
RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn
RUN python3 create_db.py
EXPOSE 5000
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
CMD ['python3', 'app.py']