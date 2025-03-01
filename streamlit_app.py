import re
import time
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
    st.session_state.messages.append({"role": "assistant", "content": "你好！我是用于医药反应交互的大语言模型助手。请问您有什么问题？我将根据提供的药物数据及相互作用预测结果，并结合现有医学权威数据进行解答。"})
if "drugs" not in st.session_state:
    st.session_state.drugs = []
if "interactions" not in st.session_state:
    st.session_state.interactions = []
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
                drug_idx = [idx for idx, drug in enumerate(st.session_state.drugs) if drug["name"] == drug_name]
                if drug_idx != []:
                    st.error("药物已输入！")
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
                        new_idx = len(st.session_state.drugs)
                        success = True
                        st.session_state.messages.append({"role": "system", "content": f"新增药物信息：药物名{drug_name}，药物性质信息{drug_property}，药物靶点信息{drug_target}"})
                        for idx, drug in enumerate(st.session_state.drugs):
                            time.sleep(5)
                            response = requests.get(
                                f"{API_URL}/interaction",
                                json={
                                    "drug1": drug_data,
                                    "drug2": drug
                                }
                            )
                            if response.status_code == 200:
                                interactions = response.json()["interactions"]
                                st.session_state.interactions.append({idx * 10 + new_idx: interactions})
                                interaction_text = "\n".join(
                                    [f"- \"{desc}\"  ({prob * 100:.2f}%)" for desc, (prob, _) in interactions.items()]
                                )
                                drug1_name = drug_data["name"]
                                drug2_name = drug["name"]
                                st.session_state.messages.append({"role": "system", "content": f"新增药物反应信息：药物{drug1_name}与药物{drug2_name}联合使用可能发生相互作用，以下是可能的反应类型及其概率：{interaction_text}"})
                            else:
                                success = False
                                st.error(f"请求失败，状态码：{response.status_code}")
                                st.error(f"错误详情：{response.text}")
                        if success:
                            st.session_state.drugs.append(drug_data)
                            st.success(f"药物 {drug_name} 信息已成功输入！")
                    else:
                        st.error(f"请求失败，状态码：{response.status_code}")
                        st.error(f"错误详情：{response.text}")
                except Exception as e:
                    st.error(f"请求出错：{str(e)}")

    delete_all_button = st.button("删除所有药物", key="delete_all", help="删除所有已保存的药物", use_container_width=True, 
                                  on_click=lambda: (st.session_state.pop('drugs', None), st.session_state.pop('interactions', None)))

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
if tab == "💊 **药物信息**":
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


if tab == "🔬 **药物反应预测**":
    st.subheader("选择需要查看反应的药物")

    if "drugs" in st.session_state and len(st.session_state.drugs) > 0:
        drug_names = [drug["name"] for drug in st.session_state.drugs]

        drug1 = st.selectbox("选择药物 1", options=drug_names, key="drug1")
        drug2 = st.selectbox("选择药物 2", options=drug_names, key="drug2")
 
        st.write(f"你选择的药物是: {drug1} 和 {drug2}")

        if st.button("显示药物反应"):
            if drug1 == drug2:
                st.write(f"不能选择相同药物！")
            # 在此处编写药物反应逻辑
            else:
                drug1_idx = next((idx for idx, drug in enumerate(st.session_state.drugs) if drug["name"] == drug1), None)
                drug2_idx = next((idx for idx, drug in enumerate(st.session_state.drugs) if drug["name"] == drug2), None)
                idx_key = min(drug1_idx, drug2_idx) * 10 + max(drug1_idx, drug2_idx)

                interactions = next((pair[idx_key] for pair in st.session_state.interactions if idx_key in pair), None)
            
                st.subheader("反应类型及可能性")
                html_code = """
                <style>
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }
                th, td {
                    text-align: left;
                    padding: 8px;
                    border: 1px solid #ddd;
                }
                th {
                    background-color: #f2f2f2;
                    font-weight: bold;
                }
                </style>
                <table>
                <tr>
                    <th>反应类型</th>
                    <th>可能性 (%)</th>
                </tr>
                """

                for reaction_type, (probability, idx) in interactions.items():
                    html_code += f"<tr><td>{reaction_type}</td><td>{probability * 100:.2f}</td></tr>"

                html_code += "</table>"
                st.markdown(html_code, unsafe_allow_html=True)
    else:
        st.write("没有任何药物记录！")


# 用来切换选中药物的函数
def toggle_drug_selection(drug_name, selected_drugs):
    if drug_name in selected_drugs:
        selected_drugs.remove(drug_name)
    elif len(selected_drugs) < 2:
        selected_drugs.append(drug_name)
    st.session_state.selected_drugs = selected_drugs

if tab == "🗣️ **对话系统**":
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("请输入您的问题"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            messages = st.session_state.messages.copy()
            messages.append({"role": "system", "content": "如果上述问题涉及生物医药，请基于全球权威指南（如NCCN、ESMO）、高循证等级的临床试验数据（如III期随机对照试验，RCT）以及相关研究数据库，提供详细分析和量化评估。"})
            response = requests.post(
                f"{API_URL}generate",
                json={"messages": messages}
            )
            if response.status_code == 200:
                generated_text = response.json()["generated_text"]
                answer = re.sub(r'<think>.*?</think>', '', generated_text, flags=re.DOTALL)

                with st.chat_message("assistant"):
                    st.markdown(answer)

                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error(f"请求失败，状态码：{response.status_code}")
                st.error(f"错误详情：{response.text}")

        except Exception as e:
            st.error(f"请求出错：{e}")