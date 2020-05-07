from Tcp import Tcp
import json
from scraper2.Scraper2 import Scraper2, scrape_utils
import yaml
from DataProcessing import DataProcessing
from sklearn.ensemble import RandomForestClassifier
import pickle
from convertor import Convertor
import pandas as pd
import os

def load(filename):
    "Load a object which is dumped in a file with pickle"
    with open(filename, mode= "rb") as f:
        return pickle.load(f)

def __test__(dp, model, fbid):
    "Using for quick test a crawled account"

    # Create a convertor and convert files in a account to vector
    convertor = Convertor("data")
    profile = convertor.read_profile(fbid)
    profile = pd.DataFrame([profile])

    # Load datapreprocessing object and nomalizing vector
    datapreprocessing = load(dp)    
    profile = datapreprocessing.convert(profile)

    # Load model and predict result
    randomforest = load(model)
    result = randomforest.predict_proba(profile)[0]

    print(result)

def __solver__(conn, addr, data, **kwargs):
    "Resolve a package 'data' come from client"

    # Change data from string to json
    data = json.loads(data)

    # Get parameter server
    if "server" not in kwargs:
        raise Exception("Expected server parameter")
    server = kwargs["server"]

    # Solve data have key fb_id
    if "fb_id" in data:
        fb_id = scrape_utils.__create_original_link__("https://", data["fb_id"])
        while True:
            # Get email and password from server object
            email = server.__email__[server.__current_account__]
            password = server.__password__[server.__current_account__]

            # Create scraper and start scraping facebook account
            try:
                scraper = Scraper2(email, password)
                bSuccess = scraper(data["fb_id"])
            except Exception as e:
                print(str(e))
                scraper.__driver__.close()
                return

            # Not success if the crawler account is banned
            if bSuccess:
                break
            content = json.dumps({
                "kind": "notify", 
                "data": "Error in crawling, restart crawling...", 
                "level": None, 
                "end": "\n"
                })
            print(content.encode())

            # Switch account
            server.__current_account__ = (server.__current_account__ + 1) % len(server.__email__) 

    
        content = json.dumps({"kind": "notify", "data": "Converting crawled data to vector......", "level": 0, "end": ""})
        print(content.encode())

        # Create convertor and convert crawled data to vector
        convertor = Convertor("data")
        profile = convertor.read_profile(fb_id.split("/")[-1])
        profile = pd.DataFrame([profile])

        content = json.dumps({"kind": "notify", "data": "Done", "level": None, "end": "\n"})
        print(content.encode())
        
        content = json.dumps({"kind": "notify", "data": "Preprocessing data......", "level": 0, "end": ""})
        print(content.encode())
        
        # Load datapreprocessing object and normalizing vector
        datapreprocessing = load("pkg/DataPreprocessingremove.dp")
        profile = datapreprocessing.convert(profile)

        content = json.dumps({"kind": "notify", "data": "Done", "level": None, "end": "\n"})
        print(content.encode())
        
        content = json.dumps({"kind": "notify", "data": "Predicting using Random forest......", "level": 0, "end": ""})
        print(content.encode())
        
        # Load model and predict result
        randomforest = load("pkg/overRandomForestremove.model")
        result = randomforest.predict_proba(profile)[0][0] > 0.6

        content = json.dumps({"kind": "notify", "data": "Done", "level": None, "end": "\n"})
        print(content.encode())

        result = "real" if result == True else "fake"

        folder = os.path.join(os.getcwd(), "data")
        target_dir = os.path.join(folder, fb_id.split("/")[-1])
        filename = os.path.join(target_dir, "result.txt")
        with open(filename, mode = "w") as f:
            f.write(result)

        content = json.dumps({"kind": "result", "data": result, "level": None, "end": "\n"})
        print(content.encode())

        conn.close()

class DetectorServer:
    def __init__(self, credential = "credentials.yaml"):
        "Load all email, password for crawling and ip, port for server"
        with open(credential, mode = "r") as yamlfile:
            cfg = yaml.safe_load(stream= yamlfile)

        self.__email__ = []
        self.__password__ = []
        for i in range(100):
            if "email{}".format(i) in cfg and "password{}".format(i) in cfg:
                if cfg["email{}".format(i)] == None or cfg["password{}".format(i)] == None:
                    continue
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