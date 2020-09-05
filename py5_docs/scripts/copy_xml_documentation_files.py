import os
import stat
import shutil
from pathlib import Path

import pandas as pd


NEW_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<root>
<name>{0}</name>

<category></category>

<subcategory></subcategory>

<type>{1}</type>

<example>
<image></image>
<code><![CDATA[
]]></code>
</example>

<description><![CDATA[
Missing Description
]]></description>

</root>
"""

PROCESSING_API_EN = Path('/home/jim/Projects/ITP/pythonprocessing/processing-docs/content/api_en/')
PY5_API_EN = Path('py5_docs/Reference/api_en/')

PY5_CLASS_LOOKUP = {
    'PApplet': 'Sketch',
    'PFont': 'Py5Font',
    'PGraphics': 'Py5Graphics',
    'PImage': 'Py5Image',
    'PShader': 'Py5Shader',
    'PShape': 'Py5Shape',
    'PSurface': 'Py5Surface',
}


# read the class datafiles so I know what methods and fields are relevant
class_data_info = dict()
class_resource_data = Path('py5_resources', 'data')
for pclass in PY5_CLASS_LOOKUP.keys():
    filename = 'py5applet.csv' if pclass == 'PApplet' else pclass.lower() + '.csv'
    class_data = pd.read_csv(class_resource_data / filename)
    class_data = class_data.fillna('').set_index('processing_name')
    class_data_info[pclass] = class_data.query("available_in_py5==True")


# go through the class data info and for each relevant method and field
# for each find the xml documentation file or note new files that must be created
xml_files = []
new_xml_files = []
for pclass, class_data in class_data_info.items():
    for processing_name, data in class_data.iterrows():
        item_type = data['type']
        if item_type in ['static field', 'unknown']:
            # skip, we don't care
            continue
        py5_name = data['py5_name']
        if not processing_name:
            # definitely a new function I need to document
            new_xml_files.append((pclass, py5_name, item_type))
            continue

        # first try the correct documentation filename
        if pclass == 'PApplet':
            name = f'{processing_name}.xml'
        else:
            name = f'{pclass}_{processing_name}.xml'
        if processing_name == 'hint':
            xml_file = PROCESSING_API_EN / 'include' / name
        else:
            xml_file = PROCESSING_API_EN / name
        if xml_file.exists():
            # documentation exists, copy
            xml_files.append((xml_file, (pclass, py5_name, processing_name)))
            continue

        # usable documentation might be in a different file because of inheritance
        if pclass in ['PApplet', 'PGraphics', 'PImage']:
            for prefix in ['', 'PGraphics_', 'PImage_']:
                if processing_name == 'hint':
                    xml_file = PROCESSING_API_EN / 'include' / f'{prefix}{processing_name}.xml'
                else:
                    xml_file = PROCESSING_API_EN / f'{prefix}{processing_name}.xml'
                if xml_file.exists():
                    break
        if xml_file.exists():
            # documentation exists, and should have already been copied
            continue

        # new documentation that I must write. skip pgraphics so I don't duplicate work
        if pclass != 'PGraphics':
            new_xml_files.append((pclass, py5_name, item_type, processing_name))


# copy the relevant xml files to the py5 directory
for xml_file, file_data in xml_files:
    pclass, py5_name, processing_name = file_data
    new_filename = f'{PY5_CLASS_LOOKUP[pclass]}_{py5_name}.xml'
    # TODO: add extra metadata and Pythonize the code example
    # TODO: should I and can I convert to a different format like yaml or toml? I can't do json
    # TODO: add underlying processing field or method to metadata because I want to mention this in the documentation
    shutil.copy(xml_file, PY5_API_EN / new_filename)
    permissions = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH
    os.chmod(PY5_API_EN / new_filename, permissions)

for new_file_data in new_xml_files:
    pclass, py5_name, item_type, *_ = new_file_data
    with open(PY5_API_EN / f'{PY5_CLASS_LOOKUP[pclass]}_{py5_name}.xml', 'w') as f:
        name = py5_name if item_type == 'dynamic variable' else py5_name + '()'
        f.write(NEW_TEMPLATE.format(name, item_type))

print(f'copied {len(xml_files)} files and created {len(new_xml_files)} new files.')


# generate docstrings using these xml descriptions with html removed and other info on parameters and signatures taken from other data files
# later, generate processing-like docs using all the xml files by learning from the existing process
# use the xml files to make rst files that I can then use in a nikola website
