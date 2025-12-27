import os
import psycopg2
import pandas as pd
import traceback
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# 1. 環境変数の読み込み
load_dotenv()

# 2. データベースURLの取得と変換
DATABASE_URL = os.getenv("DATABASE_URL")

# Renderの仕様（postgres:// を postgresql:// に置換）
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3. FastAPIのインスタンス化（1回だけでOK）
app = FastAPI()

# 4. ヘルスチェック用ルート（サーバーが生きているか確認用）
@app.get("/")
def read_root():
    return {"status": "ok", "message": "FastAPI on Render is running"}

# 5. メインの分析エンドポイント
@app.get("/analytics/moving-average/{user_id}")
def get_moving_average(user_id: int, window: int = 7):
    # 接続URLの存在チェック
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL is not set")

    try:
        # DB接続
        conn = psycopg2.connect(DATABASE_URL)
        
        # クエリ実行（PostgreSQLでは id または date でソート）
        query = "SELECT amount FROM sales WHERE user_id = %s ORDER BY id ASC"
        df = pd.read_sql_query(query, conn, params=(user_id,))
        conn.close()

        # データ存在チェック
        if df.empty:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found in database")

        # 移動平均の計算
        df['moving_avg'] = df['amount'].rolling(window=window).mean()
        result = df['moving_avg'].dropna().tolist()

        return {
            "user_id": user_id,
            "window_size": window,
            "count": len(result),
            "moving_averages": result,
            "source": "PostgreSQL on Render"
        }

    except HTTPException as he:
        # 404などはそのまま投げる
        raise he
    except Exception as e:
        # 予期せぬエラーは詳細をログに出力しつつ500を返す
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")