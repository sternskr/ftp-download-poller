FROM python:3

ENV FTP_SERVER=ftp.example.com
ENV FTP_USERNAME=username
ENV FTP_PASSWORD=password
ENV FTP_DIR=/remote/directory
ENV DELETE_FILES=false
VOLUME /download

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY poll_ftp.py poll_ftp.py

ENTRYPOINT ["python", "./poll_ftp.py"]
