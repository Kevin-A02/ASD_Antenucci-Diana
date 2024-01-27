import urllib
import zipfile

from utils import GLOBAL_PATH


def install_spotbugs():
    spotbugs_url = "https://github.com/spotbugs/spotbugs/releases/download/4.8.3/spotbugs-4.8.3.zip"

    print("Downloading Spotbugs...")
    urllib.request.urlretrieve(spotbugs_url, "spotbugs.zip")

    print("Extracting Spotbugs...")
    with zipfile.ZipFile("spotbugs.zip", "r") as zip:
        zip.extractall(GLOBAL_PATH)

if __name__ == '__main__':
    install_spotbugs()