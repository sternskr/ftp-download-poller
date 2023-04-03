# Set default environment variables
FROM python:3

EXPOSE 22

ENV SERVER=ftp.example.com
ENV USERNAME=username
ENV PASSWORD=password
ENV REMOTE_DIR=/remote/directory
ENV DESTINATION_DIR=/download
VOLUME /download

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY poll_ftp.py poll_ftp.py

ENTRYPOINT ["python", "./poll_ftp.py"]

CMD ["--server", "$SERVER", "--username", "$USERNAME", "--password", "$PASSWORD", "--remote-dir", "$REMOTE_DIR", "--destination-dir", "$DESTINATION_DIR"]
