import csv
from datetime import datetime
from pathlib import Path

import streamlit as st


# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="NeoSphere",
    page_icon="◉",
    layout="wide",
)

PASSWORD = "NEO-2026"

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
LOG_FILE = DATA_DIR / "session_log.csv"
DATA_DIR.mkdir(parents=True, exist_ok=True)


# =====================================================
# STYLE
# =====================================================

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top, #182230 0%, #070A0F 55%, #020305 100%);
        color: #EAEFF7;
    }

    h1, h2, h3 {
        color: #F2F6FF;
        letter-spacing: 0.02em;
    }

    .main-title {
        font-size: 64px;
        font-weight: 700;
        margin-bottom: 0;
        text-align: center;
    }

    .subtitle {
        font-size: 22px;
        color: #AAB7C8;
        text-align: center;
        margin-top: 0;
        margin-bottom: 35px;
    }

    .hero-box {
        padding: 32px;
        border-radius: 24px;
        background: rgba(255, 255, 255, 0.055);
        border: 1px solid rgba(255, 255, 255, 0.10);
        box-shadow: 0 0 40px rgba(80, 140, 255, 0.08);
        margin-bottom: 24px;
    }

    .session-card {
        padding: 26px;
        border-radius: 22px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.10);
        margin-top: 18px;
        margin-bottom: 18px;
    }

    .small-muted {
        color: #9BA7B7;
        font-size: 15px;
    }

    .access-box {
        max-width: 520px;
        margin: 80px auto 0 auto;
        padding: 40px;
        border-radius: 28px;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.10);
        box-shadow: 0 0 60px rgba(80, 140, 255, 0.12);
    }

    div[data-testid="stRadio"] {
        background: rgba(255,255,255,0.045);
        padding: 20px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.08);
    }

    button[kind="primary"], .stButton > button {
        border-radius: 14px;
        padding: 0.65rem 1.2rem;
        border: 1px solid rgba(255,255,255,0.16);
        background: rgba(255,255,255,0.08);
        color: #F2F6FF;
    }

    .stButton > button:hover {
        border-color: rgba(130,170,255,0.7);
        background: rgba(130,170,255,0.16);
    }

    iframe {
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.12);
        background: #000;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# ACCESS
