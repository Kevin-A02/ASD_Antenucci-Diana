import os

from install_spotbugs import install_spotbugs
from utils import PROJECT_PATH, GRADLEW_PATH, SPOTBUGS_PATH, XML_FILE_PATH, BUILD_PATH, REPORT_DIR


def check_gradlew():
    if not os.path.exists(GRADLEW_PATH):
        print(f"Can't build this version of groovy due to missing gradlew")
        return False
    return True


def check_plugin():
    plugin_name = 'spotbugsPlugins'
    if not os.path.exists(os.path.join(PROJECT_PATH, "build.gradle")):
        return False

    with open(os.path.join(PROJECT_PATH, "build.gradle"), 'r') as file:
        data = file.read()
        if plugin_name in data:
            return True
        return False


def add_plugin_config():
    spotbugs_command = """
    spotbugs {
    showStackTraces = true
    showProgress = true
    reportsDir = file("$buildDir/reports/spotbugs")
    excludeFilter = file('config/spotbugs/exclude.xml')
    }
    
    spotbugsMain {
        reports {
            xml.enabled = true
            html.enabled = false
        }
    }"""

    with open(os.path.join(PROJECT_PATH, "build.gradle"), 'a') as file:
        file.write(spotbugs_command)


def spotbugs(param):
    print("\nSPOTBUGS PLUGIN STARTED")
    done = spotbugs_plugin(param)
    if not done:
        print("SPOTBUGS PLUGIN FAILED")
        print("\nSPOTBUGS STANDALONE STARTED")
        done = spotbugs_bin(param)
        if not done:
            print("\nSPOTBUGS STANDALONE FAILED")
    return done


def spotbugs_plugin(param):
    try:
        if not check_gradlew():
            return False

        if not check_plugin():
            return False
        add_plugin_config()

        print("\nBuilding groovy")
        command = f"{GRADLEW_PATH} -p {PROJECT_PATH} spotbugsMain {param}"

        return_code = os.system(command)
        if return_code == 0:
            print('Analysis done')
            return True
        else:
            print(f'Error executing command. Return code: {return_code}')
            raise Exception()
    except Exception as e:
        print(e)
        return False


def check_spotbugs_bin():
    if not os.path.exists(SPOTBUGS_PATH):
        print("Standalone spotbugs is not present...")
        install_spotbugs()
        os.system(f"chmod +x {SPOTBUGS_PATH}")


def build_jar(param):
    gradlew_path = os.path.join(PROJECT_PATH, "gradlew")

    print("\nBuilding groovy")
    return_code = os.system(f"{gradlew_path} -p {PROJECT_PATH} clean dist {param}")
    if return_code == 0:
        print("BUILD DONE")
        return True
    else:
        print("BUILD FAILED")
        return False


def spotbugs_bin(param):
    try:
        jar_built = build_jar(param)
        if not jar_built:
            return False

        check_spotbugs_bin()
        os.makedirs(REPORT_DIR, exist_ok=True)
        command = f'{SPOTBUGS_PATH} -maxHeap 4096 -jvmArgs "-XX:+UseParallelGC" -xml={XML_FILE_PATH} -textui {BUILD_PATH} {param}'
        return_code = os.system(command)
        if not return_code == 0:
            raise Exception()

        print('Analysis done')
        return True
    except:
        print(f'Analysys Failed\n')
        return False
