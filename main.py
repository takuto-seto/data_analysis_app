from fastapi import FastAPI, HTTPException
import pandas as pd
import sqlite3
import traceback # デバッグ用

app = FastAPI()

@app.get("/analytics/moving-average/{user_id}")
def get_moving_average(user_id: int, window: int = 7):
    try:
        conn = sqlite3.connect("analysis.db")
        query = "SELECT amount FROM sales WHERE user_id = ?"
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