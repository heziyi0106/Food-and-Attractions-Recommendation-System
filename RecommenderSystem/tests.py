from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
import pandas as pd
from django.test import TestCase
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import CSVImportForm  # 匯入表單
from .models import ShopsData  # 匯入model
from message.models import Messages
import csv
import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random
# Create your tests here.


# def export_to_csv():
#     con = sqlite3.connect('D:\djangoProject\groupSite\db.sqlite3')
#     sql = f"SELECT * FROM shopsData"
#     df_date = pd.read_sql(sql, con)

#     con.close()
#     df_date.to_csv('D:\djangoProject\groupSite\shopsData.csv',
#                    index=False, encoding='utf-8')
#     return '成功寫入 CSV'


# export_to_csv()


# def recommender(request):  # 推薦
#     searchText = request.GET.get('search', '')  # 获取搜索关键字
#     data = ShopsData.objects.all()

#     if len(searchText) > 0:  #若有搜尋內容(模糊搜尋店名、地址)
#         data = data.filter(shopName__icontains=searchText)|data.filter(shopAddress__icontains=searchText)

#     # 分頁
#     paginater = Paginator(data, 12)  # 12個商品為一頁
#     page = request.GET.get('page') or 1  # 抓取頁數，預設為第1頁

#     # 如果分页后的总页数大于11
#     if paginater.num_pages > 4:
#         page = int(page)
#         # 总共11页,取中间页(当前页)来判断是否是第1~11页
#         if (page - 2) < 1:
#             # 1~11页码列表
#             page_range = range(1, 5)
#         # 取11页的中间页(当前页)判断是否是最后11页
#         elif (page + 2) > paginater.num_pages:
#             # 最后11页页码列表
#             page_range = range(paginater.num_pages - 3,
#                                paginater.num_pages + 1)
#         else:
#             # 如果不是前面11页,也不是后面11页,那么页码列表动态就会随着当前列表动态加减
#             page_range = range(page - 1, page + 3)
#     else:
#         # 总页数小于11就直接全部显示
#         page_range = paginater.page_range

#     messages = Messages.objects.all().order_by('page', '-updated_at')  # 最新留言
#     unique_messages = {}
#     for message in messages:
#         if message.page not in unique_messages:
#             unique_messages[message.page] = message.updated_at

#     # 例外
#     try:
#         data = paginater.page(page)
#     except PageNotAnInteger:  # 當page不是整數時
#         data = paginater.page(1)  # 控制頁數，回到第一頁
#     except EmptyPage:
#         data = paginater.page(paginater.num_pages)
#         # 輸入超過的頁數會跳到最後一頁(自動計算)

#     return render(request, 'RecommenderStorePage.html', locals())


# def getKeyWords(request):
#     # keyword1 =
#     data = ShopsData.objects.all()
#     msg_data = Messages.objects.all()
#     # for shop in data:
#     for i in range(len(data)):

#         key1 = data[i].shopAddress[:3]
#         key2 = data[i].shopAddress[3:6]
#         # key3 = msg_data[i].content

#         # print(i,key3)
#         # 若資料已存在資料表，則不建立新一筆物件資料
#         shopObj = ShopsData.objects.get(id=i+1)
#         ShopsKeyWords.objects.get_or_create(shop=shopObj,keyWords=key1+","+key2)

#         # 用于存储匹配的内容的列表
#     key3_list = [
#         [msg.content for msg in msg_data if msg.page == shop.id]  # 匹配的内容列表
#         for shop in data  # 外部循环迭代 data 中的对象
#     ]

#     # 打印结果以进行调试
#     for i, content_list in enumerate(key3_list):
#         # print(i, content_list)
#         # # 使用过滤器选择要更新的对象
#         # shopObj_update = ShopsKeyWords.objects.filter(contentKeyWords='')

#         # # 使用 update() 方法批量更新数据
#         # shopObj_update.update(contentKeyWords=content_list)
#         ShopsKeyWords.objects.filter(shop=shopObj, contentKeyWords='').update(contentKeyWords=content_list)

#     return HttpResponse('成功')

