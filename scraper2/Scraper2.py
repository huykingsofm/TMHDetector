import os
import platform
import sys
import urllib.request
import yaml
from . import elements
import time
from . import scrape_utils
import json

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class Scraper2:
    def __init__(self, 
    email, password, 
    friends_scan_list = None, friends_section = None, friends_elements_path = None, friends_file_names = None,
    about_scan_list = None, about_section = None, about_elements_path = None, about_file_names = None,
    posts_scan_list = None, posts_section = None, posts_elements_path = None, posts_file_names = None,
    sleep_every_page = 3,
    verbose = "print", sender= None ):
        self.__verbose__ = verbose
        if self.__verbose__ == "send":
            if sender is None:
                raise Exception("Expected receiver when verbose = 'send'")

            self.__sender__ = sender

        self.__send_message__(kind = "notify", data = "Initializing......", end = "", level = 0)
        self.__total_scrolls__ = 2500
        self.__current_scrolls__ = 0
        self.__scroll_time__ = 8
        self.__facebook_https_prefix__ = "https://"
        self.__CHROMEDRIVER_BINARIES_FOLDER__ = "bin"
        self.__email__ = email
        self.__password__ = password
        self.__sleep_every_page__ = sleep_every_page


        # FRIENDS DATA
        self.__friends_scan_list__ = scrape_utils.__assign__(friends_scan_list, elements.friends_scan_list)
        self.__friends_section__ = scrape_utils.__assign__(friends_section, elements.friends_section)
        self.__friends_elements_path__ = scrape_utils.__assign__(friends_elements_path, elements.friends_elements_path)
        self.__friends_file_names__ = scrape_utils.__assign__(friends_file_names, elements.friends_file_names)

        # ABOUT DATA
        self.__about_scan_list__ = scrape_utils.__assign__(about_scan_list, elements.about_scan_list)
        self.__about_section__ = scrape_utils.__assign__(about_section, elements.about_section)
        self.__about_elements_path__ = scrape_utils.__assign__(about_elements_path, elements.about_elements_path)
        self.__about_file_names__ = scrape_utils.__assign__(about_file_names, elements.about_file_names)

        # POST DATA
        self.__posts_scan_list__ = scrape_utils.__assign__(posts_scan_list, elements.posts_scan_list)
        self.__posts_section__ = scrape_utils.__assign__(posts_section, elements.posts_section)
        self.__posts_elements_path__ = scrape_utils.__assign__(posts_elements_path, elements.posts_elements_path)
        self.__posts_file_names__ = scrape_utils.__assign__(posts_file_names, elements.posts_file_names)

        self.__send_message__(kind = "notify", data = "Done")

    def __send_message__(self, kind, **kwargs):
        "kind = <notify|progress>"
        if self.__verbose__ in (None, "none"):
            return

        if kind == "notify":
            if "data" not in kwargs:
                raise Exception("Notify must be have data option")

            data = kwargs["data"]

            if "end" not in kwargs:
                end = "\n"
            else:
                end = kwargs["end"]

            if "level" not in kwargs:
                level = None
            else:
                level = kwargs["level"]
        
            kwargs.update({"end":end, "level": level})

        if kind == "progress":
            if "current" not in kwargs:
                raise Exception("Progress must be have current option")

            if "maximum" not in kwargs:
                raise Exception("Progress must be have maximum option")

            current = kwargs["current"]
            maximum = kwargs["maximum"]
            if current > maximum:
                raise Exception("current must be lower than maximum")
                
            kwargs.update({"current": current, "maximum": maximum})
        
        if self.__verbose__ == "print":
            if kind == "notify":
                if level is not None:
                    print("|--" + "----" * level + " ", end = "", flush= True)
                print(data, end = end, flush= True)

            if kind == "progress":
                n = len(str(maximum))
                content = "[{:{}d}/{:{}d}]".format(current, n, maximum, n) + "\b" * (n * 2 + 3)
                print(content, end = "", flush= True)

        if self.__verbose__ == "send":
            message = {"kind" : kind}
            message.update(kwargs)
            message = json.dumps(message).encode()
            self.__sender__.send(message)

    def __extract_and_write_posts__(self, elements, filename):
        try:
            f = open(filename, "w", newline="\r\n")
            f.writelines("TIME              || TYPE          || REACTS || CMTs || IMGs ||" + "\n" + "\n")
            n = len(elements)
            for i, x in enumerate(elements):
                self.__send_message__(kind = "progress", current = i + 1, maximum = n)
                try:
                    title = ""
                    time = ""
                    like = "0"
                    ptype = ""
                    cmt = "0"
                    img = "0"
                    # time--------------------------------------------------------------------------
                    time = scrape_utils.__get_time__(x)
                    #print(time)

                    # reactions and comments--------------------------------------------------------
                    like = scrape_utils.__get_reaction__(x)   
                    cmt = scrape_utils.__get_comment_count__(x, self.__driver__)
                    img = scrape_utils.__get_img_count__(x)

                    # title/type of post-------------------------------------------------------------            
                    try:
                        ptype = x.find_element_by_class_name("_3x-2").find_element_by_class_name("fwb")
                    except Exception:
                        ptype= ""
                        pass

                    try:
                        title = x.find_element_by_xpath(".//div[@class='_1dwg _1w_m _q7o']").find_element_by_class_name("fcg").text
                    except Exception:
                        title = ""

                    if (ptype == ""):                   
                        if (title.find(" at ") != -1):
                            ptype = "check in"
                        else:
                            ptype = "status update"
                    elif (title.find(" memory") != -1):
                        ptype = "shared memory"
                    else:
                        ptype = "shared a post"

                    line = (
                        str(time)
                        + " || "
                        + str(ptype)
                        + " || "
                        + str(like)
                        + " || "
                        + str(cmt)
                        + " || "
                        + str(img)
                        + "\n"
                    )
                    try:
                        f.writelines(line)
                    except Exception:
                        print("Posts: Could not map encoded characters")
                except Exception:
                    pass
            f.close()
        except Exception:
            print("Exception (extract_and_write_posts)", "Status =", sys.exc_info()[0])

        return

    def __save_to_file__(self, name, elements, status):
        try:
            f = None  # file pointer

            if status != "Posts":
                f = open(name, "w", encoding="utf-8", newline="\r\n")

            results = []

            # dealing with Friends
            if status == "Friends":
                # get profile links of friends
                results = [x.get_attribute("href") for x in elements]
                results = [scrape_utils.__create_original_link__(self.__facebook_https_prefix__, url) for url in results]

                # get names of friends
                people_names = [
                    x.find_element_by_tag_name("img").get_attribute("aria-label")
                    for x in elements
                ]

                for i, _ in enumerate(results):
                    # friend's profile link
                    f.writelines(results[i])
                    f.write(",")

                    # friend's name
                    f.writelines(people_names[i])

                    f.write("\n")

            # dealing with About Section
            elif status == "About":
                results = elements[0].text
                f.writelines(results)

            # dealing with Posts
            elif status == "Posts":
                self.__extract_and_write_posts__(elements, name)
                return
                
            f.close()

        except Exception:
            print("Exception (save_to_file)", "Status =", str(status), sys.exc_info()[0])

    def __scroll__(self):
        current_scrolls = 0

        while True:
            try:
                if current_scrolls == self.__total_scrolls__:
                    return

                old_height = self.__driver__.execute_script("return document.body.scrollHeight")
                self.__driver__.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                WebDriverWait(self.__driver__, self.__scroll_time__, 0.05).until(
                    lambda driver: scrape_utils.__check_height__(self.__driver__, old_height)
                )
                current_scrolls += 1
            except TimeoutException:
                break

        return

    def __get_param_for_scrape__(self, status):
        if status == "Friends":
            scan_list = self.__friends_scan_list__
            section = self.__friends_section__
            elements_path = self.__friends_elements_path__
            file_names = self.__friends_file_names__
        
        elif status == "About":
            scan_list = self.__about_scan_list__
            section = self.__about_section__
            elements_path = self.__about_elements_path__
            file_names = self.__about_file_names__

        elif status == "Posts":
            scan_list = self.__posts_scan_list__
            section = self.__posts_section__
            elements_path = self.__posts_elements_path__
            file_names = self.__posts_file_names__
        
        else:
            return None

        return scan_list, section, elements_path, file_names

    def __scrape_data__(self, user_id, status, target_dir):
        page = []

        if status == "Posts":
            page.append(user_id)

        scan_list, section, elements_path, file_names = self.__get_param_for_scrape__(status)

        page += [user_id + s for s in section]

        for i, scan_element in enumerate(scan_list):
            self.__send_message__(kind = "notify", data = "Scraping {}......".format(scan_element), end = "", level= 2)
            try:
                time.sleep(self.__sleep_every_page__)
                self.__driver__.get(page[i])

                if scrape_utils.__check_ban__(self.__driver__):
                    return False

                if (status == "Friends"):
                    sections_bar = self.__driver__.find_element_by_xpath(
                        "//*[@class='_3cz'][1]/div[2]/div[1]"
                    )

                    if sections_bar.text.find(scan_list[i]) == -1:
                        continue

                if status != "About":
                    self.__scroll__()

                data = self.__driver__.find_elements_by_xpath(elements_path[i])
                file_name = os.path.join(target_dir, file_names[i])
                self.__save_to_file__(file_name, data, status)

            except Exception:
                print(
                    "Exception (scrape_data) of {}".format(scan_list[i]),
                    str(i),
                    "Status =",
                    str(status),
                    sys.exc_info()[0],
                )
            finally:
                self.__send_message__(kind = "notify", data = "Done" + " " * 10)
        return True

    def __scrap_profile__(self, fb_id):
        folder = os.path.join(os.getcwd(), "data")
        scrape_utils.__create_folder__(folder)

        self.__driver__.get(fb_id)
        url = self.__driver__.current_url
        user_id = scrape_utils.__create_original_link__(self.__facebook_https_prefix__, url)

        try:
            target_dir = os.path.join(folder, user_id.split("/")[-1])
            scrape_utils.__create_folder__(target_dir)
        except Exception:
            print("Some error occurred in creating the profile directory.")
            return False

        # Nickname and avatar
        self.__scrape_nickname_and_avatar__(target_dir)
    
        #Friends
        self.__send_message__(kind = "notify", data = "Scraping friends......", level= 1)
        ret = self.__scrape_data__(user_id, "Friends", target_dir)
        if ret is False:
            return False
        self.__send_message__(kind = "notify", data = "Scraping friends......Done", level=1)

        #About
        self.__send_message__(kind = "notify", data = "Scraping about......", level= 1)
        ret = self.__scrape_data__(user_id, "About", target_dir)
        if ret is False:
            return False
        self.__send_message__(kind = "notify", data = "Scraping about......Done", level= 1)
        
        # Posts
        self.__send_message__(kind = "notify", data = "Scraping posts......", level= 1)
        ret = self.__scrape_data__(user_id, "Posts", target_dir)
        if ret == False:
            return False
        self.__send_message__(kind = "notify", data = "Scraping posts......Done", level= 1)

        return True

    def __scrape_nickname_and_avatar__(self, target_dir):
        nickname = self.__driver__.find_element_by_class_name("_2nlw").text
        nickname = nickname.split("\n")

        fullname = nickname[0]
        alter = "No alternate name"
        if len(nickname) > 1:
            alter = nickname[1][1:-1]

        avatar = self.__driver__.find_element_by_class_name("_11kf").get_attribute("src")

        filename = os.path.join(target_dir, "Avatar.txt")
        with open(filename, mode = "wt", encoding= "utf-8") as f:
            f.write("NICKNAME AND AVATAR\n")
            f.write("Fullname\n")
            f.write(fullname + "\n")
            f.write("Aternate name\n")
            f.write(alter + "\n")
            f.write("Avatar link\n")
            f.write(avatar)

    def __safe_find_element_by_id__(self, elem_id):
        try:
            return self.__driver__.find_element_by_id(elem_id)
        except NoSuchElementException:
            return None

    def __login__(self, email, password):
        """ Logging into our own profile """
        try:
            options = Options()

            #  Code to disable notifications pop up of Chrome Browser
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-infobars")
            options.add_argument("--mute-audio")
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
            # options.add_argument("headless")  
            try:
                platform_ = platform.system().lower()
                chromedriver_versions = {
                    "linux": os.path.join(
                        os.getcwd(), self.__CHROMEDRIVER_BINARIES_FOLDER__, "chromedriver_linux64",
                    ),
                    "darwin": os.path.join(
                        os.getcwd(), self.__CHROMEDRIVER_BINARIES_FOLDER__, "chromedriver_mac64",
                    ),
                    "windows": os.path.join(
                        os.getcwd(), self.__CHROMEDRIVER_BINARIES_FOLDER__, "chromedriver_win32.exe",
                    ),
                }

                driver = webdriver.Chrome(
                    executable_path=chromedriver_versions[platform_], options=options
                )
            except Exception:
                print(
                    "Kindly replace the Chrome Web Driver with the latest one from "
                    "http://chromedriver.chromium.org/downloads "
                    "and also make sure you have the latest Chrome Browser version."
                    "\nYour OS: {}".format(platform_)
                )
                exit(1)

            fb_path = self.__facebook_https_prefix__ + "facebook.com"
            driver.get(fb_path)
            driver.maximize_window()

            # filling the form
            driver.find_element_by_name("email").send_keys(email)
            driver.find_element_by_name("pass").send_keys(password)

            try:
                # clicking on login button
                driver.find_element_by_id("loginbutton").click()
            except NoSuchElementException:
                # Facebook new design
                driver.find_element_by_name("login").click()

            self.__driver__ = driver
            # if your account uses multi factor authentication
            mfa_code_input = self.__safe_find_element_by_id__("approvals_code")

            if mfa_code_input is None:
                return

            mfa_code_input.send_keys(input("Enter MFA code: "))
            driver.find_element_by_id("checkpointSubmitButton").click()

            # there are so many screens asking you to verify things. Just skip them all
            while self.__safe_find_element_by_id__("checkpointSubmitButton") is not None:
                dont_save_browser_radio = self.__safe_find_element_by_id__("u_0_3")
                if dont_save_browser_radio is not None:
                    dont_save_browser_radio.click()

                driver.find_element_by_id("checkpointSubmitButton").click()

        except Exception:
            print("There's some error when logging in.")
            print(sys.exc_info()[0])
            exit(1)
        print("Login successfully -- {}".format(driver))

    def __call__(self, fb_id):
        self.__send_message__(kind = "notify", data = "Logging in......", end = "", level = 0)
        self.__login__(self.__email__, self.__password__)
        self.__send_message__(kind = "notify", data = "Done", level = None)

        fb_id = self.__facebook_https_prefix__ + "facebook.com/" + fb_id.split("/")[-1]
        
        self.__send_message__(kind = "notify", data = "Scraping data......", level= 0)
        bsuccess = self.__scrap_profile__(fb_id)
        self.__send_message__(kind = "notify", data = "Scraping data......Done", level = 0)
        
        self.__driver__.close()
        return bsuccess


if __name__ == "__main__":
    scrape = Scraper2("0917281911", "huy040999")
    scrape.__CHROMEDRIVER_BINARIES_FOLDER__ = "../bin"
    scrape("huyln99")