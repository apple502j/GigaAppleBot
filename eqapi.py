import requests

def geteqapi():
    return requests.get("https://api.p2pquake.net/v1/human-readable?limit=1").json()[0]

eq2level = {
    0:"震度0",
    10:"震度1",
    20:"震度2",
    30:"震度3",
    40:"震度4",
    45:"震度5弱",
    46:"震度5弱以上(データなし)",
    50:"震度5強",
    55:"震度6弱",
    60:"震度6強",
    65:"震度7",
    "不明":"不明"
    }

infos = {
    "ScalePrompt":"震度速報",
    "Destination":"震源情報",
    "Foreign":"遠地地震",
    "ScaleAndDestination":"震源震度情報",
    "DetailScale":"地震情報",
    "Other":"不明な情報"
    }

tinfos = {
    "MajorWarning":"大津波警報",
    "Warning":"津波警報",
    "Watch":"津波注意報",
    "Unknown":"不明"
    }

tsunamidic = {
    "None":"なし",
    "Unknown":"不明",
    "Checking":"調査中",
    "NonEffective":"若干の海面変動[被害の心配なし]",
    "Watch":"津波注意報",
    "Warning":"津波情報を発表中!",
    "調査中":"調査中"
    }

def getcolor(i):
    FF = 16711680
    return round(FF * (i/65))

class EqData(object):
    def __init__(self,infotype, time,
                 hypo, maxscale,
                 tsunami, points):
        self.infotype=infotype
        self.time = time
        self.hyponame = "不明"
        self.lat = "N0.0"
        self.long = "E0.0"
        self.depth = "不明"
        self.mag = "不明"
        self.tsunami = "調査中"
        self.maxScale = "不明"
        self.points = []
        if infotype == "ScalePrompt":
            self.maxscale = maxscale
            self.points = points
        if infotype == "Destination" or infotype == "Foreign":
            hyponame = hypo["name"]
            lat = hypo["latitude"]
            long = hypo["longitude"]
            depth = hypo["depth"]
            mag = hypo["magnitude"]
            self.hyponame = hyponame
            self.lat = lat
            self.long = long
            self.depth = depth
            self.mag = mag
            self.tsunami = tsunami
        if infotype == "ScaleAndDestination" or infotype == "DetailScale":
            hyponame = hypo["name"]
            lat = hypo["latitude"]
            long = hypo["longitude"]
            depth = hypo["depth"]
            mag = hypo["magnitude"]
            self.maxScale = maxscale
            self.maxscale = maxscale
            self.points = points
            self.hyponame = hyponame
            self.lat = lat
            self.long = long
            self.depth = depth
            self.mag = mag
            self.tsunami = tsunami
        return

class Tsunami(object):
    def __init__(self, cancel, areas):
        self.cancel = cancel
        self.areas = []
        if not cancel:
            self.areas = areas
        return

def parseapi(dic):
    if dic["code"]==551:
        return EqData(
            dic["issue"]["type"],
            dic["earthquake"]["time"],
            dic["earthquake"].get("hypocenter",""),
            dic["earthquake"].get("maxScale",""),
            dic["earthquake"].get("domesticTsunami",""),
            dic.get("points","")
            )
    elif dic["code"]==552:
        return Tsunami(
            dic["canceled"],
            dic.get("areas", "")
            )
    else:
        return None
