import os
os.system("streamlit")
os.system("langchain")
os.system("langchain_community")
os.system("pypdf")
os.system("openai")

import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate


# 设置页面标题和布局
st.set_page_config(page_title="PDF 解析器", layout="wide")


# 初始化 LLM
@st.cache_resource
def get_llm():
    return ChatOpenAI(
        temperature=0.95,
        model="glm-4-flash",
        openai_api_key="837222c0da712c86188671d1e332b73d.jkkJUgqXG3eKnxlX",
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
    )


st.title("PDF 解析器")

# 创建两列布局
col1, col2 = st.columns(2)

with col1:
    st.header("PDF 上传和内容")
    uploaded_file = st.file_uploader("选择一个 PDF 文件", type="pdf")

    if uploaded_file is not None:
        # 保存上传的文件
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getvalue())

        # 加载 PDF
        loader = PyPDFLoader("temp.pdf")
        pages = loader.load_and_split()

        # 显示 PDF 内容
        st.write("PDF 内容预览：")
        for i, page in enumerate(pages):
            with st.expander(f"第 {i + 1} 页"):
                st.write(page.page_content)

with col2:
    st.header("解析结果")
    if uploaded_file is not None:
        if st.button("解析文档"):
            with st.spinner('正在解析文档...'):
                llm = get_llm()

                # 创建一个提示模板，指定输出中文摘要
                prompt_template = """
                系统: 你是一个专业的文档分析助手。请仔细阅读以下文档，并用中文提供一个全面的摘要。摘要应该包括文档的主要观点、关键信息和结论。

                人类: 这是文档内容：
                {text}
                请提供一个详细的中文摘要。

                助手: 好的，我会仔细阅读文档并提供一个全面的中文摘要：

                """
                PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])

                chain = load_summarize_chain(llm, chain_type="stuff", prompt=PROMPT)
                summary = chain.run(pages)
                st.write(summary)
    else:
        st.write("请在左侧上传一个 PDF 文件。")
