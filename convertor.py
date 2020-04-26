import os
import pandas as pd
import dateutil.parser as parser
import dateutil
import datetime

def check_file(filename):
    return os.path.exists(filename)

class Convertor:
    def __init__(self, parent):
        self.parent = parent

    def has_url(self, folder: str):
        if folder.isdecimal():
            return {"has_url": False}
        else:
            return {"has_url": True}

    def __read_About__(self, folder, atype, fieldnames, exception):
        filename = os.path.join(self.parent, folder, "{}.txt".format(atype))
        ret = {}
        for fieldname in fieldnames:
            ret[fieldname] = 0

        if check_file(filename) is False:
            return ret

        with open(filename, "rt", encoding= "utf-8") as f:
            flag = -1
            FIELD = [[]] * len(fieldnames)
            for line in f:
                line = line.replace("\n", "")
                for i, fieldname in enumerate(fieldnames):
                    if fieldname in line:
                        flag = i
                FIELD[flag].append(line)
            
            for i, _ in enumerate(fieldnames):
                FIELD[i] = FIELD[i][1:]

        for i, fieldname in enumerate(fieldnames):
            if exception[i] is "":
                if len(FIELD[i]) is not 0:
                    ret[fieldname] = 1
                else:
                    continue

            if exception[i] not in FIELD[i]:
                ret[fieldname] = 1

        return ret

    def read_Abouts(self, folder):
        fieldnames = ["WORK", "EDUCATION"]
        exception = [
            'No workplaces to show',
            'No schools/universities to show'
        ]
        ret = self.__read_About__(folder, "Work and Education", fieldnames, exception)

        fieldnames = ["ABOUT", "FAVOURITE QUOTES"]
        exception = [
            "No additional details to show",
            'No favourite quotes to show'
        ]
        ret.update(self.__read_About__(folder, "Details About", fieldnames, exception))

        fieldnames = ["RELATIONTSHIP", "FAMILY MEMBERS"]
        exception = [
            "No relationship info to show",
            'No family members to show'
        ]
        ret.update(self.__read_About__(folder, "Family and Relationships", fieldnames, exception))

        fieldnames = ["CURRENT CITY AND HOME TOWN"]
        exception = [
            "No places to show",
        ]
        ret.update(self.__read_About__(folder, "Places Lived", fieldnames, exception))

        fieldnames = ["CONTACT INFO", "BASIC INFO"]
        exception = [
            "No contact info to show",
            "No basic info to show"
        ]
        ret.update(self.__read_About__(folder, "Contact and Basic Info", fieldnames, exception))

        fieldnames = ["LIFE EVENTS"]
        exception = [""]
        ret.update(self.__read_About__(folder, "Life Events", fieldnames, exception))

        return ret

    def __read_Friends__(self, folder, ftype):
        filename = os.path.join(self.parent, folder, "{}.txt".format(ftype))
        if check_file(filename) is False:
            return None

        FRIENDS = 0
        with open(filename, "rt" , encoding= "utf-8") as f:
            data = f.read()
        
        FRIENDS = data.count(",") // 2
            
        return FRIENDS

    def read_Friends(self, folder):
        friendtype = [ 
            "Followers",
            "Following",
            "All Friends",
            "College Friends",
            "Current City Friends",
            "Work Friends",
            "Hometown Friends"]

        friends = {}
        for t in friendtype:
            friends[t] = self.__read_Friends__(folder, t)
        return friends
    def read_Posts(self, folder):
        filename = os.path.join(self.parent, folder, "Posts.txt")
        if check_file(filename) is False:
            return None
        
        status_text = ["check in", "status update", "shared memory", "shared a post"]
        status_count = [0] * (len(status_text) + 1)
        CMTs = 0
        LIKEs = 0
        IMGs = 0
        
        MAX_CMTs = 0
        MAX_LIKEs = 0
        MAX_IMGs = 0

        MIN_CMTs = 99999999
        MIN_LIKEs = 99999999
        MIN_IMGs = 99999999

        exist_profile = False
        LAST_INTERVAL = None
        OLD_TIME = datetime.datetime.now()
        SUM_INTERVAL = 0
        MAX_INTERVAL = 0
        MIN_INTERVAL = 99999999

        with open(filename, "rt") as f:
            for line in f:
                if "TIME" in line:
                    exist_profile = True
                    continue

                status = line.split("||")
                try:
                    if len(status) == 1:
                        raise Exception()

                    if LAST_INTERVAL is None:
                        t = parser.parse(status[0], dayfirst = True)
                        LAST_INTERVAL = (OLD_TIME - t).days

                    other = True
                    for idx, text in enumerate(status_text):
                        if text in status[1]:
                            status_count[idx] += 1
                            other = False
                    if other:
                        status_count[-1] += 1
                    
                    CMTs = int(status[2])
                    LIKEs = int(status[3])
                    IMGs = int(status[4])

                    MAX_CMTs = CMTs if MAX_CMTs < CMTs else MAX_CMTs
                    MAX_LIKEs = CMTs if MAX_LIKEs < LIKEs else MAX_LIKEs
                    MAX_IMGs = CMTs if MAX_IMGs < IMGs else MAX_IMGs

                    MIN_CMTs = CMTs if MIN_CMTs > CMTs else MIN_CMTs
                    MIN_LIKEs = CMTs if MIN_LIKEs > LIKEs else MIN_LIKEs
                    MIN_IMGs = CMTs if MIN_IMGs > IMGs else MIN_IMGs

                    POST_TIME = parser.parse(status[0], dayfirst = True)
                    SUM_INTERVAL += (OLD_TIME - POST_TIME).days
                    if (OLD_TIME - POST_TIME).days > MAX_INTERVAL:
                        MAX_INTERVAL = (OLD_TIME - POST_TIME).days
                    
                    if (OLD_TIME - POST_TIME).days < MIN_INTERVAL:
                        MIN_INTERVAL = max((OLD_TIME - POST_TIME).days, 0)

                    OLD_TIME = POST_TIME
                except:
                    pass

        if not exist_profile:
            raise Exception("Error profile")

        ret = {}
        for i, text in enumerate(status_text):
            ret.update({text.upper(): status_count[i]})
        
        ret.update({"OTHERS": status_count[-1]})

        ret.update({"CMTS": CMTs})
        ret.update({"LIKES": LIKEs})
        ret.update({"IMGS": IMGs})

        if sum(status_count) == 0:
            MIN_CMTs = 0
            MIN_IMGs = 0
            MIN_LIKEs = 0

        ret.update({"MAX_CMTS": MAX_CMTs})
        ret.update({"MAX_LIKES": MAX_LIKEs})
        ret.update({"MAX_IMGS": MAX_IMGs})

        ret.update({"MIN_CMTS": MIN_CMTs})
        ret.update({"MIN_LIKES": MIN_LIKEs})
        ret.update({"MIN_IMGS": MIN_IMGs})

        if sum(status_count) is 0:
            AVG_INTERVAL = (datetime.datetime.now() - parser.parse("1/1/2012")).days
            MIN_INTERVAL = AVG_INTERVAL
            MAX_INTERVAL = AVG_INTERVAL
        else:
            AVG_INTERVAL = SUM_INTERVAL / sum(status_count)

        ret.update({"AVG_INTERVAL": AVG_INTERVAL})
        ret.update({"MAX_INTERVAL": MAX_INTERVAL})
        ret.update({"MIN_INTERVAL": MIN_INTERVAL})       
        ret.update({"LAST_INTERVAL": LAST_INTERVAL})


        return ret

    def read_profile(self, folder):
        profile = {"ID": "id_{}".format(folder)}
        profile.update(self.read_Abouts(folder))
        profile.update(self.read_Friends(folder))
        profile.update(self.read_Posts(folder))
        profile.update({"FB_TYPE": None})
        profile.update({"FB_LINK": "https://www.facebook.com/{}".format(folder)})

        return profile

    def read(self, old_profiles = None):
        if old_profiles is not None:
            ret = old_profiles.to_dict("records")
            old_id = old_profiles["ID"].tolist()
        else:
            ret = []
            old_id = None

        with os.scandir(self.parent) as entries:
            for entry in entries:
                if old_id is not None and "id_{}".format(entry.name) in old_id:
                    continue

                try:
                    profile = self.read_profile(entry.name)
                except Exception as e:
                    print(entry.name, e)
                    continue

                ret.append(profile)

        return ret

    def __call__(self, csv):
        old_profiles = None
        try:
            old_profiles = pd.read_csv(csv).iloc[:, 1:]
        except:
            pass

        profiles = self.read(old_profiles)

        profiles = pd.DataFrame(profiles)
        profiles.to_csv(csv)

if __name__ == "__main__":
    convertor = Convertor("data")
    d = [convertor.read_profile("huyln99")]
    print(pd.DataFrame(d))