import argparse
import os
import schedule
import time
from ftplib import FTP

# Define arguments
parser = argparse.ArgumentParser()
parser.add_argument('server', type=str, help='FTP server')
parser.add_argument('username', type=str, help='FTP username')
parser.add_argument('password', type=str, help='FTP password')
parser.add_argument('remote_dir', type=str, help='Remote directory')
args = parser.parse_args()

# Remove any .tmp files in the POLL_FTP_PATH directory at the start of the script
for root, dirs, files in os.walk(os.getenv('POLL_FTP_PATH')):
    for filename in files:
        if filename.endswith('.tmp'):
            os.remove(os.path.join(root, filename))

def poll_ftp():
    # Connect to FTP server
    ftp = FTP(args.server)
    ftp.login(user=args.username, passwd=args.password)

    # Change directory to remote directory
    ftp.cwd(args.remote_dir)

    # Get list of files and folders in remote directory
    file_list = []
    ftp.retrlines('LIST', file_list.append)

    # Loop through files and folders in remote directory
    for item in file_list:
        tokens = item.split()
        filename = tokens[-1]
        if tokens[0].startswith('d'):  # it is a directory
            if not os.path.exists(os.path.join(os.getenv('POLL_FTP_PATH'), filename)):
                os.makedirs(os.path.join(os.getenv('POLL_FTP_PATH'), filename))
        else:  # it is a file
            local_dir = os.path.join(os.getenv('POLL_FTP_PATH'), tokens[-2])  # create the same folder structure locally
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            local_file = os.path.join(local_dir, filename + '.tmp')  # temporary filename
            try:
                with open(local_file, 'wb') as f:
                    ftp.retrbinary('RETR ' + filename, f.write)
                os.rename(local_file, os.path.join(local_dir, filename))  # rename the file to its final name
                ftp.delete(filename)  # delete the file from the remote directory
            except Exception as e:
                print(f"Error downloading file {filename}: {e}")
                if os.path.exists(local_file):
                    os.remove(local_file)  # delete the temporary file

    # Close FTP connection
    ftp.quit()

# Schedule the job to run every 30 minutes
schedule.every(30).minutes.do(poll_ftp)

# Keep the script running continuously
while True:
    schedule.run_pending()
    time.sleep(1)
