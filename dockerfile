# Set default environment variables
FROM python:3

ENV DESTINATION_DIR=/app/download
ENV SERVER=ftp.example.com
ENV USERNAME=username
ENV PASSWORD=password
ENV REMOTE_DIR=/remote/directory
ENV DESTINATION_DIR=/download
VOLUME /download

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "./ftp_poller.py"]

CMD ["--server", "$SERVER", "--username", "$USERNAME", "--password", "$PASSWORD", "--remote-dir", "$REMOTE_DIR", "--destination-dir", "$DESTINATION_DIR"]
