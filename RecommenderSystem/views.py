import re
import os
from .models import ShopsKeyWords
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import CSVImportForm  # 匯入表單
from .models import ShopsData, ShopsKeyWords  # 匯入model
from message.models import Messages
import csv
import re
import os
import random
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import jieba
import paddle
import jieba.analyse
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Case, When, Value
import multiprocessing
import math
from django.db import connection
import django
from django.db.models import F
from itertools import chain
from datetime import datetime
import threading
import requests
from bs4 import BeautifulSoup
import sqlite3


# Create your views here.
# 定位到 myapp 的路徑
myapp_path = os.path.dirname(os.path.abspath(__file__))
# 中文停用詞
stopwords_file = myapp_path+"\stopwords.txt"
# 自定義辭典
custom_dict = myapp_path+"\custom_dict.txt"


def index(request):
    # update_thread = threading.Thread(target=update_data)
    # update_thread.start()
    shop_values = ShopsData.objects.order_by('id')
    random_twelve_values = random.sample(list(shop_values), 12)
    for dataset in random_twelve_values:
        dataset.shopPhoto = dataset.shopPhoto.split(" ")[0]
        shop_id = Messages.objects.filter(page=dataset.id).first()

    return render(request, 'index.html', locals())


# def update_data():
#     myHeader = {
#         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
#     sess = requests.Session()
#     keywords = ["新北美食", "台北美食"]
#     conn = sqlite3.connect('db.sqlite3')
#     cursor = conn.cursor()
#     insert_data_sql = '''
#     INSERT  INTO "shopsData" ("shopName","shopAddress","shopPhone","shopHours","shopPhoto","shopType") 
#     VALUES (?, ?, ?, ?, ?, ?); '''
#     for key in keywords:
#         url = f'https://supertaste.tvbs.com.tw/search/{key}/infocard/'
#         r = sess.post(url, headers=myHeader)
#         # print(r.text)
#         soup = BeautifulSoup(r.text, 'html.parser')
#         lists = soup.find('div', class_="list").find_all('a')
#         links = [link.get("href") for link in lists]
#         for link in links:
#             try:
#                 r = sess.get(link, headers=myHeader)
#                 soup = BeautifulSoup(r.text, "html.parser")
#             except Exception as e:
#                 print(f"異常{e}")
#             else:
#                 try:
#                     # 店名
#                     title = soup.find(
#                         "div", class_="store_card").find("h1").text
#                     sorex_exists = ShopsData.objects.filter(
#                         shopName=title).exists()
#                     if sorex_exists:
#                         break
#                     else:
#                         # 地址.電話
#                         adr_tel = soup.find("div", class_="info").find_all("a")
#                         address = adr_tel[0].text
#                         tel = adr_tel[1].text
#                         # 營業時間
#                         opentime = soup.find('div', class_="card_info").find(
#                             'li', {'style': True}).find("span").text
#                         # 圖片
#                         image_url = soup.find(
#                             "div", class_="content-img").find("img").get("src")
#                         image_name = image_url.split("-")[1]
#                         response = sess.get(image_url)
#                         file_name = "./static/img/" + image_name
#                         with open(file_name, "wb") as f:
#                             f.write(response.content)
#                         cursor.execute(insert_data_sql,
#                                        (title, address, tel, opentime, image_name, "0"))
#                         conn.commit()
#                 except Exception as e:
#                     print(f"異常{e}")

#     conn.close()
#     print("shopsData更新完成！")


# update_thread = threading.Thread(target=update_data)
# update_thread.start()


def recommender(request):
    searchText = request.GET.get('search', '')
    typeNumber = request.GET.get('type', '0')

    # 初始查詢結果
    data = ShopsData.objects.filter(shopType=typeNumber).order_by('-id') #以降序的方式陳列資料

    if searchText:  # 如果有搜索文字
        # 搜索店名或地址
        data = data.filter(shopName__icontains=searchText) | data.filter(
            shopAddress__icontains=searchText)

        # 如果没有找到结果，嘗試搜索評論内容分组中包含搜索文字(仍有篩選shopType)的結果
        if not data.exists():
            keyWord_data = ShopsKeyWords.objects.filter(
                contentGroup__icontains=searchText, shop_id__in=data.values_list('id', flat=True), shop__shopType=typeNumber)
            # 從評論內容查詢篩選，獲取對應的店家或景點資料
            data = ShopsData.objects.filter(
                id__in=keyWord_data.values_list('shop_id', flat=True))

    messages = Messages.objects.all().order_by('page', '-updated_at')  # 最新留言
    unique_messages = {}
    for message in messages:
        if message.page not in unique_messages:
            unique_messages[message.page] = message.updated_at

    # 分頁
    paginater = Paginator(data, 12)  # 12個商品為一頁
    page = request.GET.get('page') or 1  # 抓取頁數，預設為第1頁

    # 若分頁後的總頁碼大於4
    if paginater.num_pages > 4:
        page = int(page)
        if (page - 2) < 1:  # 目前頁碼-2會小於1，等於在1~3頁
            page_range = range(1, 5)  # 顯示1~4頁頁碼

        # 目前頁碼+2大於總頁碼，代表位於最後的1~3頁的範圍
        elif (page + 2) > paginater.num_pages:
            page_range = range(paginater.num_pages - 3,
                               paginater.num_pages + 1)
        else:
            # 非最前面或最後面幾頁，頁碼列表會隨著當今頁碼動態加減
            page_range = range(page - 1, page + 3)
    else:
        # 總頁數小於4就全部顯示
        page_range = paginater.page_range

    # 例外
    try:
        data = paginater.page(page)
    except PageNotAnInteger:  # 當page不是整數時
        data = paginater.page(1)  # 控制頁數，回到第一頁
    except EmptyPage:
        data = paginater.page(paginater.num_pages)
        # 輸入超過的頁數會跳到最後一頁(自動計算)

    return render(request, 'RecommenderStorePage.html', locals())


