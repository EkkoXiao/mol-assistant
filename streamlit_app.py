import itertools
import json
import pandas as pd
import requests
import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from utils import API_URL, load_html, get_score_color, get_network_data, display_network_graph

# 设置页面标题和样式
st.set_page_config(page_title="联合用药助手", page_icon="💊", layout="wide")


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
if "selected_cell_line" not in st.session_state:
    st.session_state.selected_cell_line = None
if "cancer_cell_lines" not in st.session_state:
    st.session_state.cancer_cell_lines = []
if "recommendation_result" not in st.session_state:
    st.session_state.recommendation_result = []
if "selected_comb_cnt" not in st.session_state:
    st.session_state.selected_comb_cnt = 2
if "recommendation_generated" not in st.session_state:
    st.session_state.recommendation_generated = False
if "current_view" not in st.session_state:
    st.session_state.current_view = "recommendation"  # "recommendation" or "network"
if "network_data" not in st.session_state:
    st.session_state.network_data = None

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
                # if drug_name and drug_property and drug_target and drug_smiles:
                if drug_name and drug_property:
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
                            print(drug_data)
                            print(drug)
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
            )
        )

        confirm_button = st.button(
            "确定",
            use_container_width=True, 
        )

        if confirm_button:
            st.session_state.cancer_cell_lines = []
            st.session_state.selected_cell_line = None
            st.session_state.recommendation_result = []
            if cancer_type is None:
                st.warning("⚠️ 请选择一种癌症类型后再点击确定")
            else:
                st.session_state.cancer_type = cancer_type
                st.success(f"✅ 已选择癌症类型：{cancer_type}")
                cancer_type_en = cancer_type.replace("乳腺癌", "breast_cancer").replace("胃癌", "stomach_cancer").replace("肠癌", "colon_cancer").replace("肝癌", "liver_cancer")   
                # 调用后端，获取癌症对应的细胞系信息
                try:
                    resp = requests.get(f"{API_URL}/cancer_cell_line", params={"cancer_type": cancer_type_en})
                    resp.raise_for_status()
                    st.session_state.cancer_cell_lines = resp.json()["cell_lines"]
                except Exception as e:
                    st.error("细胞系获取失败，请稍后再试！")

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
                    
                    # prompt_cancer += "以下为他们之间相互作用不良反应及协同药效的可能的预测信息及发生可能性，该结果并非权威数据，仅供可能的参考所用。\n"
                    # for key in drug_interaction_keys:
                    #     interactions = next((pair[key] for pair in st.session_state.interactions if key in pair), None)
                    #     drug1 = st.session_state.drugs[key // 10]['name']
                    #     drug2 = st.session_state.drugs[key % 10]['name']

                    #     interaction_text = "\n".join(
                    #         [f"- \"{desc}\"  ({prob * 100:.2f}%)" for desc, (prob, _) in interactions.items()]
                    #     )
                    #     prompt_cancer += f"药物{drug1}与{drug2}联合用药可能有如下情况出现：{interaction_text}\n"

                    # prompt_cancer += f"关于{cancer_type}治疗中上述几种药物联合用药与单药相比在有效性和安全性方面的差异，请基于全球权威指南（如NCCN、ESMO）、高循证等级的临床试验数据（如III期随机对照试验，RCT）以及相关研究数据库，提供详细的分析与说明，可能用做参考的量化评估数据例如：总生存期（OS），无进展生存期（PFS），客观缓解率（ORR），3 级及以上不良事件发生率，治疗相关死亡率等。我们已知这几个药物组合总是有效的，解释一下作用机理或者原因，不需要详细讲述它们之间的不良反应，并最后总能得出能够推荐这几个药物的结论。"
                    prompt_cancer += f"关于{cancer_type}治疗中上述几种药物联合用药与单药相比在有效性和安全性方面的差异，我们已知他们联合使用是有效的，根据上述内容选择有用的线索，解释一下作用机理或者原因，不需要详细讲述它们之间的不良反应，并最后总能得出能够推荐这几个药物的结论。"
                    
                    try:
                        decoder = json.JSONDecoder()
                        think = False
                        answer = "⏳ 结果生成中，请稍加等待..."
                        response_placeholder.markdown(answer)

                        response = requests.post(
                            f"{API_URL}/stream",
                            json={"messages": [{"role": "user", "content": prompt_cancer}]},
                            stream=True
                        )
                        answer = ""

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
                    answer = "结果生成中，请稍加等待......"
                    response_placeholder = st.empty()
                    response_placeholder.markdown(answer)

                    response = requests.post(
                        f"{API_URL}/stream",
                        json={"messages": messages},
                        stream=True
                    )
                    answer = ""
                    
                    decoder = json.JSONDecoder()
                    think = False

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

    st.markdown("""
    <style>
        /* 标题样式 */
        .custom-title {
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e0e4ec;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.8rem;
        }
        
        /* 癌症信息卡片 */
        .cancer-card {
            border-radius: 12px;
            padding: 1.2rem 1.5rem;
            margin-bottom: 1.5rem;
            background: linear-gradient(135deg, #f0f5ff 0%, #e6f0ff 100%);
            border: 1px solid #4d7cfe;
            box-shadow: 0 4px 10px rgba(77, 124, 254, 0.15);
            position: relative;
            overflow: hidden;
        }
        
        .cancer-card::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            height: 100%;
            width: 5px;
            background: linear-gradient(to bottom, #4d7cfe, #6a8eff);
        }
        
        /* 警告卡片 */
        .warning-card {
            border-radius: 12px;
            padding: 1.2rem 1.5rem;
            margin-bottom: 1.5rem;
            background: linear-gradient(135deg, #fff8e1 0%, #fff3e0 100%);
            border: 1px solid #ffb300;
            box-shadow: 0 4px 10px rgba(255, 179, 0, 0.15);
            position: relative;
            overflow: hidden;
        }
        
        .warning-card::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            height: 100%;
            width: 5px;
            background: linear-gradient(to bottom, #ffb300, #ffca28);
        }
        
        /* 卡片内容样式 */
        .card-content {
            padding-left: 1.5rem;
        }
        
        .card-title {
            font-weight: 600;
            font-size: 1.2rem;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .card-icon {
            font-size: 1.5rem;
        }
        
        /* 动画效果 */
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(77, 124, 254, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(77, 124, 254, 0); }
            100% { box-shadow: 0 0 0 0 rgba(77, 124, 254, 0); }
        }
        
        .pulse-animation {
            animation: pulse 2s infinite;
        }
    </style>
    """, unsafe_allow_html=True)

    # 标题部分
    st.markdown(
        f'<div class="custom-title">'
        f'  <span>🧬</span>'
        f'  <span>抗癌药物组合推荐助手</span>'
        f'</div>', 
        unsafe_allow_html=True
    )

    # 癌症信息卡片
    if st.session_state.cancer_type != None:
        st.markdown(
            f'<div class="cancer-card pulse-animation">'
            f'  <div class="card-content">'
            f'      <div class="card-title">'
            f'          <span class="card-icon">♋</span>'
            f'          <span>当前已选择癌症类型: {st.session_state.cancer_type}</span>'
            f'      </div>'
            f'  </div>'
            f'</div>', 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="warning-card">'
            f'  <div class="card-content">'
            f'      <div class="card-title">'
            f'          <span class="card-icon">⚠️</span>'
            f'          <span>请从左侧菜单中选择癌症类型以继续</span>'
            f'      </div>'
            f'  </div>'
            f'</div>', 
            unsafe_allow_html=True
        )

    if st.session_state.cancer_cell_lines:
        selected = st.selectbox(
            "🎯 请选择细胞系",
            index=None,
            options=st.session_state.cancer_cell_lines,
            key="selected_cell_line_current",
            on_change=lambda: setattr(st.session_state, 'selected_cell_line', st.session_state.selected_cell_line_current)
        )

        num_drugs = st.slider("💊 请选择药物组合中的药物数量", min_value=2, max_value=4, value=2)

        max_approved = num_drugs 
        approved_drugs = st.slider("✅ 请选择药物组合中已上市的药物数量", min_value=0, max_value=max_approved, value=0)

        topk = st.number_input("📊 请输入需要推荐的组合数量", min_value=1, max_value=100, value=1, step=1)

        # 根据细胞系和药物组合参数进行推荐
        if st.button("🔍 生成药物组合推荐"):
            st.session_state.selected_comb_cnt = num_drugs
            st.session_state.recommendation_result = []
            if not st.session_state.selected_cell_line:
                st.warning("⚠️ 请先选择一个细胞系")
                st.session_state.recommendation_generated = False
            else:
                # 加载动画
                loading_placeholder = st.empty()
                
                with loading_placeholder.container():
                    st.markdown("""
                    <div style="text-align: center; padding: 20px;">
                        <div style="display: inline-block; width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                        <p style="margin-top: 15px; color: #666; font-size: 16px;">🤖 正在分析药物组合...</p>
                    </div>
                    <style>
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                    </style>
                    """, unsafe_allow_html=True)
                
                try:
                    resp = requests.post(
                        f"{API_URL}/recommend_combo",
                        json={
                            "cell_line": st.session_state.selected_cell_line,
                            "count": num_drugs,
                            "label": approved_drugs,
                            "topk": topk
                        },
                        timeout=120
                    )
                    resp.raise_for_status()
                    st.session_state.recommendation_result = resp.json()["combos"]
                
                    loading_placeholder.empty()
                    
                    if len(st.session_state.recommendation_result) > 0:
                        st.session_state.recommendation_generated = True
                    else:
                        st.warning("⚠️ 未找到合适的药物组合，请调整参数")
                        st.session_state.recommendation_generated = False
                except Exception as e:
                    loading_placeholder.empty()
                    st.error("推荐生成超时，请稍后再试！")

        if st.session_state.get("recommendation_result"):
            st.markdown("""
            <div style="display: flex; align-items: center; width: 100%; margin: 20px 0;">
            """, unsafe_allow_html=True)
            
            view_option = st.radio(
                "选择视图模式",
                ["💊 推荐列表", "🔗 网络图"],
                index=0,
                horizontal=True,
                label_visibility="collapsed",
                key="view_selector"
            )
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 根据选择更新视图状态
            if view_option == "💊 推荐列表":
                st.session_state.current_view = "recommendation"
            else:
                st.session_state.current_view = "network"
                st.session_state.network_data = None
                st.session_state.selected_combo_index = 0
            
            if st.session_state.current_view == "recommendation":
                for idx, data in enumerate(st.session_state.recommendation_result):
                    with stylable_container(
                        key=f"drug_card_{idx}",
                        css_styles="""
                            {
                                position: relative;
                                border: 1px solid rgba(49, 51, 63, 0.2);
                                border-radius: 12px;
                                padding: 5px;
                                box-shadow: 0 6px 16px rgba(0,0,0,0.1);
                                background-color: white;
                                margin-bottom: 5px;
                                overflow: hidden;
                            }
                            .drug-content {
                                position: relative;
                                z-index: 1;
                            }
                        """,
                    ):
                        st.markdown('<div class="drug-content">', unsafe_allow_html=True)

                        col1, col2, col3 = st.columns([1, 0.5, 1])

                        # 药物1
                        with col1:
                            st.markdown(f"""
                            <div style='
                                height: 160px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                            '>
                                <div style='
                                    background: linear-gradient(145deg, #bbdefb, #e3f2fd);
                                    padding: 25px;
                                    border-radius: 10px;
                                    text-align: center;
                                    height: 70%;
                                    width: 80%;
                                    flex-grow:0.5;
                                    overflow-y:auto;
                                    flex-direction: column;                                    
                                    box-shadow: 0 4px 8px rgba(30, 136, 229, 0.2);
                                    border-left: 4px solid #1E88E5;
                                '>
                                    <h3 style='margin:0; color:#0d47a1;'>{data['combo'][0]}</h3>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                        # 分数展示
                        with col2:
                            score_color = get_score_color(data['score'])
                            st.markdown(f"""
                                <div style='
                                    min-height: 160px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                '>
                                    <div style='
                                        width: 140px;
                                        height: 140px;
                                        border-radius: 50%;
                                        background: conic-gradient({score_color} 0% {data['score']*100}%, #e0e0e0 {data['score']*100}% 100%);
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
                                        border: 6px solid white;
                                    '>
                                        <div style='
                                            width: 120px;
                                            height: 120px;
                                            border-radius: 50%;
                                            background: white;
                                            display: flex;
                                            align-items: center;
                                            justify-content: center;
                                            flex-direction: column;
                                        '>
                                            <span style='font-size: 32px; font-weight: bold; color:{score_color};'>{data['score']:.3f}</span>
                                            <span style='font-size: 14px; color:#666;'>联合抗癌分数</span>
                                        </div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)

                        # 药物2
                        with col3:
                            st.markdown(f"""
                                <div style='
                                    height: 160px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                '>
                                    <div style='
                                        background: linear-gradient(145deg, #f8bbd0, #fce4ec);
                                        padding: 25px;
                                        border-radius: 10px;
                                        text-align: center;
                                        height: 70%;
                                        width: 80%;
                                        flex-grow:0.5;
                                        overflow-y:auto;
                                        flex-direction: column;
                                        box-shadow: 0 4px 8px rgba(216, 27, 96, 0.2);
                                        border-right: 4px solid #D81B60;
                                    '>
                                        <h3 style='margin:0; color:#880e4f;'>{data['combo'][1]}</h3>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)

                        if st.session_state.selected_comb_cnt == 3:
                            _, col_mid, _ = st.columns([0.75, 1, 0.75])
                            with col_mid:
                                st.markdown(f"""
                                <div style='
                                    height: 160px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                '>
                                    <div style='
                                        background: linear-gradient(145deg, #fff9c4, #fffde7);
                                        padding: 25px;
                                        border-radius: 10px;
                                        text-align: center;
                                        height: 70%;
                                        width: 80%;
                                        flex-grow:0.5;
                                        overflow-y:auto;
                                        flex-direction: column;
                                        box-shadow: 0 4px 8px rgba(255, 193, 7, 0.2);
                                        border-left: 4px solid #FFC107;
                                    '>
                                        <h3 style='margin:0; color:#ff6f00;'>{data['combo'][2]}</h3>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                                
                        elif st.session_state.selected_comb_cnt == 4:
                            _, col_left, col_right, _ = st.columns([0.1, 1, 1, 0.1])
                            with col_left:
                                st.markdown(f"""
                                    <div style='
                                        height: 160px;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                    '>
                                        <div style='
                                            background: linear-gradient(145deg, #fff9c4, #fffde7);
                                            padding: 25px;
                                            border-radius: 10px;
                                            text-align: center;
                                            height: 70%;
                                            width: 80%;
                                            flex-grow:0.5;
                                            overflow-y:auto;
                                            flex-direction: column;
                                            box-shadow: 0 4px 8px rgba(255, 193, 7, 0.2);
                                            border-left: 4px solid #FFC107;
                                        '>
                                            <h3 style='margin:0; color:#ff6f00;'>{data['combo'][2]}</h3>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                            with col_right:
                                st.markdown(f"""
                                    <div style='
                                        height: 160px;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                    '>
                                        <div style='
                                            background: linear-gradient(145deg, #c8e6c9, #e8f5e9);
                                            padding: 25px;
                                            border-radius: 10px;
                                            text-align: center;
                                            height: 70%;
                                            width: 80%;
                                            flex-grow:0.5;
                                            overflow-y:auto;
                                            flex-direction: column;
                                            box-shadow: 0 4px 8px rgba(76, 175, 80, 0.2);
                                            border-right: 4px solid #4CAF50;
                                        '>
                                            <h3 style='margin:0; color:#1b5e20;'>{data['combo'][3]}</h3>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)

            elif st.session_state.current_view == "network":
                if 'selected_combo_index' not in st.session_state:
                    st.session_state.selected_combo_index = 0
                
                combo_options = []
                for idx, result in enumerate(st.session_state.recommendation_result):
                    combo_name = f"组合 {idx + 1}: {result['combo']}"
                    combo_options.append(combo_name)
                
                st.markdown("""
                <div style="display: flex; justify-content: center; align-items: center; width: 100%; margin: 20px 0;">
                """, unsafe_allow_html=True)
                
                selected_combo_name = st.selectbox(
                    "选择药物组合",
                    combo_options,
                    index=st.session_state.selected_combo_index,
                    key="combo_selector",
                    label_visibility="collapsed"
                )
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                selected_index = combo_options.index(selected_combo_name)
                selected_combo = st.session_state.recommendation_result[selected_index]['combo']
                
                # 检查是否需要重新生成网络图
                if st.session_state.network_data is None or st.session_state.selected_combo_index != selected_index:
                    st.session_state.selected_combo_index = selected_index
                    
                    with st.spinner(f"🔄 正在生成组合 {selected_index + 1} 的网络图..."):
                        network_data = get_network_data(st.session_state.selected_cell_line, selected_combo)
                        if network_data:
                            st.session_state.network_data = network_data
                        else:
                            st.error("无法获取网络图数据")
                            st.stop()
                
                display_network_graph(st.session_state.network_data)

