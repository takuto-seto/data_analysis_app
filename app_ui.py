import streamlit as st
import requests
import pandas as pd

# ページ設定
st.set_page_config(page_title="売上解析ダッシュボード", page_icon="📈")

st.title("📈 リアルタイム売上解析ダッシュボード")
st.markdown("---")

# サイドバーの設定
st.sidebar.header("分析パラメータ")
user_id = st.sidebar.number_input("ターゲットユーザーID", min_value=1, max_value=1000, value=100)
window_size = st.sidebar.slider("移動平均の窓サイズ（日）", min_value=3, max_value=30, value=7)

# 実行ボタン
if st.sidebar.button("分析を実行"):
    # FastAPIのエンドポイントURL（ポート8000で起動している前提）
    url = f"http://127.0.0.1:8000/analytics/moving-average/{user_id}"
    params = {"window": window_size}
    
    try:
        with st.spinner('APIから計算結果を取得中...'):
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                res_data = response.json()
                averages = res_data["moving_averages"]
                
                # レイアウトを2カラムに分ける
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.subheader(f"ユーザー {user_id} の移動平均推移")
                    chart_data = pd.DataFrame(averages, columns=["売上移動平均"])
                    st.line_chart(chart_data)
                
                with col2:
                    st.subheader("統計")
                    latest_val = averages[-1]
                    st.metric("最新平均", f"¥{latest_val:,.0f}")
                    st.write(f"データ件数: {len(averages)}件")
                    
                st.success("分析が正常に完了しました。")
            
            elif response.status_code == 404:
                st.warning(f"ユーザー {user_id} のデータが見つかりません。")
            else:
                st.error(f"APIエラーが発生しました (Status: {response.status_code})")
                
    except Exception as e:
        st.error(f"接続エラー: APIサーバーが起動しているか確認してください。\n{e}")
else:
    st.info("左のサイドバーからパラメータを選択して「分析を実行」を押してください。")