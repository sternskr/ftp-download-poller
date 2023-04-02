import os
import argparse
import ftplib
import schedule
import time
from dotenv import load_dotenv

load_dotenv()

# Set up argument parser
parser = argparse.ArgumentParser(description='Poll an FTP server for files')
parser.add_argument('--server', type=str, help='FTP server address')
parser.add_argument('--username', type=str, help='FTP username')
parser.add_argument('--password', type=str, help='FTP password')
parser.add_argument('--remote-dir', type=str, help='FTP remote directory to poll')
args = parser.parse_args()

# Set default values for command line arguments
SERVER = args.server or os.getenv('SERVER')
USERNAME = args.username or os.getenv('USERNAME')
PASSWORD = args.password or os.getenv('PASSWORD')
REMOTE_DIR = args.remote_dir or os.getenv('REMOTE_DIR')

# Set up local destination directory for downloaded files
DESTINATION_DIR = os.getenv('DESTINATION_DIR', '/app/convert')

def clear_tmp_files():
    # Remove any existing .tmp files
    for filename in os.listdir(DESTINATION_DIR):
        if filename.endswith('.tmp'):
            os.remove(os.path.join(DESTINATION_DIR, filename))

def create_ftp_connection():
    # Set up FTP connection
    ftp = ftplib.FTP(SERVER)
    ftp.login(user=USERNAME, passwd=PASSWORD)
    ftp.cwd(REMOTE_DIR)

    return ftp

def poll_ftp():
    print('Polling FTP server...')
    # Clear any existing .tmp files
    clear_tmp_files()

    # Create FTP connection
    ftp = create_ftp_connection()

    # Download all files in remote directory tree
    ftp.recurse('', callback=download_file, arg=ftp)

    # Close FTP connection
    ftp.quit()

    print('Done polling FTP server.')

def download_file(ftp, filename):
    print('Downloading ' + filename + '...')
    # Download a single file from the FTP server
    local_filename = os.path.join(DESTINATION_DIR, os.path.relpath(filename, REMOTE_DIR))

    # Create local directory if it doesn't exist
    local_dirname = os.path.dirname(local_filename)
    if not os.path.exists(local_dirname):
        os.makedirs(local_dirname)

    with open(local_filename + '.tmp', 'wb') as f:
        ftp.retrbinary('RETR ' + filename, f.write)

    os.rename(local_filename + '.tmp', local_filename)
    print('Downloaded ' + filename)

    # Delete file from FTP server after download
    ftp.delete(filename)
    print('Deleted ' + filename + ' from FTP server.')

# Schedule the job to run every 30 minutes
schedule.every(30).minutes.do(poll_ftp)

# Run the job indefinitely
while True:
    schedule.run_pending()
    time.sleep(1)
