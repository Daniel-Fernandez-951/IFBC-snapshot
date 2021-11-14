#!/usr/bin/python3

"""
---------------- Iron Fish Blockchain Snapshot Script ----------------------
                         By: Daniel Fernández
                            License: MIT

After downloading (or copying) the script, run this command (Linux/UNIX):
    chmod u+x blockchain_upload.py
Then add your AWS Credentials (hardcoded or in ENV):
    export ACCESS_KEY= <your secret>
    export SECRET_KEY= <your secret>

This script should work anywhere it is place, directories created are all
relative to where the script is when executed.

Visit IRONFISH.NETWORK for more information (whitepaper, install instructions, and more).
"""

import os
import time
import boto3
import shutil
import logging
import datetime
import subprocess
from botocore.exceptions import ClientError

VERSION = 0.2

HOME = os.environ['HOME']
FILENAME_UTC = 'ironfish_db'
BUCKET = 'y3oclgak3p951zai'
OBJECT_NAME = "IronFishBlockchain/"
BLOCKCHAIN_PATH = f'{HOME}/.ironfish/databases/default'
TEMP_DIR = f'{HOME}/upload'

# Make directories--/logs and /upload
os.makedirs(f"{HOME}/upload", exist_ok=True)
os.makedirs(f"{HOME}/logs", exist_ok=True)

# Logging & timing
logging.basicConfig(filename=f'{HOME}/logs/app.log',
                    filemode='a',
                    format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
tt_start = time.time()


def make_zip(blockchain_path=BLOCKCHAIN_PATH):
    zip_start = time.time()
    # Change to saving directory
    os.chdir(TEMP_DIR)
    # Make ZIP of directory
    try:
        shutil.make_archive(FILENAME_UTC,
                            'zip',
                            BLOCKCHAIN_PATH)
        logging.info(f"Zipping Finished: {time.time() - zip_start}")
    except FileNotFoundError or FileExistsError as e_zip:
        logging.critical(f"Error zipping: \n{e_zip}", exc_info=True)
    finally:
        return True


def upload_file(file_name=f"{FILENAME_UTC}.zip", bucket=BUCKET, object_name=f"{FILENAME_UTC}.zip"):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    # Upload the file
    up_start = time.time()
    s3_client = boto3.client('s3',
                             aws_access_key_id=os.environ['ACCESS_KEY'],
                             aws_secret_access_key=os.environ['SECRET_KEY'])
    try:
        response = s3_client.upload_file(file_name, bucket, object_name, ExtraArgs={'ACL': 'public-read'})
        logging.info(f"Upload Finished: {time.time() - up_start}")
    except ClientError as e_upload:
        logging.error(f"Upload Error: \n{e_upload}", exc_info=True)
        return False
    return True


def main():
    _made_zip = make_zip()
    _uploaded = upload_file()

    if _uploaded and _made_zip is True:
        return True
    logging.critical(f"Failure at {__name__}. \n_uploaded: {_uploaded} \n_made_zip: {_made_zip}")
    return False


if __name__ == '__main__':
    logging.info(f"{'-'*10}Uploader Started: {datetime.datetime.utcnow()}{'-' * 10}")
    try:
        main()
        tt_end = time.time()
        logging.info(
            f"Total time v{VERSION}: {tt_end - tt_start}")
        logging.info(f"{'-' * 10}Uploader Ended: {datetime.datetime.utcnow()}{'-' * 10}")

    except subprocess.CalledProcessError as e:
        print(f"Subprocess Error: \n{e}")
