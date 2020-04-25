from Tcp import Tcp
import json
from scraper2.Scraper2 import Scraper2 
import yaml
from dataprocessing.DataProcessing import DataProcessing
from sklearn.ensemble import RandomForestClassifier
import pickle
from dataprocessing.convertor import Convertor
import pandas as pd

def load(filename):
    with open(filename, mode= "rb") as f:
        return pickle.load(f)

def __test__(dp, model, fbid):
    convertor = Convertor("data")
    profile = convertor.read_profile(fbid)
    profile = pd.DataFrame([profile])

    datapreprocessing = load(dp)
    
    profile = datapreprocessing.convert(profile)

    randomforest = load(model)
    
    result = randomforest.predict_proba(profile)[0]
    print(result)

def __solver__(conn, addr, data, **kwargs):
    data = json.loads(data)

    if "server" not in kwargs:
        raise Exception("Expected server parameter")
    
    server = kwargs["server"]

    if "fb_id" in data:
        while True:
            email = server.__email__[server.__current_account__]
            password = server.__password__[server.__current_account__]
            try:
                scraper = Scraper2(email, password, verbose= "send", sender= conn)
                bSuccess = scraper(data["fb_id"])
            except Exception as e:
                print(str(e))
                scraper.__driver__.close()
                conn.close()
                return

            if bSuccess:
                break
            content = json.dumps({
                "kind": "notify", 
                "data": "Error in crawling, restart crawling...", 
                "level": None, 
                "end": "\n"
                })
            conn.send(content.encode())
            server.__current_account__ = (server.__current_account__ + 1) % len(server.__email__) 

    
    content = json.dumps({"kind": "notify", "data": "Converting crawled data to vector......", "level": 0, "end": ""})
    conn.send(content.encode())

    convertor = Convertor("data")
    profile = convertor.read_profile(data["fb_id"].split("/")[-1])
    profile = pd.DataFrame([profile])

    content = json.dumps({"kind": "notify", "data": "Done", "level": None, "end": "\n"})
    conn.send(content.encode())

    datapreprocessing = load("pkg/DataPreprocessingremove.dp")
    
    content = json.dumps({"kind": "notify", "data": "Preprocessing data......", "level": 0, "end": ""})
    conn.send(content.encode())
    
    profile = datapreprocessing.convert(profile)

    content = json.dumps({"kind": "notify", "data": "Done", "level": None, "end": "\n"})
    conn.send(content.encode())

    randomforest = load("pkg/overRandomForestremove.model")
    
    content = json.dumps({"kind": "notify", "data": "Predicting using Random forest......", "level": 0, "end": ""})
    conn.send(content.encode())
    
    result = randomforest.predict_proba(profile)[0][0] > 0.6

    content = json.dumps({"kind": "notify", "data": "Done", "level": None, "end": "\n"})
    conn.send(content.encode())

    result = "real" if result == True else "fake"

    content = json.dumps({"kind": "result", "data": result, "level": None, "end": "\n"})
    conn.send(content.encode())
    
    conn.close()

class DetectorServer:
    def __init__(self, credential = "credentials.yaml"):
        with open(credential, mode = "r") as yamlfile:
            cfg = yaml.safe_load(stream= yamlfile)

        self.__email__ = []
        self.__password__ = []
        for i in range(100):
            if "email{}".format(i) in cfg and "password{}".format(i) in cfg:
                self.__email__.append(cfg["email{}".format(i)])
                self.__password__.append(cfg["password{}".format(i)])

        if len(self.__email__) == 0:
            raise Exception("Must provide at least 1 account")

        if "ip" not in cfg or "port" not in cfg:
            raise Exception("Must provide ip and port of server")

        self.__server__ = Tcp.TcpServer(cfg["ip"], cfg["port"], __solver__)
        self.__server__.__email__ = self.__email__
        self.__server__.__password__ = self.__password__
        self.__server__.__current_account__ = 0

    def start(self):
        self.__server__.start_listen()
        while not self.__server__.__stop__:
            pass

if __name__ == "__main__":
    server = DetectorServer()
    server.start()