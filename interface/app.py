import csv
from datetime import datetime
from pathlib import Path

import streamlit as st


# =====================================================
# ДОСТУП
# =====================================================

PASSWORD = "NEO-2026"


def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.set_page_config(
        page_title="NeoSphere",
        layout="wide"
    )

    st.title("NeoSphere Access")
    st.subheader("Система управления состоянием")

    password = st.text_input(
        "Введите код доступа",
        type="password"
    )

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
# PATHS
# =====================================================

ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data"
LOG_FILE = DATA_DIR / "session_log.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)


# =====================================================
# UI
# =====================================================

st.title("NeoSphere")
st.subheader("Управляй состоянием. Управляй результатом.")

st.markdown("""
NeoSphere — система аудиовизуальных протоколов
для управления внутренним состоянием.

Система помогает:

- снижать внутренний шум
- структурировать мышление
- усиливать концентрацию
- переходить в режим восстановления и сна
""")


# =====================================================
# RESET
# =====================================================

RESET_SESSIONS = [
    {
        "state": "Лёгкий перегруз / внутренний шум",
        "title": "Reset 01 — Мягкое обнуление",
        "description": "Мягкое снижение внутреннего шума.",
        "url": "https://drive.google.com/file/d/1XQHVjSdVOcXGq70N2wo733xVip0cbgbu/preview",
    },
    {
        "state": "Сильный перегруз / напряжение",
        "title": "Reset 02 — Глубокое обнуление",
        "description": "Глубокое снижение перегрузки.",
        "url": "https://drive.google.com/file/d/1Al1sv5vzf4eEIAcgAQFZYMwTKBZqCiS6/preview",
    },
    {
        "state": "Усталость / нужно восстановиться",
        "title": "Reset 03 — Восстановление",
        "description": "Мягкое восстановление и расслабление.",
        "url": "https://drive.google.com/file/d/1KwVQ836RK_pFPMt7LUkk8OX6yV8TXPlW/preview",
    },
]


# =====================================================
# ARCHITECT
# =====================================================

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


# =====================================================
# DREAM
# =====================================================

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


# =====================================================
# ПРОТОКОЛЫ
# =====================================================

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
            writer.writerow([
                "datetime",
                "request",
                "session"
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            request_name,
            session_name
        ])


def reset_protocol():
    st.session_state.step = 0
    st.rerun()


# =====================================================
# INTERFACE
# =====================================================

st.divider()

request = st.radio(
    "Что сейчас мешает?",
    list(REQUESTS.keys())
)

if st.session_state.active_request != request:
    st.session_state.active_request = request
    st.session_state.step = 0

protocol = REQUESTS[request]
step = st.session_state.step

st.divider()

if step >= len(protocol):

    st.success("Протокол завершён.")

    if st.button("Пройти снова"):
        reset_protocol()

else:

    item = protocol[step]

    st.markdown(f"## Шаг {step + 1} из {len(protocol)}")

    st.markdown("### Ваше состояние")
    st.write(item["state"])

    st.markdown("### Рекомендуемая сессия")
    st.write(f"**{item['title']}**")

    st.write(item["description"])

    st.markdown("### Как использовать")

    st.write("• Используйте наушники")
    st.write("• Не отвлекайтесь")
    st.write("• Не используйте при управлении техникой")
    st.write("• При дискомфорте остановите сессию")

    st.divider()

    st.components.v1.iframe(
        item["url"],
        height=720
    )

    st.divider()

    if st.button("Следующий шаг"):

        save_log(
            request,
            item["title"]
        )

        st.session_state.step += 1
        st.rerun()

    if st.button("Сбросить протокол"):
        reset_protocol()


# =====================================================
# LOG
# =====================================================

st.divider()

with st.expander("Журнал прохождения"):

    if LOG_FILE.exists():

        rows = list(
            csv.DictReader(
                LOG_FILE.open(
                    "r",
                    encoding="utf-8"
                )
            )
        )

        st.dataframe(
            rows,
            use_container_width=True
        )

    else:
        st.write("Журнал пока пуст.")
