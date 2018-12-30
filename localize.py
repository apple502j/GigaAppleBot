import json
import os

AVAILABLE = []
TRDATA = {}
ULANG = {}
def update():
    global TRDATA
    global AVAILABLE
    langs=list(map(lambda name:name.replace(".json",""), filter(lambda name:name.endswith(".json"),os.listdir("./i18n"))))
    AVAILABLE=langs.copy()
    for p in langs:
        path=f"./i18n/{p}.json"
        with open(path, encoding="utf-8") as f:
            TRDATA[p]=json.load(f)

def getlocale(uid):
    global ULANG
    uid=str(uid)
    with open("userdata.json", "r", encoding="utf-8") as f:
        ULANG=json.load(f)
    return ULANG.get(uid, "ja")

def setlocale(uid, l):
    global ULANG
    uid=str(uid)
    getlocale(uid) # Update the list
    ULANG[uid]=l
    with open("userdata.json","w", encoding="utf-8") as f:
        json.dump(ULANG, f)

def _(tid, uid, *args, dft=None):
    uid=str(uid)
    locale=getlocale(uid)
    try:
        return TRDATA[locale][tid].format(*args)
    except:
        if dft:
            return dft.format(*args)
        try:
            return TRDATA["ja"][tid].format(*args)
        except:
            raise Exception("Language missing for {0}".format(tid))
