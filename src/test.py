from pathlib import Path
import xml.etree.ElementTree as ET

app_name_for_blocking = "hakaramakara"
fileName = "C:\\Users\\hasan\\xf.xml"
file = Path(fileName)

if not file.exists():
    print("Configuration file does not exist")
else:
    tree = ET.parse(fileName)
    root = tree.getroot()

    element = root.find("./property/[@name='applications']")
    if element is None:
        print("applications element could not be found.")
    else:
        element = root.find("./property/property[@name='muted_applications']")
        if element is None:
            print("muted_applications element could not be found.")
            print("adding muted_applications element to applications element.")
            element = root.find("./property/[@name='applications']")
            new_element = ET.SubElement(element, 'property')
            new_element.attrib["name"] = 'muted_applications'
            new_element.attrib["type"] = 'array'
            tree.write(fileName)
        else:
            print("muted_applications element exists.")

        print("checking if '" + app_name_for_blocking + "' exists in muted_applications element.")
        element = root.find("./property/property[@name='muted_applications']/value[@value='{0}']".format(app_name_for_blocking))
        if element is None:
            print("'" + app_name_for_blocking + "' is not found in muted_applications element.")
            print("'" + app_name_for_blocking + "' will be added to muted_applications element.")
            element = root.find("./property/property[@name='muted_applications']")
            new_element = ET.SubElement(element, 'value')
            new_element.attrib["type"] = 'string'
            new_element.attrib["value"] = app_name_for_blocking
            tree.write(fileName)
        else:
            print("'" + app_name_for_blocking + "' is already added to muted_applications element.")