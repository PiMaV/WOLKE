## Installation:
- pull the repo
- install requirements (Watch out for the right "dash_mantine_components" version ) best to use a venv
- edit the config.ini as you like
- run app.py

## Conditions:

- "folder_path":
This points to the root_dir of a folder structure. In root theres a *.db file. within the db file, theres a category "relative_filepath". this points to the images relative from the *.db file

- "id" and "relative_filepath" are mandatory columns


## Good initial values example:

### IR Sky Dataset:
- mean: 0 - 2k
- sharpness: 0 - 0,2
- STD: 0 - 150
- entropy: 0 -12