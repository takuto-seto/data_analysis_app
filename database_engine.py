import sqlite3
import time
import random

class DataEngine:
    def __init__(self, db_name="analysis.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._setup_table()

    def _setup_table(self):
        """テーブルの作成"""
        self.cursor.execute("DROP TABLE IF EXISTS sales")
        self.cursor.execute("""
            CREATE TABLE sales (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                amount REAL,
                timestamp DATETIME
            )
        """)
        self.conn.commit()

    def insert_bulk_data(self, n=100000):
        """10万件のダミーデータを挿入"""
        print(f"{n}件のデータを挿入中...")
        data = [(i, random.randint(1, 1000), random.uniform(10, 5000)) for i in range(n)]
        self.cursor.executemany("INSERT INTO sales (id, user_id, amount) VALUES (?, ?, ?)", data)
        self.conn.commit()

    def search_user(self, user_id):
        """特定のユーザーの購入履歴を検索"""
        start = time.time()
        self.cursor.execute("SELECT * FROM sales WHERE user_id = ?", (user_id,))
        results = self.cursor.fetchall()
        end = time.time()
        return end - start, len(results)

    def add_index(self):
        """インデックスを作成"""
        self.cursor.execute("CREATE INDEX idx_user_id ON sales(user_id)")
        self.conn.commit()

if __name__ == "__main__":
    engine = DataEngine()
    engine.insert_bulk_data(100000)

    # 1. インデックスなしでの検索
    t1, count = engine.search_user(500)
    print(f"インデックスなしの検索時間: {t1:.6f} 秒 (ヒット数: {count})")

    # 2. インデックスを追加して検索
    print("インデックスを作成中...")
    engine.add_index()
    t2, count = engine.search_user(500)
    print(f"インデックスありの検索時間: {t2:.6f} 秒 (ヒット数: {count})")
    
    print(f"改善率: {t1/t2:.1f} 倍の高速化")