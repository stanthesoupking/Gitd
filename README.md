# Gitd
***Warning: in its current state, I can't guarantee that it won't delete your stuff***  
Gitd is a git-like command-line interface for pulling and pushing files from your personal Google Drive.

## Installation
*Note: these instructions are for Linux only. Windows and macOS instructions are still on the way.*  
To install, first make sure the you have `python3` and `pip3` installed.

You can check/install this program's dependencies by running
```
pip3 install --upgrade google-api-python-client oauth2client
```
Finally, from inside the source code directory, run:
```
python3 setup.py install
```

## User Guide
Gitd currently supports the following commands:
* clone *- for cloning Google Drive existing folders*
* init *- for initialising a folder that doesn't exist on Google Drive yet*
* list *- for listing folders avaliable to download*
* push *- for pushing changes to Google Drive*
* pull *- for downloading changes from Google Drive*

Commands can be run by typing `gitd` followed by a command.
