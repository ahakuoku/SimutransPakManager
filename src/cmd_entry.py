import PakDownloader
import sys

if __name__ == '__main__':
    json_file = sys.argv[2] if len(sys.argv) > 2 else "pak-definitions.json"
    PakDownloader.download_local(sys.argv[1], json_file)
    pass