def shopDetail(request, shopid):
    shopdata = get_object_or_404(ShopsData, id=int(shopid))
    messages = Messages.objects.filter(page=shopdata.id)[::-1]  # 留言查詢
    shopkeywords = get_object_or_404(ShopsKeyWords, id=int(shopid))
    similarity_shop_ids = shopkeywords.similarityShop
    ids = similarity_shop_ids[1:-1].split(', ')
    ids_int = [int(x) for x in ids]
    ids_4 = ids_int[:-1]

    similar_shops_data = []
    for shop_id in ids_4:
        try:
            similar_shop_data = get_object_or_404(ShopsData, id=shop_id)
            similar_shops_data.append(similar_shop_data)
        except Exception as e:
            print("Error occurred while fetching shop data:", e)

    if request.method == 'get':

        # 顯示全部的商品資料
        data = ShopsData.objects.all()  # .order_by('-id')

        paginater = Paginator(data, 8)
        return render(request, 'shopDetailPage.html', locals())
    return render(request, 'shopDetailPage.html', locals())


def import_csv(request):  # 載入爬蟲csv
    if request.method == 'POST':
        form = CSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file'].read().decode(
                'ansi').splitlines()
            # csv_reader = csv.DictReader(csv_file[:-1])
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                ShopsData.objects.create(
                    shopName=row['shopName'], shopAddress=row['shopAddress'], shopPhone=row['shopPhone'], shopHours=row['shopHours'], shopPhoto=row['shopPhoto'], shopType=row['shopType'])

            return HttpResponse('成功')  # Redirect to a success page
    else:
        form = CSVImportForm()

    return render(request, 'import.html', {'form': form})


# def getKeyWords12(request):
#     data = ShopsData.objects.all()
#     msg_data = Messages.objects.all()

#     for shop in data:
#         key1 = shop.shopAddress[:3]
#         key2 = shop.shopAddress[3:6]
#         keys = f"{key1},{key2}"

#         # 檢查是否已經存在相同的關鍵字
#         existing_keywords = ShopsKeyWords.objects.filter(
#             shop=shop, keyWords=keys)
#         if not existing_keywords.exists():
#             # 如果關鍵字不存在，則創建新的資料來寫入關鍵字
#             ShopsKeyWords.objects.create(shop=shop, keyWords=keys)

#     # 取得字頻分析的文章段落
#     # 建立存儲店家景點對應的評論內容的串列
#     key3_list = []
#     for shop in data:
#         inner_list = [msg.content for msg in msg_data if msg.page == shop.id]
#         if inner_list:  # 檢查內部串列是否為空
#             key3_list.append(inner_list)
#         else:
#             key3_list.append(None)  # 如果內部串列為空，則添加 None

#     # 通过匹配条件过滤要更新的对象，并更新内容 
#     for shop, content_list, keys in zip(data, key3_list, [f"{shop.shopAddress[:3]},{shop.shopAddress[3:6]}" for shop in data]):
#         # 过滤要更新的对象
#         shopObj_update = ShopsKeyWords.objects.filter(shop=shop, keyWords=keys)

#         # 更新内容
#         shopObj_update.update(contentGroup=content_list)

#     return HttpResponse('key1,2成功')


# def getKeyWords3(request):
#     update_keywords_in_model()
#     return HttpResponse('key3成功')

# def analyze_text(texts):
#     # 將所有評論串聯成一個長文字串列
#     all_text = " ".join(texts)
#     # 分詞
#     words = jieba.lcut(all_text)
#     # 計算字頻
#     word_counts = Counter(words)

#     return word_counts

# def extract_keywords(texts, top_n=5):
#     # 將所有文本串聯成一個大文本
#     all_text = " ".join(texts)
#     # 使用 TF-IDF 方法提取關鍵字
#     keywords = jieba.analyse.extract_tags(all_text, topK=top_n)

