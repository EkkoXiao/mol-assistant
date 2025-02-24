import streamlit as st
import requests

# FastAPI 服务的地址
API_URL = "https://b3ba-43-247-185-76.ngrok-free.app/generate"

# 页面标题
st.title("Vicuna-7B 对话演示")

# 用户输入
user_input = st.text_input("请输入你的问题：")

# 生成按钮
if st.button("生成回复"):
    if user_input:
        # 调用 FastAPI 服务
        try:
            response = requests.get(
                API_URL,
                params={"input_text": user_input}
            )
            if response.status_code == 200:
                generated_text = response.json()["generated_text"]
                st.write("模型回复：", generated_text)
            else:
                st.error(f"请求失败，状态码：{response.status_code}")
        except Exception as e:
            st.error(f"请求出错：{e}")
    else:
        st.warning("请输入问题！")