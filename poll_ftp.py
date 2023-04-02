import os
import sys
from ftplib import FTP
from concurrent.futures import ThreadPoolExecutor
import schedule
import time

# Set up default values for environment variables
SERVER = os.getenv('FTP_SERVER', '')
USERNAME = os.getenv('FTP_USERNAME', '')
PASSWORD = os.getenv('FTP_PASSWORD', '')
REMOTE_DIR = os.getenv('REMOTE_DIR', '/done')
DESTINATION_DIR = os.getenv('DESTINATION_DIR', '/app/convert')

# Define a function to remove any temporary files in the destination directory
def remove_tmp_files(destination_dir):
    for filename in os.listdir(destination_dir):
        if filename.endswith('.tmp'):
            os.remove(os.path.join(destination_dir, filename))

# Define a function to download a single file from the FTP server
def download_file(ftp, filename, local_filename):
    with open(local_filename, 'wb') as f:
        # Use FTP's retrbinary method to download the file and write it to a local file
        ftp.retrbinary('RETR ' + filename, f.write)
    print(f"Downloaded {filename}")

# Define a function to download a single file using a separate FTP connection
def download_file_worker(server, username, password, remote_dir, file, destination_dir):
    # Generate the local filename for the downloaded file
    local_filename = os.path.join(destination_dir, os.path.basename(file))
    # Connect to the FTP server and download the file using the download_file function
    with FTP(server) as ftp:
        ftp.login(user=username, passwd=password)
        ftp.cwd(remote_dir)
        download_file(ftp, file, local_filename + '.tmp')

# Define the main function that downloads all files from the FTP server
def download_files():
    try:
        # Connect to the FTP server and change to the remote directory
        with FTP(SERVER) as ftp:
            ftp.login(user=USERNAME, passwd=PASSWORD)
            ftp.cwd(REMOTE_DIR)
            # Get a list of all files in the remote directory
            files = ftp.nlst()
            # Remove any temporary files from the destination directory
            remove_tmp_files(DESTINATION_DIR)
            # Use a thread pool to download up to 5 files concurrently
            with ThreadPoolExecutor(max_workers=5) as executor:
                for file in files:
                    # Submit a download task to the thread pool for each file
                    executor.submit(download_file_worker, SERVER, USERNAME, PASSWORD, REMOTE_DIR, file, DESTINATION_DIR)
            # Rename any temporary files to their final names once they have been downloaded completely
            for file in files:
                local_filename = os.path.join(DESTINATION_DIR, os.path.basename(file))
                os.rename(local_filename + '.tmp', local_filename)
            print("All files downloaded successfully")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

# Run the download_files function once at the beginning
if __name__ == '__main__':
    download_files()
    # Use the schedule library to run the download_files function every 30 minutes
    schedule.every(30).minutes.do(download_files)

    while True:
        # Check if any scheduled tasks are due to run, and run them if they are
        schedule.run_pending()
        # Wait for 1 second before checking again
        time.sleep(1)
