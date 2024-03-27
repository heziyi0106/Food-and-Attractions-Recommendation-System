#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 21:32:17 2024

@author: yangchenyu
"""
import requests
from bs4 import BeautifulSoup
import sqlite3
def update_data():
    myHeader = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
    sess = requests.Session()
    keywords = ["新北美食", "台北美食"]
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    insert_data_sql = '''
    INSERT  INTO "shopsData" ("shopName","shopAddress","shopPhone","shopHours","shopPhoto","shopType") 
    VALUES (?, ?, ?, ?, ?, ?); '''
    for key in keywords:
        url = f'https://supertaste.tvbs.com.tw/search/{key}/infocard/'
        r = sess.post(url, headers=myHeader)
        # print(r.text)
        soup = BeautifulSoup(r.text, 'html.parser')
        lists = soup.find('div', class_="list").find_all('a')
        links = [link.get("href") for link in lists]
        for link in links:
            try:
                r = sess.get(link, headers=myHeader)
                soup = BeautifulSoup(r.text, "html.parser")
            except Exception as e:
                print(f"異常{e}")
            else:
                try:
                    # 店名
                    title = soup.find(
                        "div", class_="store_card").find("h1").text
                    cursor.execute("SELECT 1 FROM shopsData WHERE shopName = %s", [title])
                    shop_exists = cursor.fetchone()
                    if bool(shop_exists):
                        break
                    # sorex_exists = ShopsData.objects.filter(
                    #     shopName=title).exists()
                    # if sorex_exists:
                    #     break
                    else:
                        # 地址.電話
                        adr_tel = soup.find("div", class_="info").find_all("a")
                        address = adr_tel[0].text
                        tel = adr_tel[1].text
                        # 營業時間
                        opentime = soup.find('div', class_="card_info").find(
                            'li', {'style': True}).find("span").text
                        # 圖片
                        image_url = soup.find(
                            "div", class_="content-img").find("img").get("src")
                        image_name = image_url.split("-")[1]
                        response = sess.get(image_url)
                        file_name = "./static/img/" + image_name
                        with open(file_name, "wb") as f:
                            f.write(response.content)
                        cursor.execute(insert_data_sql,
                                       (title, address, tel, opentime, image_name, "0"))
                        conn.commit()
                except Exception as e:
                    print(f"異常{e}")
    conn.close()