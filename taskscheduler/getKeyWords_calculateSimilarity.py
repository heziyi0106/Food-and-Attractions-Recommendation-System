import re
import os
import time
import re
import os
import jieba
import paddle
import jieba.analyse
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import sqlite3

# 取得當前的目錄
current_dir = os.path.dirname(__file__)

# # 中文停用詞
# stopwords_file = os.path.abspath(os.path.join(current_dir, '..', 'RecommenderSystem', 'stopwords.txt'))
# # 自定義辭典
# custom_dict = os.path.abspath(os.path.join(current_dir, '..', 'RecommenderSystem', 'custom_dict.txt'))

db = os.path.abspath(os.path.join(current_dir, '..', 'db.sqlite3'))

def getKeyWords12():
    # 取得資料庫連線
    connect = sqlite3.connect(db)
    cursor = connect.cursor()

    # 取得資料庫內容
    data_query = "SELECT * FROM shopsData"
    cursor.execute(data_query)
    data = cursor.fetchall()
    print(len(data))

    for i, shop in enumerate(data):
        data_id = shop[0]
        shop_id = shop[0]
        shopAddress = shop[4]  # 假設 shopAddress_index 是 shopAddress 欄位的索引
        key1 = shopAddress[:3]
        key2 = shopAddress[3:6]
        keys = f"{key1},{key2}"
        print(i + 1, keys)  # 或者將 keys 用於接下來的處理

        # 檢查 shopKeyWords 表中是否已存在对应的 shop_id，如果不存在则插入新数据
        check_query = "SELECT * FROM shopsKeyWords WHERE shop_id = ?"
        cursor.execute(check_query, (shop_id,))
        existing_keyword = cursor.fetchone()
        if not existing_keyword:
            # 如果 shopKeyWords 表中不存在对应的 shop_id，执行插入操作
            insert_query = "INSERT INTO shopsKeyWords (shop_id, keyWords) VALUES (?, ?)"
            cursor.execute(insert_query, (shop_id, keys))
            new_id = cursor.lastrowid  # 獲取最後插入的自動增量值
            print(f"新增資料的ID為：{new_id}")

    connect.commit()
    cursor.close()
    connect.close()

    print('key1,2成功')

def getKeyWords3txt():
    # 取得資料庫連線
    connect = sqlite3.connect(db)   
    cursor = connect.cursor()
    
    # 取得資料庫內容
    data_query = "SELECT * FROM shopsData"
    cursor.execute(data_query)
    data = cursor.fetchall()
    print(len(data))
    msg_query = "SELECT * FROM Messages"
    cursor.execute(msg_query)
    msg_data = cursor.fetchall()
    print(len(msg_data))
    
    # 取得字頻分析的文章段落
    # 建立存儲店家景點對應的評論內容的串列
    key3_list = []
    for shop in data:
        inner_list = [msg[3] for msg in msg_data if msg[2] == shop[0]]
        if inner_list:  # 檢查內部串列是否為空
            key3_list.append(inner_list)
        else:
            key3_list.append(None)  # 如果內部串列為空，則添加 None

    # 通過匹配條件過濾要更新的對象，並更新內容
    for shop, content_list, keys in zip(data, key3_list, [f"{shop[4][:3]},{shop[4][3:6]}" for shop in data]):
        # 過濾要更新的對象
        update_query = "UPDATE ShopsKeyWords SET contentGroup = ? WHERE shop_id = ? AND keyWords = ?"
        cursor.execute(update_query, (str(content_list), shop[0], keys))
    
    connect.commit()
    cursor.close()
    connect.close()

    print('key3文本成功')

def getKeyWords3():
    update_keywords_in_model()
    print('key3成功')

def update_keywords_in_model():
    # 取得資料庫連線
    connect = sqlite3.connect(db)
    cursor = connect.cursor()

    # 取得所有資料
    cursor.execute("SELECT * FROM shopsKeyWords")
    all_data = cursor.fetchall()
    print(len(all_data))

    for data in all_data:
        if data[3]:  # 如果contentGroup不為空
            texts = [data[3]]  # 將contentGroup取出作為文本串列
            keywords = extract_keywords(texts)  # 提取關鍵字
            keyword_str = ",".join(keywords)  # 將關鍵字串列轉換為字串
            update_query = "UPDATE shopsKeyWords SET contentGroupKeys = ? WHERE id = ?"  # 更新SQL語句
            cursor.execute(update_query, (keyword_str, data[0]))  # 執行更新操作

    # 提交事務並關閉資料庫連線
    connect.commit()
    cursor.close()
    connect.close()

