import pandas as pd


def example_read_csv():
    # 定義要讀取的欄位
    columns_to_read = ['comments_id', 'user_id_1', 'comment_1']

    # 讀取CSV，僅讀取指定的欄位
    data = pd.read_csv('113.csv', usecols=columns_to_read)
    data.rename(columns={'user_id_1': 'user'}, inplace=True)
    data.rename(columns={'comment_1': 'comment'}, inplace=True)

    # 顯示讀取的數據
    print(data)
# example_read_csv()

    
def data_clear():
    columns_to_read1 = ['shopName', 'user_id_1', 'comment_1']
    data1 = pd.read_csv('113.csv', usecols=columns_to_read1)
    columns_to_read2 = ['shopName', 'user_id_2', 'comment_2']
    data2 = pd.read_csv('113.csv', usecols=columns_to_read2)
    columns_to_read3 = ['shopName', 'user_id_3', 'comment_3']
    data3 = pd.read_csv('113.csv', usecols=columns_to_read3)

    data1.rename(columns={'user_id_1': 'user'}, inplace=True)
    data1.rename(columns={'comment_1': 'comment'}, inplace=True)
    data2.rename(columns={'user_id_2': 'user'}, inplace=True)
    data2.rename(columns={'comment_2': 'comment'}, inplace=True)
    data3.rename(columns={'user_id_3': 'user'}, inplace=True)
    data3.rename(columns={'comment_3': 'comment'}, inplace=True)
    df_1 = pd.merge(data1, data2, how='outer')
    df = pd.merge(df_1, data3, how='outer')
    df.to_csv('clean_data.csv', index=False, encoding='utf_8_sig')
    print(df)
# data_clear()

def write_to_sqlite():
    import sqlite3
    data = pd.read_csv('clean_data.csv')
    db_name = r'db.sqlite3'

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    data = data.dropna(subset=['content'])
    data.to_sql('Messages', conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()

write_to_sqlite()