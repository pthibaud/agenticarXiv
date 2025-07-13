from pyzotero import zotero
from dotenv import load_dotenv
import requests
from lxml import html
#from seleniumbase import SB
from bs4 import BeautifulSoup
from progress.bar import ChargingBar
import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from config import ZOTERO_CONFIG

zot = zotero.Zotero(ZOTERO_CONFIG.get("user"), ZOTERO_CONFIG.get("type"), ZOTERO_CONFIG.get("api_key"))
first_ten = zot.items(limit=100)

print(first_ten[69]['data'])
quit()

bar = ChargingBar('Processing', max=100)
for index, entry in enumerate(first_ten):
    #doi = entry['data']['DOI']  
    if "data" in entry and "abstractNote" in entry["data"] and "url" in entry["data"]:
        url = entry['data']['url']
        abstract = entry['data']['abstractNote']
        if url.find("link.aps.org") != -1 and abstract == "":
            #xml_content = requests.get(url+"#abstract").content
            new_url = url.replace("https://link.aps.org/doi/","https://harvest.aps.org/v2/journals/articles/")
            #print(url,new_url)
            xml_content = requests.get(new_url).json()
            if xml_content.get("data") is not None:
                aps_abstract=BeautifulSoup(xml_content["data"]["abstract"]["value"],"html.parser")
                print("For url:",url)
                print("original abstract:",abstract)
                print("new abstract:", aps_abstract.get_text())
                print("-"*80)
    bar.next()
bar.finish()
        #print(xml_content["data"]["abstract"]["value"])
        #abstract_xpath = '//*[@id="page-content"]/div[3]/div[2]/div[1]/div/p/text()'
        #abstract_xpath = '//*[@id="abstract-section-content"]/p/text()[1]'
        #aps_abstract = xml_content.xpath(abstract_xpath)
        #print(aps_abstract)
        #iop_abstract = xml_content.xpath(abstract_xpath)
        #xml_content = requests.get(url+"#artAbst").content
        #print(xml_content)
        #print(doi,"::",url+"#artAbst","::",abstract)
    