import streamlit as st
import requests
import pandas as pd
import os

# ページ設定
st.set_page_config(page_title="売上解析ダッシュボード", page_icon="📈", layout="wide")

st.title("📈 リアルタイム売上解析ダッシュボード")
st.caption("PostgreSQL (Render) + FastAPI 連携システム")
st.markdown("---")

# --- [改善ポイント] 接続先URLの動的切り替え ---
# Streamlit CloudのSecretsまたは環境変数から取得。なければローカルを使う
API_BASE_URL = st.secrets.get("API_URL", "http://127.0.0.1:8000")

# サイドバーの設定
st.sidebar.header("📊 分析パラメータ")
user_id = st.sidebar.number_input("ターゲットユーザーID", min_value=1, max_value=1000, value=999)
window_size = st.sidebar.slider("移動平均の窓サイズ（日）", min_value=3, max_value=30, value=7)

# 実行ボタン
if st.sidebar.button("分析を実行"):
    # エンドポイントの構築
    url = f"{API_BASE_URL.rstrip('/')}/analytics/moving-average/{user_id}"
    params = {"window": window_size}
    
    try:
        with st.spinner('📡 クラウドAPIから計算結果を取得中...'):
            # APIリクエスト
            response = requests.get(url, params=params, timeout=10) # スリープ解除を考慮し少し長めに設定
            
            if response.status_code == 200:
                res_data = response.json()
                averages = res_data.get("moving_averages", [])
                
                if not averages:
                    st.warning(f"⚠️ ユーザー {user_id} はデータ件数が不足しているため、移動平均を計算できません。")
                else:
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.subheader(f"👤 ユーザー {user_id} の推移グラフ")
                        chart_data = pd.DataFrame(averages, columns=["売上移動平均"])
                        st.line_chart(chart_data)
                    
                    with col2:
                        st.subheader("📈 統計指標")
                        latest_val = averages[-1] 
                        st.metric("最新の移動平均", f"¥{latest_val:,.0f}")
                        st.metric("データポイント数", f"{len(averages)}件")
                        
                        with st.expander("詳細データ"):
                            st.write(chart_data)
                    
                    st.success(f"✅ API ({res_data.get('source', 'Unknown')}) との通信に成功しました。")
            
            elif response.status_code == 404:
                st.warning(f"🔎 ユーザー {user_id} のデータが見つかりません。")
            else:
                st.error(f"🚫 APIエラー (Status: {response.status_code})\n{response.text}")
                
    except requests.exceptions.Timeout:
        st.error("⏳ タイムアウトしました。Renderの無料枠は起動に時間がかかる場合があります。1分ほど待って再試行してください。")
    except requests.exceptions.ConnectionError:
        st.error(f"🔌 接続エラー: APIサーバー ({API_BASE_URL}) に接続できません。")
    except Exception as e:
        st.error(f" Unexpected Error: {e}")
else:
    st.info("👈 左のサイドバーからパラメータを選択して「分析を実行」を押してください。")