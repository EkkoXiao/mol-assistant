import streamlit as st

# 自定义CSS样式
st.markdown("""
<style>
    /* 侧边栏整体样式 */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #f8f9fc 0%, #eef2f6 100%);
        border-radius: 0 20px 20px 0;
        box-shadow: 5px 0 15px rgba(0,0,0,0.05);
        padding: 1.5rem;
    }
    
    .sidebar-title {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
        color: #2c3e50;
        text-align: center;
        padding: 0 0 1.5rem 0;
        margin-bottom: 1rem;
        border-bottom: 1px solid rgba(44, 62, 80, 0.1);
        font-size: 1.4rem;
        letter-spacing: 0.5px;
    }
    
    .stRadio [role=radiogroup] {
        display: flex;
        flex-direction: column;
        gap: 1.2rem;
    }
    
    .stRadio [data-testid=stRadio] > label {
        border: 1px solid #e0e4ec;
        border-radius: 15px;
        padding: 1.2rem;
        background: white;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(50, 50, 93, 0.05), 0 1px 3px rgba(0, 0, 0, 0.05);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .stRadio [data-testid=stRadio] > label:hover {
        transform: translateY(-3px);
        box-shadow: 0 7px 14px rgba(50, 50, 93, 0.1), 0 3px 6px rgba(0, 0, 0, 0.08);
        border-color: #a4b0be;
    }
    
    .stRadio [data-testid=stRadio] > label:has(input:checked) {
        background: linear-gradient(135deg, #f0f5ff 0%, #e6f0ff 100%);
        border: 1px solid #4d7cfe;
        box-shadow: 0 4px 10px rgba(77, 124, 254, 0.15);
    }
    
    .stRadio [data-testid=stRadio] > label:has(input:checked)::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        width: 4px;
        background: linear-gradient(to bottom, #4d7cfe, #6a8eff);
        border-radius: 15px 0 0 15px;
    }
    
    /* 图标样式 */
    .option-icon {
        font-size: 1.8rem;
        margin-bottom: 0.8rem;
        color: #4d7cfe;
    }
    
    .stRadio [data-testid=stRadio] > label:has(input:checked) .option-icon {
        color: #2a5db0;
    }
    
    /* 标题样式 */
    .option-title {
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        color: #2c3e50;
    }
    
    .stRadio [data-testid=stRadio] > label:has(input:checked) .option-title {
        color: #2a5db0;
    }
    
    /* 描述样式 */
    .option-caption {
        font-size: 0.9rem;
        line-height: 1.5;
        color: #5a6c80;
        padding-left: 0.5rem;
        border-left: 2px solid #e0e4ec;
        margin-top: 0.5rem;
    }
    
    /* 全局字体 */
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# 在侧边栏中
with st.sidebar:
    st.markdown('<div class="sidebar-title">请选择需要的功能</div>', unsafe_allow_html=True)
    
    # 使用空容器创建自定义布局
    col1, col2 = st.columns([0.1, 0.9])
    
    with col1:
        # 创建单选按钮（隐藏标签）
        function = st.radio(
            "功能选择",
            ["", ""],
            index=None,
            label_visibility="collapsed"
        )
    
    with col2:
        # 显示自定义内容
        st.markdown("""
        <div>
            <div class="option-icon">💊</div>
            <div class="option-title">联合用药反应评估助手</div>
            <div class="option-caption">输入药物组合信息，评估其联用时潜在的协同药效与不良反应等。适用于临床前验证等场景。</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="margin-top: 1.2rem">
            <div class="option-icon">🧬</div>
            <div class="option-title">抗癌药物组合推荐助手</div>
            <div class="option-caption">基于大数据与模型推理，为特定癌症类型推荐潜力组合。适用于治疗方案的设计等。</div>
        </div>
        """, unsafe_allow_html=True)

# 获取选中的功能值
if function:
    st.write(f"当前选中的功能: {function}")