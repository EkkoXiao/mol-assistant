import requests
import streamlit as st

# 设置页面标题和样式
st.set_page_config(page_title="药物反应助手", page_icon="💊", layout="wide")

@st.cache_resource
def load_html(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

API_URL = "https://f895-43-247-185-76.ngrok-free.app/"

# # 调用缓存函数
# html_content = load_html("style.html")
# 使用CSS来定制样式
# st.markdown(html_content, unsafe_allow_html=True)

# 初始化聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "你是一名医药反应交互的大语言模型助手，请详细准确地回答用户提出的问题。"}]

# 创建左侧sidebar
with st.sidebar:
    st.header("药物信息输入")
    
    # 使用form包裹输入内容
    with st.form(key="drug_form", clear_on_submit=True):
        drug_name = st.text_input("药物名称",)
        drug_property = st.text_area("药物性质信息（非必填）")
        drug_target = st.text_input("药物靶点（非必填）")
        drug_smiles = st.text_input("药物SMILES（非必填）")
        
        # 提交按钮
        submit_button = st.form_submit_button(label="提交药物信息", use_container_width=True)

        # 提交后处理数据
        if submit_button:
            if drug_name:
                try: 
                    response = requests.get(
                        f"{API_URL}/info",
                        json={
                            "drug": 
                            {
                                "name": drug_name,
                                "property": drug_property,
                                "target": drug_target,
                                "smiles": drug_smiles,
                            }
                        }
                    )
                    if response.status_code == 200:
                        drug_data = response.json()
                        if "drugs" not in st.session_state:
                            st.session_state.drugs = []
                        st.session_state.drugs.append(drug_data)
                        st.success(f"药物 {drug_name} 信息已成功输入！")
                    else:
                        st.error(f"请求失败，状态码：{response.status_code}")
                        st.error(f"错误详情：{response.text}")
                except Exception as e:
                    st.error(f"请求出错：{str(e)}")

    delete_all_button = st.button("删除所有药物", key="delete_all", help="删除所有已保存的药物", use_container_width=True, 
                                  on_click=lambda: st.session_state.pop('drugs', None))

    if delete_all_button:
        st.success("所有药物已删除！")

# 主页面内容
st.title("药物反应助手")

tab = st.radio(label="选择功能", options=[
    "💊 **药物信息**",
    "🔬 **药物反应预测**",
    "🗣️ **对话系统**"],
    captions=[
    "药物详细信息展示",
    "进行药物对之间反应预测",
    "与生物医药大模型对话"],
    horizontal=True, label_visibility="collapsed")
if tab == "药物信息":
    st.subheader("已提交的药物卡片")
    # 显示所有药物卡片
    if "drugs" in st.session_state and len(st.session_state.drugs) > 0:
        # 创建三列布局
        cols = st.columns(3)
        for i, drug in enumerate(st.session_state.drugs):
            # 每个药物显示一个卡片，使用 modulos 来分配卡片到各列
            col = cols[i % 3]  # 循环放入三列
            with col:
                # 使用Markdown内嵌HTML格式的卡片样式
                card_html = f"""
                <div style="background-image: url('https://cdn.jsdelivr.net/gh/EkkoXiao/BlogPic/Form.jpg'); background-size: cover; background-position: left; border-radius: 15px; padding: 20px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); text-align: left;">
                    <h3>{drug['name']}</h3>
                    <p><strong>性质信息:</strong> {drug['property'] if drug['property'] != "" else "暂无信息"}</p>
                    <p><strong>靶点信息:</strong> {drug['target'] if drug['target'] != "" else "暂无信息"}</p>
                    <p><strong>SMILES序列:</strong> {drug['smiles'] if drug['smiles'] != "" else "暂无信息"}</p>
                </div>
                """
                # 渲染HTML内容
                st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.write("没有任何药物记录！")


if tab == "药物反应预测":
    st.subheader("药物选择按钮")

    if "drugs" in st.session_state and len(st.session_state.drugs) > 0:
        drug_names = [drug["name"] for drug in st.session_state.drugs]

        drug1 = st.selectbox("选择第一个药物", options=drug_names, key="drug1")
        drug2 = st.selectbox("选择第二个药物", options=drug_names, key="drug2")
 
        st.write(f"你选择的药物是: {drug1} 和 {drug2}")

        if st.button("显示药物反应"):
            if drug1 == drug2:
                st.write(f"不能选择相同药物！")
            # 在此处编写药物反应逻辑
            else:
                drug1_info = [drug for drug in st.session_state.drugs if drug["name"] == drug1][0]
                drug2_info = [drug for drug in st.session_state.drugs if drug["name"] == drug2][0]
                try: 
                    response = requests.get(
                        f"{API_URL}/interaction",
                        json={
                            "drug1": drug1_info,
                            "drug2": drug2_info
                        }
                    )
                    if response.status_code == 200:
                        interactions = response.json()["interactions"]
                        severity = response.json()["severity"]
                        st.subheader("反应类型及可能性")
                        interaction_text = ""
                        for reaction_type, probability in response.json()["interactions"].items():
                            interaction_text += f"**{reaction_type}:** {probability * 100}%  "

                        st.markdown(interaction_text)

                        st.subheader("严重程度")
                        st.markdown(f"{response.json()['severity']}")
                    else:
                        st.error(f"请求失败，状态码：{response.status_code}")
                        st.error(f"错误详情：{response.text}")
                except Exception as e:
                    st.error(f"请求出错：{str(e)}")

    else:
        st.write("没有任何药物记录！")


# 用来切换选中药物的函数
def toggle_drug_selection(drug_name, selected_drugs):
    if drug_name in selected_drugs:
        selected_drugs.remove(drug_name)
    elif len(selected_drugs) < 2:
        selected_drugs.append(drug_name)
    st.session_state.selected_drugs = selected_drugs

if tab == "对话系统":
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What is up?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
            response = requests.post(
                f"{API_URL}generate",
                json={"messages": st.session_state.messages}
            )
            if response.status_code == 200:
                generated_text = response.json()["generated_text"]
            else:
                st.error(f"请求失败，状态码：{response.status_code}")
                st.error(f"错误详情：{response.text}")

        except Exception as e:
            st.error(f"请求出错：{e}")

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(generated_text)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": generated_text})