#     return keywords

# def update_keywords_in_model():
#     all_data = list(ShopsKeyWords.objects.all())

#     for data in all_data:
#         if data.contentGroup:
#             texts = [data.contentGroup]
#             keywords = extract_keywords(texts)
#             data.contentGroupKeys = ",".join(keywords)
#         else:
#             data.contentGroupKeys = None

#     # 將每筆資料儲存
#     for data in all_data:
#         data.save()


# def getKeyWords4(request):
#     start_time = datetime.now()  # 紀錄函式開始執行的時間
#     file_path = f"{myapp_path}+\similarity_results_0.txt"
#     if not os.path.exists(file_path):
#         # 獲取 shopType=0/1 的 ShopsKeyWords 的物件資料
#         shop_keywords_0 = ShopsKeyWords.objects.filter(shop__shopType=0)
#         shop_keywords_1 = ShopsKeyWords.objects.filter(shop__shopType=1)

#         # 處理 shopType=0 的 ShopsKeyWords 物件，並將相似度資料計算出來，寫進 txt 儲存
#         process_similarity_results(shop_keywords_0, 'similarity_results_0.txt')

#         # 處理 shopType=1 的 ShopsKeyWords 物件，並將相似度資料計算出來，寫進 txt 儲存
#         process_similarity_results(shop_keywords_1, 'similarity_results_1.txt')

#     end_time = datetime.now()  # 紀錄函式執行結束的時間
#     execution_time = end_time - start_time  # 計算函數總執行時間
#     print("函數執行時間：", execution_time)

#     return HttpResponse('key4成功')

# def process_similarity_results(shop_keywords, file_path):
#     with open(file_path, 'w', encoding='utf-8') as file:
#         for keyword_1 in shop_keywords:
#             text1 = keyword_1.contentGroupKeys
#             keyword_1_id = keyword_1.id  # 获取 keyword_1 的 id
#             for keyword_2 in shop_keywords:
#                 text2 = keyword_2.contentGroupKeys
#                 keyword_2_id = keyword_2.id  # 获取 keyword_2 的 id
#                 similarity_score = calculate_similarity(text1, text2)
#                 if similarity_score is not None:
#                     # 写入文件时同时记录 shop_id
#                     file.write(
#                         f"({keyword_1_id},{keyword_2_id},{similarity_score:.4f}),")
#                 else:
#                     file.write(f"({keyword_1_id},{keyword_2_id},-1,")
#             file.write("\n")

# def calculate_similarity(text1, text2):
#     if text1 is None or text2 is None:
#         return -1
#     vectorizer = TfidfVectorizer()
#     tfidf_matrix = vectorizer.fit_transform([text1, text2])
#     similarity_score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])

#     return similarity_score[0][0]


# def getKeyWords5(request):
#     similarity_results_0 = read_similarity_file('similarity_results_0.txt')
#     similarity_results_1 = read_similarity_file('similarity_results_1.txt')

#     merged_similarity_results = similarity_results_0 + similarity_results_1
#     print(len(similarity_results_0))

#     shopsKeyWords = ShopsKeyWords.objects.all()

#     for shop, line in zip(shopsKeyWords, merged_similarity_results):
#         # 初始化三個列表來存放最大的五個相似度資料、相似的店家景點ID、相似度的分數
#         top_5_dict = []
#         top_5_ids = []
#         top_5_similarities = []

#         # 對相似度的分數進行排序，取出前五個
#         sorted_similarities = sorted(
#             line['similarities'], key=lambda x: x['similarities'], reverse=True)[1:6]
#         myid = line['similarities'][0]['myshop_id']
#         for similarity in sorted_similarities:
#             top_5_dict.append(similarity)  # 添加字典
#             top_5_ids.append(similarity['othershop_id'])  # 提取 sim_id
#             top_5_similarities.append(similarity['similarities'])  # 提取相似度值
    
#         shop.similarityScore = top_5_similarities
#         shop.similarityShop = top_5_ids
#         shop.save()  # 保存更新

#     return HttpResponse('key5成功')


# def read_similarity_file(file_path):
#     similarity_results = []
#     with open(file_path, 'r', encoding='utf-8') as file:

#         for line in file:
#             similarities = []
#             # 使用正則表達式提取出txt的資料
#             matches = re.findall(
#                 r'\((\d+),(\d+),(-?\d+\.\d+)\),', line.strip())

#             # 對每個字串做處理
#             for match in matches:
#                 keyword_id = int(match[0])
#                 shop_id = int(match[1])
#                 score = float(match[2])
#                 similarities.append(
#                     {'myshop_id': keyword_id, 'othershop_id': shop_id, 'similarities': score})
#             similarity_results.append({'similarities': similarities})

#     return similarity_results