# =====================================================

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.markdown(
        """
        <div class="access-box">
            <div class="main-title" style="font-size:48px;">NeoSphere</div>
            <div class="subtitle">Access to state-control protocols</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    password = st.text_input("Введите код доступа", type="password")

    if st.button("Войти"):
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Неверный код доступа")

    return False


if not check_password():
    st.stop()


# =====================================================
# DATA
# =====================================================

RESET_SESSIONS = [
    {
        "state": "Лёгкий перегруз / внутренний шум",
        "title": "Reset 01 — Мягкое обнуление",
        "description": "Мягкое снижение внутреннего шума и подготовка к дальнейшей работе.",
        "url": "https://drive.google.com/file/d/1XQHVjSdVOcXGq70N2wo733xVip0cbgbu/preview",
    },
    {
        "state": "Сильный перегруз / напряжение",
        "title": "Reset 02 — Глубокое обнуление",
        "description": "Глубокое завораживающее снижение перегрузки.",
        "url": "https://drive.google.com/file/d/1Al1sv5vzf4eEIAcgAQFZYMwTKBZqCiS6/preview",
    },
    {
        "state": "Усталость / нужно восстановиться",
        "title": "Reset 03 — Восстановление",
        "description": "Мягкое восстановление и расслабление.",
        "url": "https://drive.google.com/file/d/1KwVQ836RK_pFPMt7LUkk8OX6yV8TXPlW/preview",
    },
]

ARCHITECT_SESSIONS = [
    {
        "state": "Мысли разбросаны",
        "title": "Architect 01 — Structure",
        "description": "Создание внутренней структуры.",
        "url": "https://drive.google.com/file/d/1AtQbr0wpTAzcPr9RWoKc1puXnINLy_os/preview",
    },
    {
        "state": "Не могу выбрать главное",
        "title": "Architect 02 — Select",
        "description": "Выделение главного.",
        "url": "https://drive.google.com/file/d/1T059GG3UYuhYKDuuooUbJsXU8xi2DGYX/preview",
    },
    {
        "state": "Не могу удержать внимание",
        "title": "Architect 03 — Focus",
        "description": "Удержание внимания.",
        "url": "https://drive.google.com/file/d/1tpV5mc85ekUybhG5xw3EkTcQsquR3Rj5/preview",
    },
    {
        "state": "Мешают эмоции",
        "title": "Architect 04 — Cold Mode",
        "description": "Снижение эмоционального шума.",
        "url": "https://drive.google.com/file/d/1rcwyFIEZyDIJJA9aZLDpftcQy4V_BEWj/preview",
    },
    {
        "state": "Нужно перейти к действию",
        "title": "Architect 05 — Action",
        "description": "Импульс к действию.",
        "url": "https://drive.google.com/file/d/1SPJi1qoio57GkYjT5py2s1VdGEPNTF11/preview",
    },
]

DREAM_SESSIONS = [
    {
        "state": "Не могу отключиться и уснуть",
        "title": "Dream 01 — Продавец снов",
        "description": "Мягкий вход в сон.",
        "url": "https://drive.google.com/file/d/1R-i8knbt_gFn6pGcBb_Bab4gMwcyD1m1/preview",
    },
    {
        "state": "Нужно глубже погрузиться в сон",
        "title": "Dream 02 — Углубление сна",
        "description": "Углубление сонного состояния.",
        "url": "https://drive.google.com/file/d/1jwrNTGwBT-yJKBbAB7igglfwgqYU8UmX/preview",
    },
    {
        "state": "Нужно удержать сонное состояние",
        "title": "Dream 03 — Стабилизация сна",
        "description": "Удержание сонного состояния.",
        "url": "https://drive.google.com/file/d/1MweML-ABNb4Ljy-tcSlzmvR4EDdaF3ih/preview",
    },
]

FULL_PROTOCOL = [
    RESET_SESSIONS[0],
    ARCHITECT_SESSIONS[0],
    ARCHITECT_SESSIONS[1],
    ARCHITECT_SESSIONS[2],
    ARCHITECT_SESSIONS[3],
    ARCHITECT_SESSIONS[4],
    DREAM_SESSIONS[0],
]

REQUESTS = {
    "Полный цикл NeoSphere": FULL_PROTOCOL,
    "Только Reset": RESET_SESSIONS,
    "Только Architect": ARCHITECT_SESSIONS,
    "Только Dream": DREAM_SESSIONS,
    "Лёгкий перегруз / внутренний шум": [RESET_SESSIONS[0]],
    "Сильный перегруз / напряжение": [RESET_SESSIONS[1]],
    "Усталость / нужно восстановиться": [RESET_SESSIONS[2]],
    "Мысли разбросаны": [ARCHITECT_SESSIONS[0]],
    "Не могу выбрать главное": [ARCHITECT_SESSIONS[1]],
    "Не могу удержать внимание": [ARCHITECT_SESSIONS[2]],
    "Мешают эмоции": [ARCHITECT_SESSIONS[3]],
    "Нужно перейти к действию": [ARCHITECT_SESSIONS[4]],
    "Не могу отключиться и уснуть": [DREAM_SESSIONS[0]],
    "Нужно глубже погрузиться в сон": [DREAM_SESSIONS[1]],
    "Нужно удержать сонное состояние": [DREAM_SESSIONS[2]],
}


# =====================================================
# STATE
# =====================================================

if "active_request" not in st.session_state:
    st.session_state.active_request = None

if "step" not in st.session_state:
    st.session_state.step = 0


# =====================================================
# FUNCTIONS
# =====================================================

def save_log(request_name, session_name):
    file_exists = LOG_FILE.exists()

    with LOG_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["datetime", "request", "session"])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            request_name,
            session_name,
        ])


def reset_protocol():
    st.session_state.step = 0
    st.rerun()


# =====================================================
# MAIN INTERFACE
# =====================================================

st.markdown('<div class="main-title">NeoSphere</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Управляй состоянием. Управляй результатом.</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero-box">
        <h3>Система аудиовизуальных протоколов</h3>
        <p class="small-muted">
        NeoSphere помогает перейти из состояния перегруза к структуре, фокусу,
        действию или восстановлению. Вы выбираете текущее состояние — система
        предлагает точный протокол.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1, 1.4])

with left:
    request = st.radio(
        "Что сейчас мешает?",
        list(REQUESTS.keys())
    )

if st.session_state.active_request != request:
    st.session_state.active_request = request
    st.session_state.step = 0

protocol = REQUESTS[request]
step = st.session_state.step

with right:
    if step >= len(protocol):
        st.markdown(
            """
            <div class="session-card">
                <h2>Протокол завершён</h2>
                <p class="small-muted">Вы можете пройти его снова или выбрать другое состояние.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Пройти снова"):
            reset_protocol()

    else:
        item = protocol[step]

        st.markdown(
            f"""
            <div class="session-card">
                <p class="small-muted">Шаг {step + 1} из {len(protocol)}</p>
                <h2>{item["title"]}</h2>
                <p><b>Состояние:</b> {item["state"]}</p>
                <p>{item["description"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### Как использовать")
        st.write("• Используйте наушники")
        st.write("• Не отвлекайтесь")
        st.write("• Не используйте при управлении техникой")
        st.write("• При дискомфорте остановите сессию")

        st.components.v1.iframe(item["url"], height=720)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Следующий шаг"):
                save_log(request, item["title"])
                st.session_state.step += 1
                st.rerun()

        with col2:
            if st.button("Сбросить протокол"):
                reset_protocol()


# =====================================================
# LOG
# =====================================================

with st.expander("Журнал прохождения"):
    if LOG_FILE.exists():
        rows = list(csv.DictReader(LOG_FILE.open("r", encoding="utf-8")))
        st.dataframe(rows, use_container_width=True)
    else:
        st.write("Журнал пока пуст.")
