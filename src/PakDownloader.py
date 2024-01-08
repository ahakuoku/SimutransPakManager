import json
import requests
from cabarchive import CabArchive
import zipfile
import os
import io
from enum import Enum
import re
import logging
from typing import Any, Callable
from bs4 import BeautifulSoup

class OperationCommand(Enum):
    EXTRACT_ALL_PAK_FILES = "extract_all_pak_files"
    DOWNLOAD_AND_OPERATIONS = "custom_operations_with_downloaded_file"
    REMOVE_FILE = "remove_file"

class CustomOperationCommand(Enum):
    COPY = "copy_file"

def download_local(directory: str, json_file_path: str, index: int) -> None:
    with open(json_file_path, "r") as f:
        pak_definitions = json.load(f)
        download_from_definition(
            directory, 
            pak_definitions, 
            index,
            lambda message: logging.info(message),
            lambda progress_percent: logging.info(f"progress: {progress_percent}%")
        )
    pass

def download_from_definition(
        directory: str, 
        definition_json: Any, 
        index: int,
        show_message: Callable[[str], None],
        report_progress_percent: Callable[[int], None]
    ) -> None:
    definition = definition_json["paks"][index]
    # download the pak first.
    download_pakset(definition["pakset_url"], directory, show_message, report_progress_percent)
    # process operations
    pakset_directory = os.path.join(directory, definition["pakset_directory_name"])
    for operation in definition["operations"]:
        if operation["command"] == OperationCommand.EXTRACT_ALL_PAK_FILES.value:
            download_and_extract_pak_files(operation["url"], pakset_directory, show_message, report_progress_percent)
        elif operation["command"] == OperationCommand.DOWNLOAD_AND_OPERATIONS.value:
            download_and_do_custom_operations(operation["url"], pakset_directory, operation["operations"])
        elif operation["command"] == OperationCommand.REMOVE_FILE.value:
            remove_file(operation["path"], pakset_directory)

MIME_TYPE_ZIP = "application/zip"
MIME_TYPE_CAB = "application/vnd.ms-cab-compressed"

def download_pakset(
        url: str, 
        directory: str, 
        show_message: Callable[[str], None], 
        report_progress_percent: Callable[[int], None]
    ) -> None:
    show_message(f"start downloading pakset from {url}")
    response = __download_from_url__(url)
    show_message(f"download completed. extracting pakset to {directory}")
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
        # The path separator of the zip file is always '/', even on Windows.
        if name[-1] == '/':
            continue
        # mixing os.sep and '/' separator works fine on Windows.
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

def download_and_extract_pak_files(
        url: str, 
        directory: str,
        show_message: Callable[[str], None], 
        report_progress_percent: Callable[[int], None]
    ) -> None:
        show_message(f"Downloading pak files from {url}")
        response = __download_from_url__(url)
        data = response.content
        zip_file = zipfile.ZipFile(io.BytesIO(data))
        __copy_pak_files__(zip_file, directory)
        __copy_jatab_files__(zip_file, directory)
        show_message(f"Pak extraction succeeded for {url}")

def __copy_pak_files__(zip_file: zipfile.ZipFile, directory: str) -> None:
    names = zip_file.namelist()
    for name in names:
        if not name.endswith(".pak"):
            continue
        # The path separator of the zip file is always '/'
        path = os.path.join(directory, name.split('/')[-1])
        file_data = zip_file.read(name)
        with open(path, "wb") as f:
            f.write(file_data)
    pass

JATAB_REGEX = re.compile(r'^ja\..+\.tab$') # ja.***.tab

def __copy_jatab_files__(zip_file: zipfile.ZipFile, pak_directory: str) -> None:
    names = zip_file.namelist()
    for name in names:
        # The path separator of the zip file is always '/', even on Windows.
        file_name = name.split('/')[-1]
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

def download_and_do_custom_operations(url: str, pakset_directory: str, operations: list[dict]) -> None:
    logging.info(f"Downloading pak files from {url}")
    response = __download_from_url__(url)
    logging.info(f"Downloading succeeded.")
    data = response.content
    zip_file = zipfile.ZipFile(io.BytesIO(data))
    for operation in operations:
        __process_custom_operation__(operation, zip_file, pakset_directory)

def __process_custom_operation__(operation: dict, zip_file: zipfile.ZipFile, pakset_directory: str) -> None:
    if operation["command"] == CustomOperationCommand.COPY.value:
        logging.info(f"copying file from {operation['source_path']} to {operation['destination']}")
        source_path = operation["source_path"]
        # The file separator in the definition json file is always '/'.
        file_name = source_path.split('/')[-1]
        destination = os.path.join(pakset_directory, operation["destination"])
        with open(os.path.join(destination, file_name), "wb") as f:
            f.write(zip_file.read(source_path))

def __make_directory_if_needed__(directory: str) -> None:
    parent = os.path.dirname(directory)
    if not os.path.exists(parent):
        __make_directory_if_needed__(parent)
    if not os.path.exists(directory):
        os.makedirs(directory)

# Do a get request for the given url. It raises an exception if the response is an error.
def __download_from_url__(url: str) -> requests.Response:
    if "getuploader.com" in url:
        return __download_from_getuploader__(url)
    response = requests.get(url)
    logging.debug(f"response headers: {response.headers}")
    response.raise_for_status()
    return response

# getuploader.com requests us to do a special operation to download the file.
def __download_from_getuploader__(url: str) -> requests.Response:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    # extract data to compose download url
    token = soup.find('input', attrs={'name': 'token', 'type': 'hidden'})['value']
    fileName = soup.find('meta', attrs={'name': 'keywords'})['content'].split(',')[0]
    userName = soup.find('a', attrs={'class': 'navbar-brand'})['href'].split('/')[-2]
    index = url.split('/')[-1]
    # download actual file
    downloadUrl = f'https://downloadx.getuploader.com/g/{token}/{userName}/{index}/{fileName}'
    response = requests.get(downloadUrl)
    response.raise_for_status()
    return response

def remove_file(path_in_pakset: str, pakset_directory: str) -> None:
    logging.info(f"removing file {path_in_pakset}")
    path = os.path.join(pakset_directory, path_in_pakset)
    os.remove(path)
