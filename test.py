import streamlit as st
from streamlit_extras.stylable_container import stylable_container

drug_count = 4
# 示例数据
data = {
    "drug1": "Alpelisib",
    "drug2": " CopanlisibCopanlisibCopanlisibdasfafasdfasfdafadsfas",
    "drug3": "adsfasdf",
    "drug4": "asdfasdf",
    "score": 0.305,
    "explanation": "Alpelisib和Copanlisib通过与各自的作用靶点结合，协同对抗癌症，共同抑制癌细胞的生长和分裂。 "
                   "Alpelisib作用于磷脂酰肌醇4,5-二磷酸3-核糖合酶家族成员1（PAI-3），而 Copanlisib则作用于磷脂酰肌醇4,5-二磷酸3-核糖合酶家族成员1。"
                   "它们通过协同作用，共同发挥抗癌作用。"
}

# 根据分数设置颜色
def get_score_color(score):
    if score > 0.6:
        return "#4CAF50"  # 绿色
    elif score > 0.3:
        return "#FFC107"  # 黄色
    else:
        return "#F44336"  # 红色

if drug_count == 2:
    # 使用卡片布局展示主要信息
    with stylable_container(
        key="drug_card",
        css_styles="""
            {
                position: relative;
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 12px;
                padding: 10px;
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
                        width:80%;
                        height:80%;
                        flex-grow:0.5;
                        overflow-y:auto;
                        flex-direction: column;
                        box-shadow: 0 4px 8px rgba(30, 136, 229, 0.2);
                        border-left: 4px solid #1E88E5;
                    '>
                        <h3 style='margin:0; color:#0d47a1;'>{data['drug1']}</h3>
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
                            <span style='font-size: 14px; color:#666;'>相互作用分数</span>
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
                        padding: 15px;
                        border-radius: 10px;
                        text-align: center;
                        width:80%;
                        height:80%;
                        flex-grow:0.5;
                        overflow-y:auto;
                        flex-direction: column;
                        box-shadow: 0 4px 8px rgba(216, 27, 96, 0.2);
                        border-right: 4px solid #D81B60;
                    '>
                        <h3 style='margin:0; color:#880e4f;'>{data['drug2']}</h3>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # 解释部分
        with st.expander("📝 作用机制详解", expanded=True):
            st.markdown(f"""
                <div style='
                    margin: 5px;
                    background-color: #e3f2fd;
                    padding: 10px;
                    border-radius: 8px;
                    line-height: 1.8;
                    font-size: 16px;
                '>
                    {data['explanation']}
                </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

elif drug_count == 3:
    # 使用卡片布局展示主要信息
    with stylable_container(
        key="drug_card",
        css_styles="""
            {
                position: relative;
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 12px;
                padding: 10px;
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
                        width:80%;
                        height:80%;
                        flex-grow:0.5;
                        overflow-y:auto;
                        flex-direction: column;
                        box-shadow: 0 4px 8px rgba(30, 136, 229, 0.2);
                        border-left: 4px solid #1E88E5;
                    '>
                        <h3 style='margin:0; color:#0d47a1;'>{data['drug2']}</h3>
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
                            <span style='font-size: 14px; color:#666;'>相互作用分数</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # 药物2
        with col3:
            st.markdown(f"""
                <div style='
                    height: 120px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                '>
                    <div style='
                        background: linear-gradient(145deg, #f8bbd0, #fce4ec);
                        padding: 15px;
                        border-radius: 10px;
                        text-align: center;
                        width:80%;
                        height:80%;
                        flex-grow:0.5;
                        overflow-y:auto;
                        flex-direction: column;
                        box-shadow: 0 4px 8px rgba(216, 27, 96, 0.2);
                        border-right: 4px solid #D81B60;
                    '>
                        <h3 style='margin:0; color:#880e4f;'>{data['drug3']}</h3>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        col1_1, col1_2, col1_3 = st.columns([0.5, 1, 0.5])
        with col1_2:
            st.markdown(f"""
                <div style='
                    height: 120px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                '>
                    <div style='
                        background: linear-gradient(145deg, #bbdefb, #e3f2fd);
                        padding: 25px;
                        border-radius: 10px;
                        text-align: center;
                        width:80%;
                        height:80%;
                        flex-grow:0.5;
                        overflow-y:auto;
                        flex-direction: column;
                        box-shadow: 0 4px 8px rgba(30, 136, 229, 0.2);
                        border-left: 4px solid #1E88E5;
                    '>
                        <h3 style='margin:0; color:#0d47a1;'>{data['drug1']}</h3>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # 解释部分
        with st.expander("📝 作用机制详解", expanded=True):
            st.markdown(f"""
                <div style='
                    margin: 5px;
                    background-color: #e3f2fd;
                    padding: 10px;
                    border-radius: 8px;
                    line-height: 1.8;
                    font-size: 16px;
                '>
                    {data['explanation']}
                </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

elif drug_count == 4:
    # 使用卡片布局展示主要信息
    with stylable_container(
        key="drug_card",
        css_styles="""
            {
                position: relative;
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 12px;
                padding: 10px;
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
                        height: 120px;
                        flex-grow:0.5;
                        overflow-y:auto;
                        flex-direction: column;
                        box-shadow: 0 4px 8px rgba(30, 136, 229, 0.2);
                        border-left: 4px solid #1E88E5;
                    '>
                        <h3 style='margin:0; color:#0d47a1;'>{data['drug2']}</h3>
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
                            <span style='font-size: 14px; color:#666;'>相互作用分数</span>
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
                        padding: 15px;
                        border-radius: 10px;
                        text-align: center;
                        height: 120px;
                        flex-grow:0.5;
                        overflow-y:auto;
                        flex-direction: column;
                        box-shadow: 0 4px 8px rgba(216, 27, 96, 0.2);
                        border-right: 4px solid #D81B60;
                    '>
                        <h3 style='margin:0; color:#880e4f;'>{data['drug3']}</h3>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        col1_1, col1_2, col1_3, col1_4 = st.columns([0.25, 1, 1, 0.25])
        with col1_2:
            st.markdown(f"""
                <div style='
                    height: 160px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                '>
                    <div style='
                        background: linear-gradient(145deg, #fff9c4, #fffde7);
                        padding: 35px;
                        border-radius: 10px;
                        text-align: center;
                        height:120px;
                        flex-grow:0.5;
                        overflow-y:auto;
                        flex-direction: column;
                        box-shadow: 0 4px 8px rgba(255, 193, 7, 0.2);
                        border-left: 4px solid #FFC107;
                    '>
                        <h3 style='margin:0; color:#ff6f00;'>{data['drug2']}</h3>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with col1_3:
            st.markdown(f"""
                <div style='
                    height: 160px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                '>
                    <div style='
                        background: linear-gradient(145deg, #c8e6c9, #e8f5e9);
                        padding: 35px;
                        border-radius: 10px;
                        text-align: center;
                        height: 120px;
                        flex-grow:0.5;
                        overflow-y:auto;
                        flex-direction: column;
                        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.2);
                        border-left: 4px solid #4CAF50;
                    '>
                        <h3 style='margin:0; color:#1b5e20;'>{data['drug3']}</h3>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # 解释部分
        with st.expander("📝 作用机制详解", expanded=False):
            st.markdown(f"""
                <div style='
                    margin: 5px;
                    background: linear-gradient(135deg, #f5f0ff 0%, #f3edff 100%);
                    padding: 20px;
                    border-radius: 10px;
                    border-left: 4px solid #7e57c2;
                    line-height: 1.8;
                    font-size: 16px;
                    box-shadow: 0 4px 8px rgba(126, 87, 194, 0.1);
                '>
                    <div style='
                        font-size: 20px;
                        color: #5e35b1;
                        margin-bottom: 12px;
                        font-weight: bold;
                        display: flex;
                        align-items: center;
                    '>
                        <span style='font-size: 24px; margin-right: 8px;'>📝</span> 作用机制详解
                    </div>
                    {data['explanation']}
                </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
