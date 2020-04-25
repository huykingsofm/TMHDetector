import os
import calendar

from selenium.webdriver.support.ui import WebDriverWait

def __create_folder__(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)

def __create_original_link__(prefix, url):
    if url.find(".php") != -1:
        original_link = prefix + ".facebook.com/" + ((url.split("="))[1])

        if original_link.find("&") != -1:
            original_link = original_link.split("&")[0]

    elif url.find("fnr_t") != -1:
        original_link = (
            prefix
            + ".facebook.com/"
            + ((url.split("/"))[-1].split("?")[0])
        )
    elif url.find("_tab") != -1:
        original_link = (
            prefix
            + ".facebook.com/"
            + (url.split("?")[0]).split("/")[-1]
        )
    else:
        original_link = url

    return original_link

def __assign__(var, default):
    if var is None:
        return default
    return var

__ban_text__ = "We limit"
def __check_ban__(driver):
    try:
        text = driver.find_element_by_class_name("phl").text
        if ban_text in text:
            return True
        return False
    except:
        return False

def __check_height__(driver, old_height):
    new_height = driver.execute_script("return document.body.scrollHeight")
    return new_height != old_height

def get_div_links(x, tag):
    try:
        temp = x.find_element_by_xpath(".//div[@class='_3x-2']")
        return temp.find_element_by_tag_name(tag)
    except Exception:
        return ""


def __get_title_links__(title):
    l = title.find_elements_by_tag_name("a")
    return l[-1].text, l[-1].get_attribute("href")


def __get_title__(x):
    title = ""
    try:
        title = x.find_element_by_xpath(".//span[@class='fwb fcg']")
    except Exception:
        try:
            title = x.find_element_by_xpath(".//span[@class='fcg']")
        except Exception:
            try:
                title = x.find_element_by_xpath(".//span[@class='fwn fcg']")
            except Exception:
                pass
    finally:
        return title


def __get_time__(x):
    t = ""
    try:
        t = x.find_element_by_tag_name("abbr").get_attribute("title")

        t = (
            str("%02d" % int(t.split(", ")[1].split()[1]),)
            + "-"
            + str(("%02d" % (int((list(calendar.month_abbr).index(t.split(", ")[1].split()[0][:3]))),)))
            + "-"
            + t.split()[3]
            + " "
            + str("%02d" % int(t.split()[5].split(":")[0]))
            + ":"
            + str(t.split()[5].split(":")[1])
        )
    except Exception:
        pass

    finally:
        return t

def __get_reaction__(x):
    try:
        like = x.find_element_by_class_name("_81hb").text
        return like
    except Exception:
        #print("Exception (count reaction)")
        return "0"

def __get_comment_count__(x, driver):
    cmt = "0"
    try:    
        WebDriverWait(driver, 10)
        string = x.find_element_by_class_name("_4vn1").text.lower()
        if (string.find("comment")!=-1):
            cmt = string.split("comment")[0]
            if (cmt.find('k ')!=-1):
                cmt = float(cmt.split("k ")[0])*1000  
            elif (cmt.find('m ')!=-1): 
                cmt = float(cmt.split("m ")[0])*1000000
        return cmt
    except Exception:
        return 0

def __get_img_count__(x):
    img = "0"
    try: 
        img = x.find_element_by_class_name("_19wj")
        return 1
    except Exception:
        try:
            img = len(x.find_elements_by_class_name("_46-h"))
            try :
                hide_img = x.find_element_by_class_name("_52db").text
                img = int(img) + int(hide_img)
                return img
            except Exception:
                return img
        except Exception:
            return 0