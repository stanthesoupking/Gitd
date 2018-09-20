import os
from io import FileIO
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from googleapiclient.errors import HttpError
from shutil import rmtree

# Useful functions

def get_files(service, path_id):
    """Returns a list of all files inside the given folder id
    """
    q = f"'{path_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed = false"
    result = service.files().list(q=q).execute()['files']
    return result

def get_folders(service, path_id):
    """Returns a list of all folders inside the given folder id
    """
    q = f"'{path_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed = false"
    result = service.files().list(q=q).execute()['files']
    return result

def create_folder(service, path, from_path = 'root', fail_if_exists = False):
    """Creates a folder with the given path. If fail_if_exists is set to True
    then the function will return False if a folder at the given path already
    exists.

    If this function succeeds then the ID of the new folder will be returned
    """
    if 'path' == '':
        return 'root'

    pfolders = path.split('/') # Get folder names
    pfolders = [ f for f in pfolders if f != '' ] # Prune folders named ''

    current_id = from_path
    for pf in pfolders:
        q = f"'{current_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed = false"
        lfolders = service.files().list(q=q).execute()
        found = False
        for lf in lfolders['files']:
            if lf['name'] == pf:
                if fail_if_exists and pf == pfolders[-1:][0]:
                    # Destination folder exists, return error if fail_if_exists
                    # was specified.
                    return False
                else:
                    current_id = lf['id']
                    found = True
                    break
        if not found:
            # Folder doesn't exist, create it
            body = {
                'name': pf,
                'parents': [current_id],
                'mimeType': 'application/vnd.google-apps.folder'
            }
            result = service.files().create(body = body).execute()
            current_id = result['id']

    return current_id
    

def find_folder_id(service, path, from_path = 'root'):
    """Find the ID of the folder at the given path
    Path should be in the format of 'foo/bar'. If the ID can't be found, None
    will be returned. 
    To start scanning from a directory other than 'root', set the from_path
    variable
    """
    if path == '':
        return 'root'

    pfolders = path.split('/') # Get folder names
    pfolders = [ f for f in pfolders if f != '' ] # Prune folders named ''

    current_id = from_path
    for pf in pfolders:
        q = f"'{current_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed = false"
        lfolders = service.files().list(q=q).execute()
        found = False
        for lf in lfolders['files']:
            if lf['name'] == pf:
                current_id = lf['id']
                found = True
                break
        if not found:
            return None

    return current_id

def push_from_folder(service, container, folder, recursive = True):
    """Pushes files from the inside the container folder into the Drive folder with the given folder ID.
    This function is set to recursive by default, so it will upload files
    inside sub-directories
    """
    container = to_path(container)
    ls = os.listdir(container)

    ffiles = [ x for x in ls if os.path.isfile(container+x) ]
    ffolders = [ x for x in ls if x not in ffiles ]

    efiles = get_files(service, folder)
    efolders = get_folders(service, folder)

    for ffile in ffiles:
        updated = False
        for efile in efiles:
            if ffile == efile['name']:
                print(f"Updating {ffile}...")

                media = MediaFileUpload(container+ffile)
                service.files().update(fileId = efile['id'], media_body = media).execute()
                updated = True
                break
        if not updated:
            print(f"Uploading new file {ffile}...")

            body = {
                'name': ffile,
                'parents': [folder]
            }

            media = MediaFileUpload(container+ffile)

            service.files().create(body = body, media_body = media).execute()

    for ffolder in ffolders:
        updated = False
        for efolder in efolders:
            if ffolder == efolder['name']:
                print(f"Updating {ffolder}...")
                push_from_folder(service, container+ffolder+"/", efolder['id'])
                updated = True
                break
        if not updated:
            # Folder doesn't exist on Drive, create it
            body = {
                'name': ffolder,
                'parents': [folder],
                'mimeType': 'application/vnd.google-apps.folder'
            }

            result = service.files().create(body = body).execute()
            # Upload contents
            push_from_folder(service, container+ffolder+"/", result['id'])


def pull_from_folder(service, container, folder, recursive = True, force = False):
    """Pulls files from the given folder ID and stores them in the container path.
    This function is set to recursive by default, so it will download files
    inside sub-directories.
    If force is set to True then the program will automatically assume that the
    the user responds 'Yes' to any prompt.
    """
    container = to_path(container)
    q=f"'{folder}' in parents and trashed = false"
    files = service.files().list(q=q).execute()['files']
    
    # Check to see if any files need deleting
    ffiles = [ x['name'] for x in files ]
    to_delete = [ x for x in os.listdir(container) if x not in ffiles ]

    # If files need to be deleted, ask user if they wish to proceed
    if not force and (len(to_delete) > 0):
        print("The following files/folders are present and need to be deleted in order to pull.")
        for file in to_delete:
            if(os.path.isdir(os.path.join(container, file))):
                print(f" {file}/...")
            else:
                print(f" {file}")

        ans = None
        while(ans == None):
            ans = input("Do you still wish to proceed (y/n)? ")
            if(ans == 'y'):
                ans = True
            elif(ans == 'n'):
                return
            else:
                print('Invalid input')
                ans = None
    
    # Delete files that didn't exist on the Google Drive
    for file in to_delete:
        if(os.path.isdir(os.path.join(container, file))):
            # Delete the directory
            rmtree(os.path.join(container, file))
        else:
            # Delete the file
            os.remove(os.path.join(container, file))

    # Download files from Drive
    for file in files:
            if(file['mimeType'] == 'application/vnd.google-apps.folder'):
                # File is of type folder, create folder an download it's files
                path = container+file['name']
                safe_create_folder(path)
                if recursive:
                    pull_from_folder(service, path, file['id'])
            else:
                print(f"Pulling {file['name']} into {container}...")
                request = service.files().get_media(fileId=file['id'])
                fh = FileIO(container+file['name'],'wb')
                try:
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print("Download %d%%." % int(status.progress() * 100))
                except HttpError:
                    print("Failed")
                fh.close()

def safe_create_folder(directory):
    """Checks to see if the directory already exists, if not then create it.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def to_path(path):
    """Returns the given path in the correct format;
    Ending with the '/' characer.
    """
    path += "/" if path[-1:] != "/" else ""
    return path