FROM python:3

# Set working directory
WORKDIR /app

# Copy Python script to container
COPY poll_ftp.py /app/

# Install necessary packages
RUN pip install --no-cache-dir \
    schedule \
    python-dotenv \
    argparse \
    ftplib

# Set default environment variables
ENV POLL_FTP_PATH=/app/convert
ENV SERVER=ftp.example.com
ENV USERNAME=username
ENV PASSWORD=password
ENV REMOTE_DIR=/remote/directory

# Run the Python script with command line arguments
CMD python poll_ftp.py $SERVER $USERNAME $PASSWORD $REMOTE_DIR
