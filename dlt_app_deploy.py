# dlt_app.py
# Streamlit 在线版大乐透智能分析

import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="大乐透智能分析", layout="wide")

st.title("🎯 体彩大乐透 · 智能分析网页应用")

# ============ 数据抓取函数 ============
@st.cache_data(ttl=3600)
def fetch_latest_data():
    try:
        url = "import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 每60分钟自动刷新一次
st_autorefresh(interval=60 * 60 * 1000, key="datarefresh")

st.set_page_config(page_title="大乐透数据分析", layout="wide")
st.title("🎯 大乐透数据分析助手（自动更新版）")

@st.cache_data(ttl=3600)
def fetch_data():
    """从体彩官方公开接口获取最近30期大乐透数据"""
    url = "https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry"
    params = {"gameNo": "85", "pageSize": "30", "pageNo": "1"}
    res = requests.get(url, timeout=10)
    data = res.json()
    df = pd.DataFrame(data["value"]["list"])
    df = df.rename(columns={
        "lotteryDrawNum": "期号",
        "lotteryDrawResult": "开奖号码",
        "lotteryDrawTime": "开奖日期"
    })
    return df[["期号", "开奖号码", "开奖日期"]]

# 抓取数据
try:
    df = fetch_data()
    st.success(f"✅ 数据更新成功！最近一期：{df.iloc[0]['期号']} （{df.iloc[0]['开奖日期']}）")

    # 显示表格
    st.dataframe(df, use_container_width=True, hide_index=True)

    # 分析区
    st.subheader("📊 开奖号码分布分析")
    nums = df["开奖号码"].str.split(" ", expand=True)
    front_nums = nums.iloc[:, :5].astype(int).values.flatten()
    back_nums = nums.iloc[:, 5:].astype(int).values.flatten()

    col1, col2 = st.columns(2)
    with col1:
        st.write("前区号码分布（1-35）")
        front_counts = pd.Series(front_nums).value_counts().sort_index()
        st.bar_chart(front_counts)
    with col2:
        st.write("后区号码分布（1-12）")
        back_counts = pd.Series(back_nums).value_counts().sort_index()
        st.bar_chart(back_counts)

    # 推荐号码
    st.subheader("🎰 智能推荐号码（随机策略）")
    import random
    if st.button("生成推荐号码"):
        front = sorted(random.sample(range(1, 36), 5))
        back = sorted(random.sample(range(1, 13), 2))
        st.success(f"推荐号码：{' '.join(map(str, front))} + {' '.join(map(str, back))}")

except Exception as e:
    st.error(f"❌ 抓取数据失败：{e}")
    st.info("请稍后再试，或手动刷新。")

st.caption("数据来源：中国体育彩票公开接口 ｜ 每60分钟自动刷新一次")
"
        response = requests.get(url, timeout=10)
        data = response.json()
        results = data['value']['list']
        df = pd.DataFrame(results)
        df = df[['lotteryDrawNum','lotteryDrawResult','lotteryDrawTime']]
        df.columns = ['期号','开奖号码','开奖日期']
        df['开奖日期'] = pd.to_datetime(df['开奖日期'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"数据抓取失败：{e}")
        return pd.DataFrame()

# ============ 数据加载 ============
with st.spinner('正在从官网抓取最新大乐透数据...'):
    df = fetch_latest_data()

if not df.empty:
    st.success(f"✅ 已获取最新 {len(df)} 期数据（更新于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}）")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("未能获取数据，请稍后重试或检查网络连接。")

# ============ 统计分析 ============
if not df.empty:
    numbers = df['开奖号码'].str.split(' ', expand=True)
    numbers.columns = ['前1','前2','前3','前4','前5','后1','后2']
    for col in numbers.columns:
        numbers[col] = pd.to_numeric(numbers[col], errors='coerce')

    all_numbers = numbers.melt(var_name='位置', value_name='号码')

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔥 前区号码分布")
        fig1 = px.histogram(all_numbers[all_numbers['位置'].str.contains('前')], x='号码', nbins=35)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("💧 后区号码分布")
        fig2 = px.histogram(all_numbers[all_numbers['位置'].str.contains('后')], x='号码', nbins=12)
        st.plotly_chart(fig2, use_container_width=True)

    # ============ 推荐算法 ============
    st.markdown("---")
    st.subheader("🎲 智能号码推荐")

    def recommend_numbers():
        front_pool = np.arange(1, 36)
        back_pool = np.arange(1, 13)
        np.random.seed(int(pd.Timestamp.now().timestamp()) % 100000)
        front = np.random.choice(front_pool, 5, replace=False)
        back = np.random.choice(back_pool, 2, replace=False)
        return sorted(front), sorted(back)

    if st.button("点击生成推荐号码"):
        front, back = recommend_numbers()
        st.success(f"推荐号码：{' '.join(map(str, front))} + {' '.join(map(str, back))}")

# ============ 自动刷新提示 ============
st.markdown("---")
next_update = datetime.now() + timedelta(minutes=60)
st.info(f"🕒 页面将在 {next_update.strftime('%H:%M')} 自动更新抓取最新数据（每60分钟刷新一次）")
