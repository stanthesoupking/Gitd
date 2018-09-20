from io import FileIO
from os import listdir
from .repository import *
from .functions import *

class Client:
    """Client object
    User interaction methods are stored in this object.
    """
    def __init__(self, service):
        self.service = service

    def clone(self, container, path = "root"):
        """Clone a repository into the given container folder.
        If no path is supplied then the "root" path will be chosen.
        """
        repo = clone_repo_in_folder(self.service, container, path)
        if repo:
            if not repo.is_corrupt():
                repo.pull()
                print(f"{repo.get_name()} cloned.")
        else:
            print("Error: Unable to clone a repository where one already exists")
        
    def push(self, container, path = None):
        """Push changes to a repository in the given container folder.
        """
        repo = get_repo_in_folder(self.service, container)
        if repo:
            repo.push()
        else:
            print("Error: repository doesn't exist in this folder")

    def pull(self, container, path = None):
        """Pull changes into a repository in the given container folder.
        """
        repo = get_repo_in_folder(self.service, container)
        if repo:
            repo.pull()
        else:
            print("Error: repository doesn't exist in this folder")
    
    def init(self, container, path):
        """Initialise a new repository inside the current folder at the given
        path inside the user's Drive.
        """
        folder = create_folder(self.service, path, fail_if_exists = True)
        if not folder:
            print(f"Error: This repository already exists, clone it by running 'gitd clone {path}'")
        else:
            repo = Repository(self.service, container, path = path, path_id = folder)
            print(f"Repository '{repo.get_name()}' initialised.")
    
    def list_repos(self, path = ''):
        """Gets and displays available repositories inside the user's Drive at the given path.
        """
        path_id = find_folder_id(self.service, path)
        repos = [ x['name'] for x in get_folders(self.service, path_id) ]
        repos.sort()

        for repo in repos:
            print(repo)
        