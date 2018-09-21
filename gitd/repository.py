from io import FileIO
import json
from .functions import *
import os
import time

REPO_FILE = ".gitd"

def get_repo_in_folder(service, folder):
    """Attempts to get the repository in the given folder, if none exists,
    return None.
    """
    folder = to_path(folder)
    if(os.path.isfile(folder+REPO_FILE)):
        return Repository(service, folder)
    else:
        return None

def clone_repo_in_folder(service, folder, path):
    # Create repo folder
    name = path.split('/')[-1:][0]
    destination = os.path.join(folder, name)
    try:
        os.mkdir(destination)
    except FileExistsError:
        pass

    if(os.path.isfile(os.path.join(destination, REPO_FILE))):
        # Return false, can't clone a repository into a folder already contains a repository
        return False    
    else:
        return Repository(service, destination, path = path)

class Repository:
    """ Gitd Repository class
    """
    def __init__(self, service, container, path = None, path_id = None):
        container = to_path(container)
        self.service = service
        self.container = container

        # Attempt to read pre-existing config
        if not self.read_config():
            # Config file didn't exist, create config
            self.data = {
                'path': path,
                'name': path.split("/")[-1:][0],
                'sync_time': 0
            }

        self.corrupt = False

        # Attempt to find pre-existing config file
        self.read_config()
        if 'path_id' not in self.data:
            # If no path ID was supplied, get the path ID
            if path_id == None:
                path_id = find_folder_id(service, path)
                if(path_id == None):
                    print("Error: This repository doesn't exist :(")
                    print(f"Tip: You can create a new repository by calling 'gitd init \"{path}\"'")
                    print("  You can also the list available repositories by calling 'gitd list'")
                    self.corrupt = True

            # Set path ID in config
            self.data['path_id'] = path_id

        if not self.is_corrupt():
            self.write_config()

    def pull(self):
        """Pull changes from the Drive folder
        """
        if self.is_corrupt():
            return

        pull_from_folder(self.service, self.container, self.data['path_id'])
        self.set_sync_time(time.time())

    def push(self):
        """Push changes to the Drive folder
        """
        if self.is_corrupt():
            return
        
        push_from_folder(self.service, self.container,
            self.data['path_id'], after_time = self.get_sync_time())
        self.set_sync_time(time.time())

    def read_config(self):
        """Attempt to read config file and set config data.
        If no config file exists, return False. 
        """
        try:
            config_file = FileIO(self.container + REPO_FILE, "rb")
            file_data = json.loads(config_file.readall())
            self.data = file_data
            return True
        except FileNotFoundError:
            # No config file found: new repository
            return False

    def write_config(self):
        """Write current config to the config file
        """
        config_file = FileIO(self.container + REPO_FILE, "wb")
        config_file.seek(0)
        config_file.truncate(0)
        config_file.write(json.dumps(self.data).encode())

    def is_corrupt(self):
        """Return bool for if the repository is corrupt
        """
        return self.corrupt

    def set_name(self, name):
        """Set the name of this repository and update the config file.
        """
        self.data['name'] = name
        self.write_config()

    def get_name(self):
        """Get the name of this repository
        """
        return self.data['name']

    def set_sync_time(self, time):
        self.data['sync_time'] = time
        self.write_config()
    
    def get_sync_time(self):
        return self.data['sync_time']

    def reset_changes_token(self):
        self.data['changes_token'] = self.service.changes().getStartPageToken().execute()['startPageToken']
        self.write_config()

    def is_out_of_date(self):
        """Returns True if the repository is out o; the Drive has been modified
        since the last pull/push request.
        """
        pass
        #files = self.service.files().list(q=f"'{self.data['path_id']}' in parents and trashed = false", fields="files(name, id, md5Checksum)").execute()
        #print(files)
