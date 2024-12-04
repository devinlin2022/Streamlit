import os
os.system("pip install streamlit")
os.system("pip install PIL")
os.system("pip install pillow_heif")
import streamlit as st
import os
import json
import base64
import requests
from datetime import datetime
from io import BytesIO
from PIL import Image
from pillow_heif import register_heif_opener
register_heif_opener()

st.set_page_config(layout="wide")

st.markdown("""
    <style>
    .css-1v0mbdj.e115fcil1 {
        width: 100%;
    }
    .stButton>button {
        width: 100%;
    }
    .uploadedFile {
        border: 1px solid #ccc;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

class AliBailianImageService:
    def __init__(self, configuration):
        self.configuration = configuration

    def get_api_key(self):
        dev_environment_variable = os.getenv("ENVIRONMENT")
        is_development = not dev_environment_variable or dev_environment_variable.lower() == "development"
        if is_development:
            api_key = self.configuration.get("DASHSCOPE_API_KEY")
        else:
            api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            print("API Key 未设置。请确保环境变量 'DASHSCOPE_API_KEY' 已设置。")
            return None
        return api_key

    def get_image_base64_string_and_save(self, image_data):
        if isinstance(image_data, bytes):
            encoded_image = base64.b64encode(image_data).decode('utf-8')
        else:
            response = requests.get(image_data)
            if response.status_code != 200:
                raise Exception(f"Failed to download image: {response.status_code}")
            encoded_image = base64.b64encode(response.content).decode('utf-8')
        return encoded_image

    def send_post_request(self, url, json_content, api_key):
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        response = requests.post(url, data=json_content, headers=headers)
        response_body = response.text
        self.write_response_to_log(response_body)
        if response.status_code >= 200 and response.status_code < 300:
            return response_body
        else:
            return f"请求失败: {response.status_code}"

    def write_response_to_log(self, response_body):
        log_file_path = "Logs/response.log"
        log_dir = os.path.dirname(log_file_path)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        with open(log_file_path, 'a') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Response Body: {response_body}\n")

    def get_results(self, encoded_image):
        api_key = self.get_api_key()
        if not api_key:
            return None

        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        json_content = {
            "model": "qwen2-vl-7b-instruct",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请对这张图片进行OCR识别，并输出最准确的文字内容，直接输出识别出的中文/英文结果字符，不要输出其他内容。"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_image}"}}
                    ]
                }
            ]
        }
        json_content_str = json.dumps(json_content)
        result = self.send_post_request(url, json_content_str, api_key)
        return result

def main():
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("Image Upload")

        upload_option = st.selectbox(
            "Choose upload method",
            ["Upload File", "Provide URL"]
        )

        image_data = None
        if upload_option == "Upload File":
            uploaded_file = st.file_uploader(
                "Choose an image file",
                type=['png', 'jpg', 'jpeg', 'heic', 'HEIC'],  # Added HEIC format
                help="Drag and drop an image file here",
            )

            if uploaded_file is not None:
                file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
                if file_size > 5:
                    st.error("File size too large! Please upload an image smaller than 5MB")
                    return

                try:
                    # Convert the uploaded file to PIL Image
                    image = Image.open(uploaded_file)

                    # Convert to RGB if necessary
                    if image.mode != 'RGB':
                        image = image.convert('RGB')

                    # Convert PIL Image to bytes for display
                    buf = BytesIO()
                    image.save(buf, format='PNG')
                    image_data = buf.getvalue()

                    # Display the image
                    st.image(image, caption="Uploaded Image", use_column_width=True)

                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")
                    return

        if image_data:
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                status_text.text("Processing image...")
                progress_bar.progress(30)

                config = {
                    "DASHSCOPE_API_KEY": "sk-db6fa6efbf144521b0180da5e83b0a94"
                }
                service = AliBailianImageService(config)

                encoded_image = service.get_image_base64_string_and_save(image_data)
                progress_bar.progress(60)

                with st.spinner('Processing image...'):
                    result = service.get_results(encoded_image)
                    json_str = result.replace('Result: ', '')
                    data = json.loads(json_str)
                    message = data['choices'][0]['message']['content']

                progress_bar.progress(100)
                status_text.text("Processing complete!")

                st.session_state.result = message

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                progress_bar.empty()
                status_text.empty()

    with col2:
        st.header("Recognition Result")

        result_container = st.container()

        with result_container:
            if 'result' in st.session_state:
                text_area = st.text_area(
                    "Recognized Text",
                    value=st.session_state.result,
                    height=100,
                    key="result_area"
                )

                if st.button("Copy to Clipboard"):
                    st.markdown(f"""
                        <textarea id="text-to-copy" style="position: absolute; left: -9999px;">{st.session_state.result}</textarea>
                        <script>
                            var textArea = document.getElementById('text-to-copy');
                            textArea.select();
                            document.execCommand('copy');
                            document.body.removeChild(textArea);
                        </script>
                        """, unsafe_allow_html=True)
                    st.success("Text copied to clipboard!")
            else:
                st.info("Upload an image to see the recognition result")

if __name__ == "__main__":
    main()
