import streamlit as st
import pandas as pd
import os

# --- 页面基础配置 ---
st.set_page_config(
    page_title="Guardrails Validators 浏览器",
    page_icon="🛡️",
    layout="wide"
)


# --- 数据加载函数 ---
@st.cache_data
def load_data():
    # 这里填写您的文件名，请确保 CSV 文件和本脚本在同一目录下
    file_path = "Organized_Guardrails_Validators.xlsx"

    if not os.path.exists(file_path):
        st.error(f"❌ 未找到文件: {file_path}。请确保 CSV 文件与脚本在同一目录下。")
        return pd.DataFrame()

    try:
        df = pd.read_excel(file_path)
        # 清理关键列的空值，防止报错
        filter_cols = ['Use Cases', 'Risk Category', 'Content Type']
        for col in filter_cols:
            if col in df.columns:
                df[col] = df[col].fillna("").astype(str)
        return df
    except Exception as e:
        st.error(f"读取文件时出错: {e}")
        return pd.DataFrame()


# --- 辅助函数：提取选项 ---
def get_unique_options(df, column_name):
    """从逗号分隔的字符串列中提取所有唯一的选项"""
    unique_items = set()
    if column_name in df.columns:
        for item in df[column_name]:
            if item:
                # 按逗号分割，并去除首尾空格
                tags = [tag.strip() for tag in item.split(',')]
                for tag in tags:
                    if tag:  # 排除空字符串
                        unique_items.add(tag)
    return sorted(list(unique_items))


# --- 主程序逻辑 ---
def main():
    st.title("🛡️ Guardrails Validators 交互式查询")
    st.markdown("通过左侧的过滤器筛选 **应用场景**、**风险类别** 或 **内容类型**。")

    df = load_data()

    if df.empty:
        return

    # --- 侧边栏：过滤器 ---
    st.sidebar.header("🔍 筛选条件")
    st.sidebar.markdown("支持多选，留空则显示全部。")

    # 1. Use Cases (C列) 过滤器
    use_case_options = get_unique_options(df, 'Use Cases')
    selected_use_cases = st.sidebar.multiselect(
        "Use Cases (应用场景)",
        options=use_case_options,
        placeholder="选择应用场景..."
    )

    # 2. Risk Category (D列) 过滤器
    risk_options = get_unique_options(df, 'Risk Category')
    selected_risks = st.sidebar.multiselect(
        "Risk Category (风险类别)",
        options=risk_options,
        placeholder="选择风险类别..."
    )

    # 3. Content Type (E列) 过滤器
    content_options = get_unique_options(df, 'Content Type')
    selected_content = st.sidebar.multiselect(
        "Content Type (内容类型)",
        options=content_options,
        placeholder="选择内容类型..."
    )

    # --- 核心过滤逻辑 ---
    filtered_df = df.copy()

    # 逻辑说明：如果用户选择了标签，则保留包含“任意一个”选中标签的行
    if selected_use_cases:
        filtered_df = filtered_df[filtered_df['Use Cases'].apply(
            lambda x: any(tag in x for tag in selected_use_cases)
        )]

    if selected_risks:
        filtered_df = filtered_df[filtered_df['Risk Category'].apply(
            lambda x: any(tag in x for tag in selected_risks)
        )]

    if selected_content:
        filtered_df = filtered_df[filtered_df['Content Type'].apply(
            lambda x: any(tag in x for tag in selected_content)
        )]

    # --- 结果展示 ---
    st.divider()

    # 顶部统计信息
    col1, col2 = st.columns([1, 6])
    with col1:
        st.metric(label="匹配结果", value=f"{len(filtered_df)} 个")

    # 表格展示
    st.dataframe(
        filtered_df,
        use_container_width=True,  # 铺满宽度
        hide_index=True,  # 隐藏索引列
        column_config={
            "Name": st.column_config.TextColumn("验证器名称", width="medium"),
            "Description": st.column_config.TextColumn("描述", width="large"),
            "Use Cases": st.column_config.TextColumn("应用场景"),
            "Risk Category": st.column_config.TextColumn("风险类别"),
            "Content Type": st.column_config.TextColumn("内容类型"),
            "Infrastructure": st.column_config.TextColumn("基础设施"),
        }
    )

    if len(filtered_df) == 0:
        st.warning("🔍 没有找到符合条件的验证器，请尝试减少筛选条件。")


if __name__ == "__main__":
    main()