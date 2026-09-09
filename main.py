import os
import streamlit as st
from datetime import date

import chains
import utils

if 'history' not in st.session_state:
    st.session_state['history'] = []

st.set_page_config(page_title="問診機器人", page_icon=":hospital:", layout="wide")

SUPPORTED_DEPARTMENTS = [
    "中醫科", "外科", "牙科", "骨科", "眼科",
    "耳鼻喉科", "皮膚科", "神經內科", "婦產科", "精神科",
    "內科", "復健科", "整型外科", "放射線科", "高年科",
]


@st.dialog("當前支援詢問的科別")
def show_supported_departments():
    st.markdown("\n".join(f"- {department}" for department in SUPPORTED_DEPARTMENTS))


st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
        background: transparent;
        border: 0;
        color: #ffffff;
        cursor: pointer;
        font-size: 0.875rem;
        font-style: italic;
        font-weight: 400;
        padding: 0;
        text-align: left;
    }

    section[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
        color: #b8b8b8;
        text-decoration: underline;
    }

    section[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:focus {
        box-shadow: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("✏️使用者基本資料填寫")
    name = st.text_input("姓名", value=st.session_state.get('name', ''), max_chars=20)
    id_number = st.text_input("身份證字號/護照號碼", value=st.session_state.get('id_number', ''), max_chars=20)
    gender = st.radio("性別", options = ["男", "女", "其他"], index = ["男", "女", "其他"].index(st.session_state.get("gender", "其他")))
    birth_date = st.date_input("出生年月日", value=st.session_state.get('birth_date', date(1911, 10, 10)),
                               min_value=date(1900, 1, 1), max_value=date.today())
    blood_type = st.selectbox("血型", options=["", "A", "B", "AB", "O"], 
                              index=["", "A", "B", "AB", "O"].index(st.session_state.get('blood_type', '')))

    st.markdown("---")

    st.caption("**本網站僅供測試使用，輸入的資料不會被保存。**")
    st.caption(f"本網站回答的參考資料來源於下列網站:\n\
               衛生福利部台灣e院,\n網址為\nhttps://sp1.hso.mohw.gov.tw/doctor/ ")
    if st.button(
        "點擊此處可查看當前網站最新可支援的詢問科別，將持續進行擴充",
        key="show_supported_departments",
    ):
        show_supported_departments()

# Main content
st.title("台灣e院問診機器人🏥")
st.markdown("🔔**提醒**: 本網站目前僅處在問診輔助的測試階段，請勿將網站回答作為診療依據，\
            如若身體不適請就近咨詢醫師取得專業照護建議。")
utils.write_history()

# Question input
if question := st.chat_input("請輸入您的問題，或是您想詢問的症狀、疾病、藥物等"):
    utils.set_chat_history("user", question)

    if not all([name, id_number, gender, birth_date, blood_type]):
        utils.set_chat_history("ai", "請先在左側填寫完整的使用者基本資料，才能對症下藥，提高回答準確性。")

    else:
        try:
            suggestion = chains.get_suggestion_chain(question = question)
            utils.set_chat_history("ai", suggestion.get("result"),
                                   [
                                        {
                                            "_id":doc.metadata.get("_id"),
                                             "department": doc.metadata.get("department"),
                                             "symptom": doc.metadata.get("symptom"),
                                             "answer": doc.metadata.get("answer"),
                                             "gender": doc.metadata.get("gender"),
                                             "question": doc.page_content,
                                        }
                                        for doc in suggestion.get("source_documents", [])
                                   ]
                               )

        except Exception as e:
            print(f"Error Occurred when generating response: {e}")
            utils.set_chat_history("ai", "抱歉，系統發生錯誤，請稍後再試或聯絡管理員。")

# Store conclusion
if st.session_state['history'] and not st.session_state['history'][-1]['content'] == "請先在左側填寫完整的使用者基本資料，才能對症下藥，提高回答準確性。":
    with st.expander("📚問診結果"):
        st.subheader("👦使用者基本資料")
        st.write(f"**姓名**: {name or '未填寫'}")
        st.write(f"**身份證字號/護照號碼**: {id_number or '未填寫'}")
        st.write(f"**性別**: {gender}")
        st.write(f"**出生年月日**: {birth_date.strftime('%Y-%m-%d')}")
        st.write(f"**血型**: {blood_type}")

        st.subheader("🩺詢問內容")
        for msg in st.session_state['history'][-2:]:
            speaker = "使用者" if msg["role"] == "user" else "問診機器人"
            st.markdown(f"**{speaker}**: {msg['content']}")

        if st.session_state['history'][-1].get("references"):
            st.subheader("📖參考資料")
            for ref in st.session_state['history'][-1]["references"]:
                st.markdown(f"- **資料ID**: {ref['_id']}")
                st.write(f"- **患者性別**: {ref['gender']}")
                st.write(f"- **患者主訴**:")
                st.write(f"- {ref['question']}")
                st.write(f"- **科別**: {ref['department']}")
                st.write(f"- **症狀概括**: {ref['symptom']}")
                st.write(f"- **醫師建議**:")
                st.write(f"- {ref['answer'].replace('回覆','')}")
                
                st.markdown("---")