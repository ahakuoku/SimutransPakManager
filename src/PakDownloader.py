import json
import requests
from cabarchive import CabArchive
import zipfile
import os
import io
from enum import Enum
import re
import logging

class OperationCommand(Enum):
    EXTRACT_ALL_PAK_FILES = "extract_all_pak_files"

def download_local(directory: str, json_file_path: str, index: int) -> None:
    with open(json_file_path, "r") as f:
        pak_definitions = json.load(f)
        definition = pak_definitions["paks"][index]
        # download the pak first.
        download_pakset(definition["pakset_url"], directory)
        # process operations
        pakset_directory = os.path.join(directory, definition["pakset_directory_name"])
        for operation in definition["operations"]:
            if operation["command"] == OperationCommand.EXTRACT_ALL_PAK_FILES.value:
                download_and_extract_pak_files(operation["url"], pakset_directory)
            pass
    pass

MIME_TYPE_ZIP = "application/zip"
MIME_TYPE_CAB = "application/vnd.ms-cab-compressed"

def download_pakset(url: str, directory: str) -> None:
    logging.info(f"start downloading pakset from {url}")
    response = requests.get(url)
    response.raise_for_status()
    logging.info(f"download completed. extracting pakset to {directory}")
    logging.debug(f"response headers: {response.headers}")
    data = response.content
    if response.headers['content-type'] == MIME_TYPE_ZIP:
        extract_zip_pakset(data, directory)
    elif response.headers['content-type'] == MIME_TYPE_CAB:
        extract_cab_pakset(data, directory)
    else:
        # process as zip for unknown MIME type
        extract_zip_pakset(data, directory)

def extract_zip_pakset(data: bytes, directory: str) -> None:
    zip_file = zipfile.ZipFile(io.BytesIO(data))
    names = zip_file.namelist()
    for name in names:
        # skip directory definition
        if name[-1] == os.sep:
            continue
        path = os.path.join(directory, name)
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            __make_directory_if_needed__(dirname)
        file_data = zip_file.read(name)
        with open(path, "wb") as f:
            f.write(file_data)
    pass

def extract_cab_pakset(data: bytes, directory: str) -> None:
    archive = CabArchive(data)
    for name in archive.keys():
        # skip directory definition
        file_name = name.replace("\\", os.sep)
        if file_name[-1] == os.sep:
            continue
        path = os.path.join(directory, file_name)
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            __make_directory_if_needed__(dirname)
        file_data = archive[name].buf
        with open(path, "wb") as f:
            f.write(file_data)
    pass

def download_and_extract_pak_files(url: str, directory: str) -> None:
        logging.info(f"Downloading pak files from {url}")
        response = requests.get(url)
        logging.debug(f"response headers: {response.headers}")
        response.raise_for_status()
        data = response.content
        zip_file = zipfile.ZipFile(io.BytesIO(data))
        __copy_pak_files__(zip_file, directory)
        __copy_jatab_files__(zip_file, directory)
        logging.info(f"Pak extraction succeeded for {url}")
        
def __copy_pak_files__(zip_file: zipfile.ZipFile, directory: str) -> None:
    names = zip_file.namelist()
    for name in names:
        if not name.endswith(".pak"):
            continue
        path = os.path.join(directory, name.split(os.sep)[-1])
        file_data = zip_file.read(name)
        with open(path, "wb") as f:
            f.write(file_data)
    pass

JATAB_REGEX = re.compile(r'^ja\..+\.tab$') # ja.***.tab

def __copy_jatab_files__(zip_file: zipfile.ZipFile, pak_directory: str) -> None:
    names = zip_file.namelist()
    for name in names:
        file_name = name.split(os.sep)[-1]
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