def analyze_text(texts):
    # 將所有評論串聯成一個長文字串列
    all_text = " ".join(texts)
    # 分詞
    words = jieba.lcut(all_text)
    # 計算字頻
    word_counts = Counter(words)

    return word_counts

def extract_keywords(texts, top_n=5):
    # 將所有文本串聯成一個大文本
    all_text = " ".join(texts)
    # 使用 TF-IDF 方法提取關鍵字
    keywords = jieba.analyse.extract_tags(all_text, topK=top_n)

    return keywords

current_dir = os.path.dirname(__file__)  # 獲取當前腳本所在的目錄
file_path_0 = os.path.abspath(os.path.join(current_dir, '..', 'RecommenderSystem', 'similarity_results_0.txt'))
file_path_1 = os.path.abspath(os.path.join(current_dir, '..', 'RecommenderSystem', 'similarity_results_1.txt'))

# def getKeyWords4():
#     start_time = datetime.now()  # 紀錄函式開始執行的時間

#     # 取得資料庫連線
#     connect = sqlite3.connect(db)
#     cursor = connect.cursor()

#     # 處理 shopType=0 的 ShopsKeyWords 物件，並將相似度資料計算出來，寫進 txt 儲存
#     process_similarity_results(cursor, file_path_0, shop_type=0)
#     # 處理 shopType=1 的 ShopsKeyWords 物件，並將相似度資料計算出來，寫進 txt 儲存
#     process_similarity_results(cursor, file_path_1, shop_type=1)

#     # 關閉資料庫連線
#     cursor.close()
#     connect.close()

#     end_time = datetime.now()  # 紀錄函式執行結束的時間
#     execution_time = end_time - start_time  # 計算函數總執行時間
#     print("函數執行時間：", execution_time)
#     print('key4成功')

# def process_similarity_results(cursor, file_path, shop_type):
#     if not os.path.exists(file_path):
#         # 如果文件不存在，則創建一個新文件
#         open(file_path, 'w').close()

#     with open(file_path, 'w', encoding='utf-8') as file:
#         # 獲取相應類型的關鍵字
#         cursor.execute("SELECT id, contentGroupKeys FROM shopsKeyWords WHERE shop_id IN (SELECT id FROM shopsData WHERE shopType=?)", (shop_type,))
#         shop_keywords = cursor.fetchall()

#         for keyword_1 in shop_keywords:
#             text1 = keyword_1[1]
#             keyword_1_id = keyword_1[0]  # 獲取 keyword_1 的 id
#             for keyword_2 in shop_keywords:
#                 text2 = keyword_2[1]
#                 keyword_2_id = keyword_2[0]  # 獲取 keyword_2 的 id
#                 similarity_score = calculate_similarity(text1, text2)
#                 if similarity_score is not None:
#                     # 寫入檔案時同時記錄 shop_id
#                     file.write(f"({keyword_1_id},{keyword_2_id},{similarity_score:.4f}),")
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

def getKeyWords4():
    start_time = datetime.now()  # 紀錄函式開始執行的時間

    # 取得資料庫連線
    connect = sqlite3.connect(db)
    cursor = connect.cursor()

    # 定義兩個不同 shopType 的檔案路徑
    file_path_0 = os.path.abspath(os.path.join(current_dir, '..', 'RecommenderSystem', 'similarity_results_0.txt'))
    file_path_1 = os.path.abspath(os.path.join(current_dir, '..', 'RecommenderSystem', 'similarity_results_1.txt'))

    # 處理 shopType=0 的 ShopsKeyWords 物件，並將相似度資料計算出來，寫進 txt 儲存
    process_similarity_results(cursor, file_path_0, shop_type=0)

    # 處理 shopType=1 的 ShopsKeyWords 物件，並將相似度資料計算出來，寫進 txt 儲存
    process_similarity_results(cursor, file_path_1, shop_type=1)

    # 關閉資料庫連線
    cursor.close()
    connect.close()

    end_time = datetime.now()  # 紀錄函式執行結束的時間
    execution_time = end_time - start_time  # 計算函數總執行時間
    print("函數執行時間：", execution_time)
    print('key4成功')

