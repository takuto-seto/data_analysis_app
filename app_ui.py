import streamlit as st
import requests
import pandas as pd

# ページ設定
st.set_page_config(page_title="売上解析ダッシュボード", page_icon="📈", layout="wide")

st.title("📈 リアルタイム売上解析ダッシュボード")
st.caption("PostgreSQL (Render) + FastAPI 連携システム")
st.markdown("---")

# サイドバーの設定
st.sidebar.header("📊 分析パラメータ")
user_id = st.sidebar.number_input("ターゲットユーザーID", min_value=1, max_value=1000, value=999)
window_size = st.sidebar.slider("移動平均の窓サイズ（日）", min_value=3, max_value=30, value=7)

# 実行ボタン
if st.sidebar.button("分析を実行"):
    # 接続先URL (ローカル開発時は localhost:8000)
    url = f"http://127.0.0.1:8000/analytics/moving-average/{user_id}"
    params = {"window": window_size}
    
    try:
        with st.spinner('📡 APIから計算結果を取得中...'):
            response = requests.get(url, params=params, timeout=5) # タイムアウトを設定
            
            if response.status_code == 200:
                res_data = response.json()
                averages = res_data.get("moving_averages", [])
                
                # --- [改善点] 空リストのチェック ---
                if not averages:
                    st.warning(f"⚠️ ユーザー {user_id} はデータ件数が不足しているため、移動平均を計算できません。（窓サイズ: {window_size}）")
                    st.info("解決策: `database_engine.py` でデータを追加挿入してください。")
                else:
                    # レイアウトを2カラムに分ける
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.subheader(f"👤 ユーザー {user_id} の推移グラフ")
                        chart_data = pd.DataFrame(averages, columns=["売上移動平均"])
                        st.line_chart(chart_data)
                    
                    with col2:
                        st.subheader("📈 統計指標")
                        # --- [改善点] 安全なインデックスアクセス ---
                        latest_val = averages[-1] 
                        st.metric("最新の移動平均", f"¥{latest_val:,.0f}")
                        st.metric("データポイント数", f"{len(averages)}件")
                        
                        with st.expander("生データを確認"):
                            st.write(chart_data)
                    
                    st.success("✅ 分析が正常に完了しました。")
            
            elif response.status_code == 404:
                st.warning(f"🔎 ユーザー {user_id} はデータベースに存在しません。")
            else:
                st.error(f"🚫 APIエラーが発生しました (Status: {response.status_code})")
                
    except requests.exceptions.ConnectionError:
        st.error("🔌 接続エラー: APIサーバー（uvicorn）が起動していないようです。ターミナルを確認してください。")
    except Exception as e:
        st.error(f" Unexpected Error: {e}")
else:
    st.info("👈 左のサイドバーからパラメータを選択して「分析を実行」を押してください。")