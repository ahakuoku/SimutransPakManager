import json
import requests
import cabarchive
import zipfile
import os
import io
from enum import Enum
import re

class OperationCommand(Enum):
    EXTRACT_ALL_PAK_FILES = "extract_all_pak_files"

def download_local(directory: str, json_file_path: str) -> None:
    with open(json_file_path, "r") as f:
        pak_definitions = json.load(f)
        definition = pak_definitions["paks"][0]
        # download the pak first.
        download_pakset(definition["pakset_url"], directory)
        # process operations
        pakset_directory = os.path.join(directory, definition["pakset_directory_name"])
        for operation in definition["operations"]:
            if operation["command"] == OperationCommand.EXTRACT_ALL_PAK_FILES.value:
                download_and_extract_pak_files(operation["url"], pakset_directory)
            pass
    pass

def download_pakset(url: str, directory: str) -> None:
    print(f"start downloading pakset from {url}")
    response = requests.get(url)
    print(f"download completed. extracting pakset to {directory}")
    data = response.content
    zip_file = zipfile.ZipFile(io.BytesIO(data))
    names = zip_file.namelist()
    for name in names:
        # skip directory definition
        if name[-1] == "/":
            continue
        path = os.path.join(directory, name)
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            __make_directory_if_needed__(dirname)
        file_data = zip_file.read(name)
        with open(path, "wb") as f:
            f.write(file_data)
    pass

def download_and_extract_pak_files(url: str, directory: str) -> None:
        response = requests.get(url)
        data = response.content
        zip_file = zipfile.ZipFile(io.BytesIO(data))
        __copy_pak_files__(zip_file, directory)
        __copy_jatab_files__(zip_file, directory)
        
def __copy_pak_files__(zip_file: zipfile.ZipFile, directory: str) -> None:
    names = zip_file.namelist()
    for name in names:
        if not name.endswith(".pak"):
            continue
        path = os.path.join(directory, name.split("/")[-1])
        file_data = zip_file.read(name)
        with open(path, "wb") as f:
            f.write(file_data)
    pass

JATAB_REGEX = re.compile(r'^ja\..+\.tab$') # ja.***.tab

def __copy_jatab_files__(zip_file: zipfile.ZipFile, pak_directory: str) -> None:
    names = zip_file.namelist()
    for name in names:
        file_name = name.split("/")[-1]
        if file_name == "ja.tab":
            # TODO: Need to add its contents to ja.tab
            continue
        if JATAB_REGEX.match(file_name) == None:
            continue
        file_data = zip_file.read(name)
        text_path = os.path.join(pak_directory, "text")
        path = os.path.join(text_path, file_name)
        with open(path, "wb") as f:
            f.write(file_data)
    pass

def __make_directory_if_needed__(directory: str) -> None:
    parent = os.path.dirname(directory)
    if not os.path.exists(parent):
        __make_directory_if_needed__(parent)
    if not os.path.exists(directory):
        os.makedirs(directory)
    pass