def process_similarity_results(cursor, file_path, shop_type):
    if not os.path.exists(file_path):
        # 如果文件不存在，則創建一個新文件
        open(file_path, 'w').close()

    with open(file_path, 'w', encoding='utf-8') as file:
        # 獲取相應類型的關鍵字
        cursor.execute("SELECT id, contentGroupKeys FROM shopsKeyWords WHERE shop_id IN (SELECT id FROM shopsData WHERE shopType=?)", (shop_type,))
        shop_keywords = cursor.fetchall()

        for keyword_1 in shop_keywords:
            text1 = keyword_1[1]
            keyword_1_id = keyword_1[0]  # 獲取 keyword_1 的 id
            for keyword_2 in shop_keywords:
                text2 = keyword_2[1]
                keyword_2_id = keyword_2[0]  # 獲取 keyword_2 的 id
                similarity_score = calculate_similarity(text1, text2)
                if similarity_score is not None:
                    # 寫入檔案時同時記錄 shop_id
                    file.write(f"({keyword_1_id},{keyword_2_id},{similarity_score:.4f}),")
                else:
                    file.write(f"({keyword_1_id},{keyword_2_id},-1,")
            file.write("\n")
       
def calculate_similarity(text1, text2):
    if text1 is None or text2 is None:
        return -1
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    similarity_score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])

    return similarity_score[0][0]


def getKeyWords5():
    similarity_results_0 = read_similarity_file(file_path_0)
    similarity_results_1 = read_similarity_file(file_path_1)
    merged_similarity_results = similarity_results_0 + similarity_results_1
    print(len(similarity_results_0))

    # 取得資料庫連線
    connect = sqlite3.connect(db)
    cursor = connect.cursor()

    # 取得所有的 ShopsKeyWords 資料
    cursor.execute("SELECT * FROM shopsKeyWords")
    shopsKeyWords = cursor.fetchall()

    for shop, line in zip(shopsKeyWords, merged_similarity_results):
        # 初始化三個列表來存放最大的五個相似度資料、相似的店家景點ID、相似度的分數
        top_5_dict = []
        top_5_ids = []
        top_5_similarities = []

        # 對相似度的分數進行排序，取出前五個
        sorted_similarities = sorted(
            line['similarities'], key=lambda x: x['similarities'], reverse=True)[1:6]
        myid = line['similarities'][0]['myshop_id']
        for similarity in sorted_similarities:
            top_5_dict.append(similarity)  # 添加字典
            top_5_ids.append(similarity['othershop_id'])  # 提取 sim_id
            top_5_similarities.append(similarity['similarities'])  # 提取相似度值
    
        update_query = """
            UPDATE shopsKeyWords 
            SET similarityScore = ?, similarityShop = ? 
            WHERE id = ?
        """
        cursor.execute(update_query, (str(top_5_similarities), str(top_5_ids), shop[0]))

    # 提交事務並關閉資料庫連線
    connect.commit()
    cursor.close()
    connect.close()
    print('key5成功')


def read_similarity_file(file_path):
    similarity_results = []
    with open(file_path, 'r', encoding='utf-8') as file:

        for line in file:
            similarities = []
            # 使用正則表達式提取出txt的資料
            matches = re.findall(
                r'\((\d+),(\d+),(-?\d+\.\d+)\),', line.strip())

            # 對每個字串做處理
            for match in matches:
                keyword_id = int(match[0])
                shop_id = int(match[1])
                score = float(match[2])
                similarities.append(
                    {'myshop_id': keyword_id, 'othershop_id': shop_id, 'similarities': score})
            similarity_results.append({'similarities': similarities})

    return similarity_results



# getKeyWords12()
# time.sleep(3)

# getKeyWords3txt()
# time.sleep(3)

# getKeyWords3()
# time.sleep(3)

getKeyWords4()
time.sleep(3)

# getKeyWords5()