def getKeyWords(request):
    # 取得關鍵字1、2
    data = ShopsData.objects.all()
    msg_data = Messages.objects.all()

    for shop in data:
        key1 = shop.shopAddress[:3]
        key2 = shop.shopAddress[3:6]

        # 确保店铺对象存在
        shopObj, created = ShopsKeyWords.objects.get_or_create(
            shop=shop, keyWords=key1 + "," + key2)

    # 取得字頻分析的文章段落
    # 用于存储匹配的内容的列表
    key3_list = []
    for shop in data:
        inner_list = [msg.content for msg in msg_data if msg.page == shop.id]
        if inner_list:  # 检查内部列表是否为空
            key3_list.append(inner_list)
        else:
            key3_list.append(None)  # 如果内部列表为空，则添加 None

    # 通过匹配条件过滤要更新的对象，并更新内容
    for shop, content_list in zip(data, key3_list):
        # 过滤要更新的对象
        shopObj_update = ShopsKeyWords.objects.filter(shop=shop)

        # 更新内容
        if not shopObj_update.exists():
            shopObj_update.update(contentKeyWords=content_list)
        # shopObj_update.update(contentKeyWords=content_list)

    # 評論文本分析
    ShopContents = ShopsKeyWords.objects.all()
    stopwords_file = myapp_path+"\stopwords.txt"  # 停用詞表的絕對檔案路徑

    count = 0
    for content in ShopContents:
        texts = content.contentKeyWords
        count += 1
        if not texts:
            continue

        # 提取關鍵字
        keywords = extract_keywords(texts, stopwords_file)
        print(count, "關鍵字：", keywords)

    # ## 計算評論的相似程度
    # # 從資料庫中讀取第一個物件的評論串列
    # first_object = ShopsKeyWords.objects.first()  # 假設您的物件模型名稱為 ShopsKeyWords
    # comments = first_object.contentKeyWords.split(',') if first_object.contentKeyWords else []

    # # 從資料庫中讀取其他物件的評論串列列表
    # other_objects = ShopsKeyWords.objects.exclude(id=first_object.id)  # 排除第一個物件
    # comments_list = []
    # for obj in other_objects:
    #     if obj.contentKeyWords:  # 如果 contentKeyWords 不是 None
    #         comments_list.append(obj.contentKeyWords.split(','))

    # # 對第一個物件的每一條評論與其他物件的每一條評論進行相似度計算
    # for comment in comments:
    #     if not comment:  # 如果評論為空，跳過
    #         continue

    #     print(f"第一個物件的評論：{comment}")
    #     for idx, comments_other in enumerate(comments_list):
    #         print(f"與第 {idx + 1} 個物件的評論相似度：")
    #         for comment_other in comments_other:
    #             if not comment_other:  # 如果評論為空，跳過
    #                 continue
    #             similarity_score = calculate_similarity(comment, comment_other)
    #             print(f"評論：{comment_other}，相似度：{similarity_score}")

    return HttpResponse('成功')


def getKeyWords(request):
    # 評論文本分析
    ShopContents = ShopsKeyWords.objects.all()
    stopwords_file = myapp_path+"\stopwords.txt"  # 停用詞表的絕對檔案路徑

    count = 0
    for content in ShopContents:
        texts = content.contentKeyWords
        count += 1
        if not texts:
            continue

        # 進行字頻分析
        word_counts = analyze_text_frequency(texts, stopwords_file)

        # 提取關鍵字
        keywords = extract_keywords(word_counts)
        print(count, "關鍵字：", keywords[2:])

# 計算文章詞彙的字頻，算出哪些字為關鍵字


def remove_punctuation(text):
    # 使用正則表達式將標點符號替換成空格
    text_without_punct = re.sub(r'[^\w\s]', ' ', text)
    return text_without_punct


def remove_stopwords(text, stopwords):
    # 將文本分詞並去除停用詞
    words = jieba.lcut(text)
    words_without_stopwords = [word for word in words if word not in stopwords]
    return " ".join(words_without_stopwords)


def analyze_text_frequency(texts, stopwords_file):
    # 將所有文字串聯成一個大文本
    all_text = " ".join(texts)

    # 去除標點符號
    all_text = remove_punctuation(all_text)

    # 讀取停用詞表
    with open(stopwords_file, 'r', encoding='utf-8') as f:
        stopwords = [line.strip() for line in f]

    # 分詞並去除停用詞
    all_text = remove_stopwords(all_text, stopwords)

    # 分詞，使用精確模式
    jieba.enable_paddle()
    jieba.load_userdict(myapp_path+"\custom_dict.txt")  # 加載自訂詞典
    tokens = jieba.cut(all_text, cut_all=True, use_paddle=True)
    # tokens = jieba.cut(all_text, cut_all=False)

    # 計算字頻
    word_counts = Counter(tokens)

    return word_counts


def extract_keywords(word_counts, top_n=100):
    # 選取出現頻率最高的前 top_n 個詞語作為關鍵字
    keywords = [word for word, count in word_counts.most_common(top_n)]

    return keywords


def getKeyWords4(request):
    # 計算評論的相似程度
    # 從資料庫中讀取所有物件的文本串列
    all_objects = ShopsKeyWords.objects.all()

    # 輸出相似度結果到txt檔案
    with open('similarity_results.txt', 'w', encoding='utf-8') as file:
        for i, obj1 in enumerate(all_objects):
            # 以 關鍵字 作為相似度分析的素材
            if obj1.contentGroupKeys:  # 如果 contentGroupKeys 不是 None
                text1 = obj1.contentGroupKeys
                for j, obj2 in enumerate(all_objects):
                    if i == j:  # 跳過相同的物件
                        continue
                    if obj2.contentGroupKeys:  # 如果 contentGroupKeys 不是 None
                        text2 = obj2.contentGroupKeys
                        similarity_score = calculate_similarity(text1, text2)
                        file.write(
                            f"文本1：{text1}，文本2：{text2}，相似度：{similarity_score}\n")

    return HttpResponse('key4成功')


def calculate_similarity(text1, text2):
    # 將文本轉換為 TF-IDF 向量
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])

    # 計算餘弦相似度
    similarity_score = cosine_similarity(
        tfidf_matrix[0], tfidf_matrix[1])[0][0]

    return similarity_score
