import PakDownloader
import sys
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    PakDownloader.download_local(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    pass