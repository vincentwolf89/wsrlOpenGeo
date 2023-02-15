from qgis.core import *
from qgis.gui import *

import requests

@qgsfunction(args='auto', group='Custom', referenced_columns=[])
def link_check(url, feature, parent):
    try:
        r = requests.head(url,verify=False,timeout=5)
        if r.status_code == 404:
            return "Geen pdf beschikbaar"
        else:
            return url
       
    except:
        return 'foutje'