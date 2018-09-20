from __future__ import print_function
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from httplib2 import Http, ServerNotFoundError
from oauth2client import file, client, tools
from sys import argv
import os
from gitd.client import *
from gitd.functions import to_path

PROGRAM_DIR = argv[0][:-7]
WORKING_DIR = os.getcwd()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive',\
    'https://www.googleapis.com/auth/drive.file',\
    'https://www.googleapis.com/auth/drive.appdata']

def get_service():
    global PROGRAM_DIR
    PROGRAM_DIR = to_path(PROGRAM_DIR)
    store = file.Storage(PROGRAM_DIR+"token.json")
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(f"{PROGRAM_DIR}./credentials.json", SCOPES)
        creds = tools.run_flow(flow, store)

    return build('drive', 'v3', http=creds.authorize(Http()))

def main():
    """Main function
    """
    # Connect to Google Drive API
    try:
        service = get_service()
    except ServerNotFoundError:
        print("Error: couldn't connect to Google's servers")
        return

    client = Client(service)

    # Check command arguments
    if(len(argv) < 2):
        print("Action must be provided")
    elif(argv[1] == "clone"):
        if(len(argv) < 3):
            # No file or folder name provided, cloning root
            client.clone(WORKING_DIR, "/")
        else:
            path = argv[2]
            client.clone(WORKING_DIR, path)
    elif(argv[1] == "pull"):
        if(len(argv) < 3):
            # No file or folder name provided, pulling root
            client.pull(WORKING_DIR)
        else:
            path = argv[2]
            client.pull(WORKING_DIR, path)
    elif(argv[1] == "push"):
        if(len(argv) < 3):
            # No file or folder name provided, pushing to everything
            client.push(WORKING_DIR)
        else:
            path = argv[2]
            client.push(WORKING_DIR, path)
    elif(argv[1] == "init"):
        if(len(argv) < 3):
            print("Error: a repository name must be specified when initialising a new repository")
        else:
            path = argv[2]
            client.init(WORKING_DIR, path)

if __name__ == '__main__':
    main()