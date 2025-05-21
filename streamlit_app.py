import itertools
import json
import random
import re
import time
import pandas as pd
import requests
import streamlit as st

# 设置页面标题和样式
st.set_page_config(page_title="联合用药助手", page_icon="💊", layout="wide")

@st.cache_resource
def load_html(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

API_URL = "https://a11d-43-247-185-76.ngrok-free.app/"

# 调用缓存函数
html_content = load_html("page.html")

st.markdown(html_content, unsafe_allow_html=True)

# 功能 A 
if "messages" not in st.session_state:
    st.session_state.messages = []
if "drugs" not in st.session_state:
    st.session_state.drugs = []
if "interactions" not in st.session_state:
    st.session_state.interactions = []
if "greetings" not in st.session_state:
    st.session_state.greetings = False
if "button_pressed" not in st.session_state:
    st.session_state.button_pressed = ""
if "disabled" not in st.session_state:
    st.session_state.disabled = False
if "selected_drugs" not in st.session_state:
    st.session_state.selected_drugs = []
if "cancer_reply" not in st.session_state:
    st.session_state.cancer_reply = ""

# 功能 B
if "cancer_type" not in st.session_state:
    st.session_state.cancer_type = None
if "selected_targets" not in st.session_state:
    st.session_state.selected_targets = []
if "cancer_targets" not in st.session_state:
    st.session_state.cancer_targets = []
if "recommendation_result" not in st.session_state:
    st.session_state.recommendation_result = []

# 创建左侧sidebar
with st.sidebar:
    st.title("请选择需要的功能")
    function = st.radio(" ", ["💊 联合用药反应评估助手", "🧬 抗癌药物组合推荐助手"], index=None, label_visibility="collapsed",
                        captions=["输入药物组合信息，评估其联用时潜在的协同药效与不良反应等。适用于临床前验证等场景。",
                                  "基于大数据与模型推理，为特定癌症类型推荐潜力组合。适用于治疗方案的设计等。"])

    if function == "💊 联合用药反应评估助手":
        st.header("📝 药物信息输入")
        
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
                if drug_name and drug_property and drug_target and drug_smiles:
                    drug_idx = [idx for idx, drug in enumerate(st.session_state.drugs) if drug["name"].lower() == drug_name.lower()]
                    if drug_idx != []:
                        st.error("该药物已输入！")
                    drug_data = {
                        "name": drug_name,
                        "property": drug_property,
                        "target": drug_target,
                        "smiles": drug_smiles,
                    }
                    new_idx = len(st.session_state.drugs)
                    success = True
                    try:
                        for idx, drug in enumerate(st.session_state.drugs):
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
                                st.session_state.messages.append({"role": "system", "content": f"<DRUG>新增药物反应信息：药物{drug1_name}与药物{drug2_name}联合使用可能发生相互作用，以下是可能的反应类型及其概率：{interaction_text}"})
                            else:
                                success = False
                                st.error(f"查询药物相互作用出错！请检查药物信息及SMILES序列合法性！")
                    except Exception as e:
                        success = False
                        st.error(f"服务器繁忙！请稍后再试！")
                    if success:
                        st.session_state.drugs.append(drug_data)
                        st.session_state.messages.append({"role": "system", "content": f"<DRUG>新增药物信息：药物名{drug_data['name']}，药物性质信息{drug_data['property']}，药物靶点信息{drug_data['target']}"})
                        st.success(f"药物信息已直接导入！")
                elif drug_name:
                    drug_idx = [idx for idx, drug in enumerate(st.session_state.drugs) if drug["name"].lower() == drug_name.lower()]
                    if drug_idx != []:
                        st.error("该药物已输入！")
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
                            try:
                                for idx, drug in enumerate(st.session_state.drugs):
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
                                        st.session_state.messages.append({"role": "system", "content": f"<DRUG>新增药物反应信息：药物{drug1_name}与药物{drug2_name}联合使用可能发生相互作用，以下是可能的反应类型及其概率值：{interaction_text}"})
                                    else:
                                        success = False
                                        st.error(f"查询药物相互作用出错！请检查药物信息")
                            except Exception as e:
                                success = False
                                st.error(f"服务器繁忙！请稍后再试！")
                            if success:
                                st.session_state.drugs.append(drug_data)
                                st.session_state.messages.append({"role": "system", "content": f"<DRUG>新增药物信息：药物名{drug_data['name']}，药物性质信息{drug_data['property']}，药物靶点信息{drug_data['target']}"})
                                st.success(f"药物信息查询并导入成功！")
                        elif response.status_code == 404:
                            st.error("未查询到该药物，请确定输入为标准英文药物名称！")
                        else:
                            st.error("药物信息导入出错！")
                    except Exception as e:
                        st.error(f"服务器繁忙！请稍后再试！")

        delete_all_button = st.button(
            "删除所有药物", 
            key="delete_all", 
            help="删除所有已保存的药物", 
            use_container_width=True, 
            on_click=lambda: (
                st.session_state.pop('drugs', None),
                st.session_state.pop('interactions', None),
                setattr(st.session_state, "messages", [msg for msg in st.session_state.get("messages", []) 
                                                    if not (msg["role"] == "system" and msg["content"].startswith("<DRUG>"))])
            )
        )
        if delete_all_button:
            st.success("所有药物信息记录已删除！")

    elif function == "🧬 抗癌药物组合推荐助手":
        st.header("📝 请选择癌症类型")

        cancer_type = st.selectbox(
            "📝 请选择癌症类型",
            ["乳腺癌", "胃癌", "肠癌", "肝癌"],
            label_visibility="collapsed",
            index=(
                ["乳腺癌", "胃癌", "肠癌", "肝癌"].index(st.session_state.cancer_type)
                if st.session_state.cancer_type in ["乳腺癌", "胃癌", "肠癌", "肝癌"]
                else None
            ),
        )

        confirm_button = st.button(
            "确定",
            use_container_width=True, 
        )

        if confirm_button:
            st.session_state.cancer_targets = []
            st.session_state.selected_targets = []
            st.session_state.recommendation_result = []
            if cancer_type is None:
                st.warning("⚠️ 请选择一种癌症类型后再点击确定")
            else:
                st.session_state.cancer_type = cancer_type
                st.success(f"✅ 已选择癌症类型：{cancer_type}")

                # TODO 调用后端，获取癌症对应靶点信息
                def get_cancer_targets(cancer_type):
                    cancers = {
                        "乳腺癌": [{"name": "乳腺癌靶点1", "info": "其他信息"},{"name": "乳腺癌靶点2", "info": "其他信息"}],
                        "胃癌": [{"name": "胃癌靶点1", "info": "其他信息"},{"name": "胃癌靶点2", "info": "其他信息"}],
                        "肠癌": [{"name": "肠癌靶点1", "info": "其他信息"},{"name": "肠癌靶点2", "info": "其他信息"}],
                        "肝癌": [{"name": "肝癌靶点1", "info": "其他信息"},{"name": "肝癌靶点2", "info": "其他信息"}],
                    }
                    return cancers[cancer_type]
                
                st.session_state.cancer_targets = get_cancer_targets(st.session_state.cancer_type)

# 主页面内容
if function == None:
    st.title("欢迎使用多功能联合用药助手")
    st.info("👈 请在左侧选择需要的功能以开始使用")

elif function == "💊 联合用药反应评估助手":

    st.title("💊 联合用药反应评估助手")
    tab = st.radio(label="选择功能", options=[
        "💊 **药物信息**",
        "🔬 **药物反应预测**",
        "🧬 **抗癌联用药效预测**",
        "💬 **自由对话**"],
        captions=[
        "药物详细信息展示",
        "进行药物对之间反应预测",
        "预测抗癌药物联合使用的疗效",
        "与生物医药大模型进行自由对话交流"],
        horizontal=True, label_visibility="collapsed")

    if tab == "💊 **药物信息**":
        st.subheader("📜 已收录的药物信息")
        # 显示所有药物卡片
        if "drugs" in st.session_state and len(st.session_state.drugs) > 0:
            # 创建三列布局
            cols = st.columns(3)
            for i, drug in enumerate(st.session_state.drugs):
                col = cols[i % 3]
                with col:
                    card_html = f"""
                    <div style="background-image: url('https://cdn.jsdelivr.net/gh/EkkoXiao/BlogPic/Form.jpg'); 
                                background-size: cover; 
                                background-position: left; 
                                border-radius: 15px; 
                                padding: 20px; 
                                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); 
                                text-align: left; 
                                min-height: 300px; /* 固定高度 */
                                display: flex;
                                flex-direction: column;">
                        <h3 style="margin: 0; font-size: 1.2em;">{drug['name']}</h3>
                        <div style="flex-grow: 1; overflow-y: auto; max-height: 300px; min-height: 300px; padding-right: 5px;"> 
                            <p style="margin: 5px 0; font-size: 0.9em;"><strong>性质信息:</strong> {drug['property'] if drug['property'] != "" else "暂无信息"}</p>
                            <p style="margin: 5px 0; font-size: 0.9em;"><strong>靶点信息:</strong> {drug['target'] if drug['target'] != "" else "暂无信息"}</p>
                            <p style="margin: 5px 0; font-size: 0.9em;"><strong>SMILES序列:</strong> {drug['smiles'] if drug['smiles'] != "" else "暂无信息"}</p>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.warning("⚠️ 当前没有收录的药物，请先添加药物信息！")


    if tab == "🔬 **药物反应预测**":
        st.subheader("🔍 选择需要查看反应的药物")

        if "drugs" in st.session_state and len(st.session_state.drugs) > 0:
            drug_names = [drug["name"] for drug in st.session_state.drugs]

            drug1 = st.selectbox("选择药物 1", options=drug_names, key="drug1")
            drug2 = st.selectbox("选择药物 2", options=drug_names, key="drug2")
    
            st.write(f"你选择的药物是: {drug1} 和 {drug2}")

            if st.button("⚡ 显示药物反应"):
                if drug1 == drug2:
                    st.warning(f"不能选择相同药物！")
                else:
                    drug1_idx = next((idx for idx, drug in enumerate(st.session_state.drugs) if drug["name"] == drug1), None)
                    drug2_idx = next((idx for idx, drug in enumerate(st.session_state.drugs) if drug["name"] == drug2), None)
                    idx_key = min(drug1_idx, drug2_idx) * 10 + max(drug1_idx, drug2_idx)

                    interactions = next((pair[idx_key] for pair in st.session_state.interactions if idx_key in pair), None)
                
                    st.subheader("反应类型及可能性")

                    df = pd.DataFrame(interactions.items(), columns=['交互类型', '数据'])
                    df[['可能性(%)', '索引']] = pd.DataFrame(df['数据'].tolist(), index=df.index)
                    df = df[['交互类型', '可能性(%)']]

                    df['可能性(%)'] = df['可能性(%)'].mul(100).round(2)

                    df = df.sort_values(by='可能性(%)', ascending=False).head(5)

                    st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ 当前没有可选的药物，请先添加药物信息！")

    # 用来切换选中药物的函数
    def toggle_drug_selection(drug_name, selected_drugs):
        if drug_name in selected_drugs:
            selected_drugs.remove(drug_name)
        elif len(selected_drugs) < 2:
            selected_drugs.append(drug_name)
        st.session_state.selected_drugs = selected_drugs

    if tab == "🧬 **抗癌联用药效预测**":
        st.subheader("🔬 抗癌联用药效预测")

        cancer_type = st.radio(
            "请选择癌症类型",
            ["乳腺癌", "肠癌", "胃癌", "肝癌"],
            horizontal=True,
            index=0
        )

        options = [drug["name"] for drug in st.session_state.drugs]

        def update_selected_drugs():
            st.session_state.selected_drugs = st.session_state.selected_drugs_current

        if not options:
            st.warning("⚠️ 当前没有可选的药物，请先添加药物信息！")
        else:
            st.multiselect(
                "请选择至少两种药物", 
                options, 
                default=st.session_state.selected_drugs,  # 设定默认值
                key="selected_drugs_current",  # 绑定到一个临时变量
                placeholder="请选择已收录的药物名称",
                on_change=update_selected_drugs  # 当选择变化时调用回调函数
            )

            cancer_button = st.button("🔍 查看联合药效预测")

            response_placeholder = st.empty()
            response_placeholder.markdown(st.session_state.cancer_reply)

            if cancer_button:
                if len(st.session_state.selected_drugs) < 2:
                    st.warning("请选择至少两种药物进行联合预测！")
                else:
                    drug_information = [drug for drug in st.session_state.drugs if drug["name"] in st.session_state.selected_drugs]
                    drug_index = [idx for idx, drug in enumerate(st.session_state.drugs) if drug["name"] in st.session_state.selected_drugs]
                    drug_interaction_keys = [min(a, b) * 10 + max(a, b) for a, b in itertools.combinations(drug_index, 2)]

                    prompt_cancer = f"以下为几种用于{cancer_type}治疗的药物信息：\n"
                    for drug in drug_information:
                        prompt_cancer += f"药物名称{drug['name']}，药物性质简要信息{drug['property']}，药物靶点信息{drug['target']}, 药物可能的SMILES序列{drug['smiles']}\n"
                    prompt_cancer += "以下为他们之间相互作用不良反应及协同药效的可能的预测信息及发生可能性，该结果并非权威数据，仅供可能的参考所用。\n"
                    for key in drug_interaction_keys:
                        interactions = next((pair[key] for pair in st.session_state.interactions if key in pair), None)
                        drug1 = st.session_state.drugs[key // 10]['name']
                        drug2 = st.session_state.drugs[key % 10]['name']

                        interaction_text = "\n".join(
                            [f"- \"{desc}\"  ({prob * 100:.2f}%)" for desc, (prob, _) in interactions.items()]
                        )
                        prompt_cancer += f"药物{drug1}与{drug2}联合用药可能有如下情况出现：{interaction_text}\n"

                    prompt_cancer += f"关于{cancer_type}治疗中上述几种药物联合用药与单药相比在有效性和安全性方面的差异，请基于全球权威指南（如NCCN、ESMO）、高循证等级的临床试验数据（如III期随机对照试验，RCT）以及相关研究数据库，提供详细的分析与说明，可能用做参考的量化评估数据例如：总生存期（OS），无进展生存期（PFS），客观缓解率（ORR），3 级及以上不良事件发生率，治疗相关死亡率等"
                    
                    try:
                        decoder = json.JSONDecoder()
                        think = True
                        answer = "🔄 模型连接中..."
                        response_placeholder.markdown(answer)

                        response = requests.post(
                            f"{API_URL}stream",
                            json={"messages": [{"role": "user", "content": prompt_cancer}]},
                            stream=True
                        )
                        answer = "⏳ 结果生成中，请稍加等待..."

                        for chunk in response.iter_lines():
                            chunk = chunk.decode("utf-8")
                            try:
                                obj, end = decoder.raw_decode(chunk)
                                word = obj['message']['content']
                                if not think:
                                    answer += word
                                    response_placeholder.markdown(answer + "▌")
                                    st.session_state.cancer_reply = answer
                                else:
                                    response_placeholder.markdown(answer)
                                if word == "</think>":
                                    think = False
                                    answer = ""
                            except json.JSONDecodeError:
                                st.error("大模型生成解析出错！请稍后再试！")
                        
                        response_placeholder.markdown(answer)

                    except Exception as e:
                        st.error(f"服务器繁忙！请稍后再试！")
                    

    example_prompts = [
        "请列出当前系统已收录的药物信息，包括药物名称、简介以及靶点信息",
        "请分析当前收录的药物在联合使用时可能产生的协同作用和拮抗作用",
        "当前收录的药物在治疗癌症上是否具有临床意义，请进行疗效与风险评估"
    ]

    if tab == "💬 **自由对话**":
        # Display chat messages from history on app rerun
        if not st.session_state.greetings:
            st.session_state.messages.append({"role": "system", "content": "你是一名医药反应交互的大语言模型助手，请详细准确地回答用户提出的问题。"})
            st.session_state.messages.append({"role": "assistant", "content": "你好！我是用于医药反应交互的大语言模型助手。请问您有什么问题？我将根据提供的药物数据及相互作用预测结果，并结合现有医学权威数据进行解答。"})
            st.session_state.greetings = True
        
        for message in st.session_state.messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        def set_example(prompt):
            st.session_state.button_pressed = prompt
            st.session_state.disabled = True

        button_cols = st.columns(3)

        button_cols[0].button(example_prompts[0], on_click=set_example, args=(example_prompts[0],), disabled=st.session_state.disabled)
        button_cols[1].button(example_prompts[1], on_click=set_example, args=(example_prompts[1],), disabled=st.session_state.disabled)
        button_cols[2].button(example_prompts[2], on_click=set_example, args=(example_prompts[2],), disabled=st.session_state.disabled)

        # React to user input
        if prompt := (st.chat_input("请输入您的问题") or st.session_state.button_pressed):
            st.session_state.disabled = False
            st.session_state.button_pressed = ""
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            try:
                messages = st.session_state.messages.copy()
                messages.append({"role": "system", "content": "如果上述问题涉及生物医药，请基于全球权威指南（如NCCN、ESMO）、高循证等级的临床试验数据（如III期随机对照试验，RCT）以及相关研究数据库，提供详细的原因分析和量化评估，提供的药物反应预测概率数据可能有误，请仔细辨别。"})
                with st.chat_message("assistant"):
                    answer = "模型连接中..."
                    response_placeholder = st.empty()
                    response_placeholder.markdown(answer)

                    response = requests.post(
                        f"{API_URL}/stream",
                        json={"messages": messages},
                        stream=True
                    )
                    answer = "结果生成中，请稍加等待..."
                    
                    decoder = json.JSONDecoder()
                    think = True

                    st.session_state.messages.append({"role": "assistant", "content": ""})

                    for chunk in response.iter_lines():
                        chunk = chunk.decode("utf-8")
                        try:
                            obj, end = decoder.raw_decode(chunk)
                            word = obj['message']['content']
                            if not think:
                                answer += word
                                response_placeholder.markdown(answer + "▌")
                                st.session_state.messages[-1]['content'] = answer
                            else:
                                response_placeholder.markdown(answer)
                            if word == "</think>":
                                think = False
                                answer = ""
                        except json.JSONDecodeError:
                            st.error("大模型生成解析出错！请稍后再试！")
                    
                    response_placeholder.markdown(answer)
                    st.session_state.messages[-1]['content'] = answer

                    st.rerun()

            except Exception as e:
                st.error(f"服务器繁忙！请稍后再试！")

                st.rerun()

elif function == "🧬 抗癌药物组合推荐助手":

    st.title("🧬 抗癌药物组合推荐助手")
    if st.session_state.cancer_type != None:
        st.info(f"当前已选择癌症：♋ {st.session_state.cancer_type}")
    else:
        st.warning("⚠️ 请选择癌症类型")

    def update_selected_targets():
        st.session_state.selected_targets = st.session_state.selected_targets_current

    if st.session_state.cancer_targets:
        selected = st.multiselect(
            "🎯 请选择目标靶点",
            default=st.session_state.get("selected_targets", []),
            options=st.session_state.cancer_targets,
            on_change=update_selected_targets,
            format_func=lambda x: x["name"],
            key="selected_targets_current"
        )

        # if selected:
        #     st.session_state.selected_targets = selected
        
        st.json(st.session_state.selected_targets)

        # TODO: 根据靶点信息进行药物组合推荐
        def drug_recommendation(targets):
            # 根据靶点获得所有药物，可以访问后端实现
            all_drugs = [
            {
                "target": t["name"],
                "drug": f"{t['name']}的药物",
                "score": round(random.uniform(0, 1), 3)  # DTI 的分数
            }
            for t in st.session_state.selected_targets]
            # TODO: 根据药物以及 DDI 结果，获得药物组合
            # TODO: 访问 DDI 模型参照 L88 开始的内容，路径是 {API_URL}/interaction
            # TODO: 可以访问大语言模型 (Deepseek32b) 生成解释，路径是 {API_URL}/generate
            combo_recommendations = []
            for d1, d2 in itertools.combinations(all_drugs, 2):
                avg_score = round((d1["score"] + d2["score"]) / 2, 3)
                combo = {
                    "drug1": d1["drug"],
                    "drug2": d2["drug"],
                    "score": avg_score,
                    "explanation": f"组合 {d1['drug']} 和 {d2['drug']} 可能具有潜在的协同抗癌效应。"
                }
                combo_recommendations.append(combo)

            return combo_recommendations
        
        if st.button("🔍 生成药物组合推荐"):
            st.session_state.recommendation_result = []
            if not st.session_state.selected_targets:
                st.warning("⚠️ 请先选择至少一个靶点")
            else:
                st.session_state.recommendation_result = drug_recommendation(st.session_state.selected_targets)
                st.success("✅ 药物组合推荐已生成")

        if st.session_state.recommendation_result:
            st.subheader("💊 推荐的药物组合")
            for combo in st.session_state.recommendation_result:
                st.json(combo)



