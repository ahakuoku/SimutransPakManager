import PakDownloader
import sys

if __name__ == '__main__':
    PakDownloader.download_local(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    pass