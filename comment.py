#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 04:00:16 2024

@author: yangchenyu
"""

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
import pandas as pd
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

import sqlite3
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
#建立評論資料表
create_table_sql = '''
CREATE TABLE IF NOT EXISTS "comments" (
 	"comments_id"	INTEGER,
 	"shopName"	TEXT NOT NULL,
 	"comment_1"	TEXT ,
 	"comment_2"	TEXT ,
 	"comment_3"	TEXT L,
 	PRIMARY KEY("comments_id")
);
'''
cursor.execute(create_table_sql)
#讀取shopsData資料表    
query_sql = 'SELECT id, shopName FROM shopsData;'
cursor.execute(query_sql)
rows = cursor.fetchall()
id_shopnames={}
for row in rows:
    id_, shopName = row
    id_shopnames[id_]=shopName    
#開啟瀏覽器執行檔    
chrome_path = "/Users/yangchenyu/chromedriver/chromedriver"
browser =webdriver.Chrome(service=webdriver.chrome.service.Service(chrome_path))
#google map頁面
browser.get("https://www.google.com/maps/search/")
time.sleep(0.1)  

for id_,shopName in id_shopnames.items():
    if 1045 <= id_ <= 1045:
        browser.find_element(By.ID,'searchboxinput').clear()
        browser.find_element(By.ID,'searchboxinput').send_keys(shopName)
        browser.find_element(By.ID,'searchbox-searchbutton').click()
        time.sleep(3)
        soup = BeautifulSoup(browser.page_source,"html.parser")
        all_comments = soup.find_all("a", class_='B8AOT')
        comments=[]
        for comment in all_comments:
            c = comment.get("aria-label")
            comments.append(c.split('"')[1].split('"')[0])
        
        insert_data_sql = '''
        INSERT OR REPLACE INTO "comments" ("comments_id","shopName","comment_1","comment_2"
        ,"comment_3") 
        VALUES (?, ?, ?, ?, ?);
        '''
        if len(comments)<3:
            cursor.execute(insert_data_sql, (id_, shopName, None, None, None))
            print(f"{id_}成功!")
        else:
            cursor.execute(insert_data_sql, (id_, shopName, comments[0], comments[1], comments[2]))
            print(f"{id_}成功!")
        
        conn.commit()
    else:
        continue

conn.close()
browser.close()






