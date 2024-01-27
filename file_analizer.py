import os
import xml.etree.ElementTree as ET

from utils import XML_FILE_NAME


def analyze_spotbugs_results(xml_file_path, bug_categories_counter, file_bug_count):
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        for bug_instance in root.iter('BugInstance'):
            # Ottieni la categoria del bug
            category = bug_instance.attrib.get('category')
            bug_categories_counter[category] += 1

            # Ottieni il file associato al bug
            class_element = bug_instance.find('.//Class')
            source_file = class_element.find('.//SourceLine').attrib.get('sourcepath')
            file_bug_count[source_file] += 1
    except Exception as e:
        print(e)
        return [], []

    os.remove(XML_FILE_NAME)
    return bug_categories_counter, file_bug_count
