import requests
import urllib3
import re
from bs4 import BeautifulSoup
import json

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
try:
    requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
except AttributeError:
    # no pyopenssl support used / needed / available
    pass
url = "https://www.biznes.gov.pl/en/classification-pkd-code"
response = requests.get(url, verify=False)

soup = BeautifulSoup(response.content, 'html.parser')

classes_texts = [
    class_.find('a').text
    for class_ in
    soup.findAll('li', {'class': 'listPkd-fourth', 'data-level': '4'})
]

classes_texts_dict = {}
for class_text in classes_texts:
    match_number = re.match(r"Class ([0-9.]*)", class_text)
    class_number = int(match_number.group(1).replace('.', ''))
    match_name = re.search(r"(\w*) - ([\w -]*)", class_text)
    class_name = match_name.group(2)
    classes_texts_dict[class_number] = class_name

with open("PKDMainClassName.json", "w") as f:
    f.write(json.dumps(classes_texts_dict, indent=4))
