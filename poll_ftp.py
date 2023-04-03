import os
import sys
from concurrent.futures import ThreadPoolExecutor
import schedule
import time
import logging
import paramiko
import uuid
import stat

# Set up default values for environment variables
SERVER = os.getenv('FTP_SERVER', '')
USERNAME = os.getenv('FTP_USERNAME', '')
PASSWORD = os.getenv('FTP_PASSWORD', '')
REMOTE_DIR = os.getenv('FTP_DIR', '/remote')
DESTINATION_DIR = '/download'

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Set up console handler to output log messages to console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
logger.addHandler(console_handler)

logger.info(f"SERVER: {SERVER}")
logger.info(f"USERNAME: {USERNAME}")
logger.info(f"PASSWORD: {PASSWORD}")
logger.info(f"REMOTE_DIR: {REMOTE_DIR}")
logger.info(f"DESTINATION_DIR: {DESTINATION_DIR}")

#Create the dir if it doesn't exist already
def create_destination_dir(destination_dir, task_uuid):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
        logger.info(f"Task {task_uuid} Created destination directory: {destination_dir}")

# Define a function to remove any temporary files in the destination directory
def remove_tmp_files(destination_dir):
    logger.info("Removing temporary files...")
    for filename in os.listdir(destination_dir):
        if filename.endswith('.tmp'):
            os.remove(os.path.join(destination_dir, filename))
            logger.info(f"Removed {filename}")

# Define a function to download a single file from the SFTP server
def download_file(sftp, filename, local_filename, task_uuid):
    logger.info(f"Task {task_uuid}: Downloading {filename}...")
    # Use SFTP's get method to download the file and write it to a local file
    sftp.get(filename, local_filename)
    logger.info(f"Task {task_uuid}: Downloaded {filename}")

# Define a function to download a single file using a separate SFTP connection
def download_file_worker(server, username, password, remote_dir, file, destination_dir, task_uuid):
    # Remove the REMOTE_DIR part of the path from the file name
    file = file.replace(remote_dir, '', 1).lstrip('/')
    # Generate the local filename for the downloaded file
    local_filename = os.path.join(destination_dir, file)

    # Create necessary directories for the file
    local_file_directory = os.path.dirname(local_filename)
    create_destination_dir(local_file_directory, task_uuid)

    # Connect to the SFTP server and download the file using the download_file function
    with paramiko.Transport((server, 22)) as transport:
        try:
            transport.connect(username=username, password=password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.chdir(remote_dir)
            download_file(sftp, file, local_filename + '.tmp', task_uuid)
            sftp.remove(file)  # Delete the file on the server after downloading
            logger.info(f"Task {task_uuid}: Deleted {file} from the server")
        except Exception as e:
            logger.error(f"Task {task_uuid}: Error downloading {file}: {e}")

    # Connect to the SFTP server and download the file using the download_file function
    with paramiko.Transport((server, 22)) as transport:
        try:
            transport.connect(username=username, password=password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.chdir(remote_dir)
            download_file(sftp, file, local_filename + '.tmp', task_uuid)
            sftp.remove(file)  # Delete the file on the server after downloading
            logger.info(f"Deleted {file} from the server")
        except Exception as e:
            logger.error(f"Error downloading {file}: {e}")

# Define the main function that downloads all files from the FTP server
def download_files():
    try:
        create_destination_dir(DESTINATION_DIR, "main")
        logger.info(f"Connecting to SFTP server {SERVER} with username {USERNAME}...")
        # Connect to the SFTP server and change to the remote directory
        with paramiko.Transport((SERVER, 22)) as transport:
            try:
                # Remove any temporary files from the destination directory
                remove_tmp_files(DESTINATION_DIR)
                transport.connect(username=USERNAME, password=PASSWORD)
                
                sftp = paramiko.SFTPClient.from_transport(transport)
                sftp.chdir(REMOTE_DIR)
                # Get a list of all files and directories in the remote directory
                files = sftp.listdir_attr()
                logger.info(f"Found {len(files)} files and directories on the SFTP server:")
                for file in files:
                    logger.info(f"- {file.filename} ({stat.filemode(file.st_mode)})")
                logger.info(f"Remote directory: {REMOTE_DIR}")
                logger.info(f"Destination directory: {DESTINATION_DIR}")

                # Use a thread pool to download up to 5 files concurrently
                with ThreadPoolExecutor(max_workers=5) as executor:
                    for file in files:
                        # Check if the item in the list is a file or a directory
                        if not file.st_mode & stat.S_IFDIR:
                            # Generate a UUID for each file download task
                            task_uuid = str(uuid.uuid4())
                            # Submit a download task to the thread pool for each file, passing the UUID as an argument
                            executor.submit(download_file_worker, SERVER, USERNAME, PASSWORD, REMOTE_DIR, file.filename, DESTINATION_DIR, task_uuid)
                # Rename any temporary files to their final names once they have been downloaded completely
                for file in files:
                    if not file.st_mode & stat.S_IFDIR:
                        local_filename = os.path.join(DESTINATION_DIR, os.path.basename(file.filename))
                        os.rename(local_filename + '.tmp', local_filename)
                        logger.info(f"Renamed {local_filename + '.tmp'} to {local_filename}")
                logger.info("All files downloaded successfully")
            except Exception as e:
                logger.error(f"Error: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")
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
