from pyzotero import zotero
from dotenv import load_dotenv
import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from config import ZOTERO_CONFIG

zot = zotero.Zotero(ZOTERO_CONFIG.get("user"), ZOTERO_CONFIG.get("type"), ZOTERO_CONFIG.get("api_key"))
first_ten = zot.items(limit=10)

url = first_ten[0]['data']['url']
abstract = first_ten[0]['data']['abstractNote']
print(url)
print(abstract)