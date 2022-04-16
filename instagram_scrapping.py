#!/usr/bin/env python
# coding: utf-8

# In[1]:


import time
from functools import reduce
from selenium import webdriver
import json 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# In[2]:


def ask_user():
    check = str(input("Do you want to continue? (Y/N): ")).lower().strip()
    try:
        if check[0] == 'y':
            return True
        elif check[0] == 'n':
            return False
        else:
            print('Invalid Input')
            return ask_user()
    except Exception as error:
        print("Please enter valid inputs")
        print(error)
        return ask_user()


# In[3]:


def find_element(driver, XPATH):
    try:
        element=driver.find_element_by_xpath(XPATH)
        return element, True
    except:
        return "Nothing", False


# In[4]:


def get_information(driver, XPATH):
    element, boolean = find_element(driver, XPATH)
    if boolean == False:
        return False
    return element.text


# In[5]:


def get_post_links(driver):
    reached_page_end = False
    last_height = driver.execute_script("return document.body.scrollHeight")
    links=set()
    while not reached_page_end:   
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        # Fetching Posts
        posts=driver.find_elements_by_xpath("//div[@class='v1Nh3 kIKUG  _bz0w']/a")
        fetched_links=[post.get_attribute("href") for post in posts]
        links=links.union(set(fetched_links))
        if last_height == new_height:
            reached_page_end = True
        else:
            last_height = new_height
    return list(links)


# In[6]:


def get_post_information(driver, post):
    # DICT BLUEPRINT
    post_information={
        "date":"Null",
        "url":"Null",
        "comment_count":0,
        "like_count":0,
        "location":"Null",
        "lng":"Null",
        "lat":"Null",
        "error":"Null"
    }
    # URL
    post_information["url"]=post
    driver.get(post)
    refresh_if_not_loaded(driver, "//time[@class='_1o9PC Nzb55']")
    try:
        # GET DATE (ALWAYS PRESENT)
        date=driver.find_element_by_xpath("//time[@class='_1o9PC Nzb55']").get_attribute("title")
        post_information["date"]=date
    
        # COUNT TOTAL OF COMMENTS
        try:
            load_comments, boolean= find_element(
                driver,"(//*[name()='svg'][contains(@aria-label,'Load more comments')])[1]")
            if boolean==True:
                while boolean==True:
                    load_comments.click()
                    time.sleep(2)
                    load_comments, boolean=find_element(
                        driver,"(//*[name()='svg'][contains(@aria-label,'Load more comments')])[1]")
        except:
            pass
        comments=driver.find_elements_by_xpath("//ul[@class='Mr508 ']")
        post_information["comment_count"]=len(comments)
    
        # COUNT LIKES
        likes_button, boolean=find_element(driver,"//a[normalize-space()='others']")
        if boolean==False:
            post_information["like_count"]=0
        else:
            likes_button.click() # Click others
            WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label,'Likes')]/div[contains(@class,'')]/div[3]/div[1]")))
            scrollable=driver.find_element_by_xpath(
                "//div[contains(@aria-label,'Likes')]/div[contains(@class,'')]/div[3]/div[1]") #Element to scroll
            counted_people=set()
            while True:
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label,'Likes')]/div[contains(@class,'')]/div[3]/div[1]/div[1]")))
                size_scroll=driver.find_element_by_xpath(
                    "//div[contains(@aria-label,'Likes')]/div[contains(@class,'')]/div[3]/div[1]/div[1]").get_attribute(
                    "style").split("padding-top: ")[1]
                # Counting people
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@class='             qF0y9          Igw0E   rBNOH        eGOV_     ybXk5    _4EzTm                                                                                   XfCBB          HVWg4                 ']/div[2]/div/div/span/a")))
                people=driver.find_elements_by_xpath(
                    "//div[@class='             qF0y9          Igw0E   rBNOH        eGOV_     ybXk5    _4EzTm                                                                                   XfCBB          HVWg4                 ']/div[2]/div/div/span/a")
                people_names=[person.text for person in people]
                counted_people=counted_people.union(set(people_names))
                time.sleep(2)
                driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable)
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label,'Likes')]/div[contains(@class,'')]/div[3]/div[1]/div[1]")))
                new_size_scroll=driver.find_element_by_xpath(
                    "//div[contains(@aria-label,'Likes')]/div[contains(@class,'')]/div[3]/div[1]/div[1]").get_attribute(
                    "style").split("padding-top: ")[1]
                if size_scroll==new_size_scroll:
                    break
            post_information["like_count"]=len(counted_people)
    
        # GETTING LOCATION AND COORDINATES
        location, boolean =find_element(driver,"//a[@class='O4GlU']")
        if boolean==True:
            location_name=location.text
            post_information["location"]=location_name
            driver.get(location.get_attribute("href"))
            refresh_if_not_loaded(driver, "//h1[@class='_7UhW9       fKFbl yUEEX   KV-D4          uL8Hv         ']")
            try:
                lat=driver.find_element_by_xpath("//meta[@property='place:location:latitude']").get_attribute("content")
                lng=driver.find_element_by_xpath("//meta[@property='place:location:longitude']").get_attribute("content")
                post_information["lat"]=lat
                post_information["lng"]=lng
            except:
                pass
        post_information["error"]="False"
    except Exception as e:
        post_information["error"]="True"
        print(e)
    return post_information


# In[7]:


def refresh_if_not_loaded(driver,XPATH):
    # REFRESH PAGE UNTIL SIX TIMES IF NOT PROPERLY LOADED
    counter=0
    while True:
        if counter>5:
            break
        try:
            WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH, XPATH)))
            break
        except:
            driver.refresh()
            counter+=1


