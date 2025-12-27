import os
import psycopg2
import pandas as pd
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

def get_db_connection():
    # .envに書いたDATABASE_URLを使って接続
    return psycopg2.connect(os.getenv("DATABASE_URL"))

@app.get("/analytics/moving-average/{user_id}")
def get_moving_average(user_id: int, window: int = 7):
    try:
        conn = get_db_connection()
        # %s を使ったプレースホルダ形式（SQLインジェクション対策）
        query = "SELECT amount FROM sales WHERE user_id = %s ORDER BY id ASC"
        df = pd.read_sql_query(query, conn, params=(user_id,))
        conn.close()

        if df.empty:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found in PostgreSQL")

        df['moving_avg'] = df['amount'].rolling(window=window).mean()
        result = df['moving_avg'].dropna().tolist()

        return {
            "source": "PostgreSQL (Render)",
            "user_id": user_id,
            "moving_averages": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app = FastAPI()

@app.get("/analytics/moving-average/{user_id}")
def get_moving_average(user_id: int, window: int = 7):
    try:
        # SQLiteの代わりにPostgreSQLへ接続
        url = os.getenv("DATABASE_URL")
        conn = psycopg2.connect(url)
        
        query = "SELECT amount FROM sales WHERE user_id = %s ORDER BY date ASC"
        df = pd.read_sql_query(query, conn, params=(user_id,))
        conn.close()

        if df.empty:
            # ここで発生した 404 を下の except で捕まえないようにする
            raise HTTPException(status_code=404, detail=f"User {user_id} not found in database")

        df['moving_avg'] = df['amount'].rolling(window=window).mean()
        result = df['moving_avg'].dropna().tolist()

        return {
            "user_id": user_id,
            "window_size": window,
            "count": len(result),
            "moving_averages": result
        }

    # HTTPException (404など) はそのままスルーさせる
    except HTTPException as he:
        raise he
    # それ以外の本当の異常（DB接続失敗など）だけを 500 にする
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))