import os
import re
import tarfile
import urllib.request

LINK_TO_REPO = "https://github.com/apache/groovy"
GLOBAL_PATH = os.path.dirname(os.path.abspath(__file__))

PROJECT_PATH = os.path.join(GLOBAL_PATH, "groovy-master")
BUILD_PATH = os.path.join(PROJECT_PATH, "build")
GRADLEW_PATH = os.path.join(PROJECT_PATH, "gradlew")

README_PATH = os.path.join(PROJECT_PATH, "README.adoc")

SPOTBUGS_PATH = os.path.join(GLOBAL_PATH, "spotbugs-4.8.3/bin/spotbugs")
REPORT_DIR = os.path.join(os.path.join(BUILD_PATH, "reports"), "spotbugs")
XML_FILE_NAME = os.path.join(REPORT_DIR, "main.xml")
XML_FILE_PATH = os.path.join(REPORT_DIR, XML_FILE_NAME)

RESULTS_PATH = os.path.join(GLOBAL_PATH, "results")
CATEGORIES_FILENAME = "bug_categories.json"
BUGCOUNT_FILENAME = "file_bug_count.json"

FINAL_RESULT_PATH = os.path.join(GLOBAL_PATH, "FINAL RESULTS")
RESULT_CATEGORIES = "categories.json"
RESULT_FILE_COUNT = "file_counts.json"


def find_java_version():
    if not os.path.exists(README_PATH):
        return None

    with open(README_PATH, 'r') as file:
        content = file.read()
        match = re.search(r'\* \{jdk\}\[JDK (\d+)\+\]', content)

        if match:
            return int(match.group(1))
        else:
            return None


def check_jdk_is_installed():
    current_java = find_java_version()

    if os.path.exists(os.path.join(GLOBAL_PATH, f"jdk-{current_java}")):
        return True
    else:
        return False


def get_java_url():
    java8_url = "https://download.java.net/openjdk/jdk8u41/ri/openjdk-8u41-b04-linux-x64-14_jan_2020.tar.gz"
    java9_url = "https://download.java.net/java/GA/jdk9/9/binaries/openjdk-9_linux-x64_bin.tar.gz"
    java11_url = "https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_linux-x64_bin.tar.gz"
    java16_url = "https://download.java.net/openjdk/jdk16/ri/openjdk-16+36_linux-x64_bin.tar.gz"

    java_version = find_java_version()
    if java_version is None:
        raise Exception()

    if java_version == 8:
        return java8_url
    elif java_version == 9:
        return java9_url
    elif java_version == 11:
        return java11_url
    elif java_version == 16:
        return java16_url
    else:
        print("Can't build the project: JAVA version is not 8, 9, 11 or 16")
        raise Exception()


def download_and_extract_java():
    try:
        java_url = get_java_url()
        print("\nDownloading Java...")
        urllib.request.urlretrieve(java_url, "java.tar.gz")

        print("Extracting Java...")
        with tarfile.open("java.tar.gz", "r:gz") as tar:
            tar.extractall(GLOBAL_PATH)

        if find_java_version() == 8:
            os.rename(os.path.join(GLOBAL_PATH, "java-se-8u41-ri"), os.path.join(GLOBAL_PATH, "jdk-8"))
    except Exception as e:
        print("\nException occured: ", e)


def set_environment_variables():
    # Imposta le variabili di ambiente per utilizzare la versione di Java scaricata
    java_dir = os.path.join(GLOBAL_PATH, f"jdk-{find_java_version()}")
    os.environ["JAVA_HOME"] = os.path.abspath(java_dir)
    os.environ["PATH"] = os.path.join(os.path.abspath(java_dir), "bin") + os.pathsep + os.environ["PATH"]