# In[8]:


def get_post_dict(driver, posts):
    posts_info=[]
    for count,post in enumerate(posts):
        print("Getting information: Post",count+1,"of",len(posts))
        post_information=get_post_information(driver,post)
        posts_info.append(post_information)
    return posts_info


# In[9]:


def get_user_information(driver):
    user_information={
        "username":"Null",
        "full_name":"Null",
        "website":"Null",
        "is_verified":"Null",
        "is_private":"Null",
        "follower_count":"Null",
        "following_count":"Null",
        "media_count":"Null",
        "likes_count":"Null",
        "posts":[]
    }
    # GET USERNAME (ALWAYS PRESENT)
    refresh_if_not_loaded(driver, "//h2[@class='_7UhW9       fKFbl yUEEX   KV-D4              fDxYl     ']")
    username=driver.find_element_by_xpath(
        "//h2[@class='_7UhW9       fKFbl yUEEX   KV-D4              fDxYl     ']").text
    # GET FULLNAME (ALWAYS PRESENT)
    full_name=driver.find_element_by_xpath("//h1[@class='Yk1V7']").text
    # GET WEBSITE 
    website = get_information(driver, "//a[@class='heKAw']")
    # FIND IF ACCOUNT IS A VERIFIED ONE
    _ , is_verified =find_element(driver, "//span[@class='mTLOB Szr5J coreSpriteVerifiedBadge ']")
    # FIND IF ACCOUNT IS PRIVATE
    _ , is_private =find_element(driver, "//h2[@class='rkEop']")
    # FIND THE NUMBER OF FOLLOWERS AND FOLLOWING
    if is_private==True:
        media_count=driver.find_element_by_xpath("(//span[@class='-nal3 ']/span[@class='g47SY '])[position()=1]").text
        follower_count=driver.find_element_by_xpath("(//span[@class='-nal3 ']/span[@class='g47SY '])[position()=2]").text
        following_count=driver.find_element_by_xpath("(//span[@class='-nal3 ']/span[@class='g47SY '])[position()=3]").text
    else:
        media_count=driver.find_element_by_xpath("(//span[@class='-nal3 ']/span[@class='g47SY '])[position()=1]").text
        follower_count=driver.find_element_by_xpath("(//a[@class='-nal3 ']/span[@class='g47SY '])[position()=1]").text
        following_count=driver.find_element_by_xpath("(//a[@class='-nal3 ']/span[@class='g47SY '])[position()=2]").text

    # ADDING INFORMATION
    user_information["username"]=username
    user_information["full_name"]=full_name
    user_information["website"]=website
    user_information["is_verified"]=is_verified
    user_information["is_private"]=is_private
    user_information["follower_count"]=follower_count
    user_information["following_count"]=following_count
    user_information["media_count"]=media_count
    return user_information


# In[ ]:


if __name__ == '__main__':
    # READ CREDENTIALS AND USER PROFILE
    config=open("instagram_scrapper_conf.txt","r")
    lines=config.readlines()
    USERNAME=lines[0].split("USER_EMAIL=")[1].replace("\n","")
    PASSWORD=lines[1].split("USER_PASSWORD=")[1].replace("\n","")
    PATH=lines[2].split("PATH=")[1].replace("\n","")
    config.close()
    
    # READ INSTAGRAM PROFILES
    profiles_file=open("instagram_profiles.txt","r")
    profiles=profiles_file.readlines()
    profiles_file.close()
    
    # OPENING INSTAGRAM
    driver = webdriver.Chrome(executable_path = PATH)
    driver.maximize_window()
    url="https://www.instagram.com"
    driver.get(url)
    refresh_if_not_loaded(driver, "//input[contains(@name,'username')]")
    driver.find_element_by_xpath(
        "//input[contains(@name,'username')]").send_keys(USERNAME) # Sending Email
    driver.find_element_by_xpath(
        "//input[@name='password']").send_keys(PASSWORD) # Sending Password
    driver.find_element_by_xpath("//button[@class='sqdOP  L3NKy   y3zKF     ']").click() # Clicking Log In
    time.sleep(3)    
    # ASK USER TO CONTINUE
    if ask_user()==False:
        driver.quit()
        quit()
        time.sleep(2)
    else:
        print("Ok Continue")
    
    # GETTING PROFILES INFORMATION
    for profile in profiles:
        print("Getting information of user:",profile)
        driver.get("https://www.instagram.com/" + profile.replace("\n",""))
        # GET USER INFORMATION
        try:
            user_information=get_user_information(driver)
            if user_information["is_private"]==True:
                with open(user_information["username"]+".json", "w") as outfile:
                    json.dump(user_information, outfile, indent=4)
                    outfile.close()
                continue
        except:
            print("Unable to get user information")
            continue
        # SCROLL DOWN AND FETCH POST INFORMATION
        posts=get_post_links(driver)
        if len(posts)==0:  # TESTING IF PROFILE HAS POSTS
            with open(user_information["username"]+".json", "w") as outfile:
                json.dump(user_information, outfile, indent=4)
                outfile.close()
            print("Profile has not posts yet")
            continue
        posts_info=get_post_dict(driver,posts)
        # COUNT TOTAL LIKES
        likes=list(map(lambda post: post["like_count"],posts_info))
        total_likes=reduce(lambda a, b: a + b, likes)
        user_information["likes_count"]=total_likes
        # ADDING POSTS INFORMATION TO USER INFORMATION
        user_information["posts"]=posts_info
        # EXPORTING JSON FILE
        with open(user_information["username"]+".json", "w") as outfile:
            json.dump(user_information, outfile, indent=4)
            outfile.close()
    # CLOSING
    driver.close()
    quit()

