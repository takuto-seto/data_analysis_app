import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cur = conn.cursor()
        
        # テストデータの挿入
        cur.execute("INSERT INTO sales (user_id, amount) VALUES (%s, %s)", (999, 1234.56))
        
        # 挿入したデータの確認
        cur.execute("SELECT * FROM sales WHERE user_id = 999;")
        result = cur.fetchone()
        
        conn.commit()
        print(f"取得成功: {result}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"接続エラー: {e}")

if __name__ == "__main__":
    test_connection()