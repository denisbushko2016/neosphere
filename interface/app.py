import csv
from datetime import datetime
from pathlib import Path

import streamlit as st


# =========================
# ДОСТУП ПО ПАРОЛЮ
# =========================

PASSWORD = "NEO-2026"


def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.set_page_config(page_title="NeoSphere Access", layout="centered")

    st.title("NeoSphere Access")
    st.subheader("Система управления состоянием")

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


# =========================
# ОСНОВНЫЕ НАСТРОЙКИ
# =========================

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
LOG_FILE = DATA_DIR / "session_log.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)


st.title("NeoSphere")
st.subheader("Управляй состоянием. Управляй результатом.")

st.markdown("""
NeoSphere — система управления состоянием через аудиовизуальные протоколы.

Выберите текущее состояние. Система подберёт протокол и адаптирует следующий шаг по вашей реакции.
""")


# =========================
# RESET
# =========================

RESET_SESSIONS = [
    {
        "state": "Лёгкий перегруз / внутренний шум",
        "title": "Reset 01 — Мягкое обнуление",
        "description": "Мягкое снижение внутреннего шума и подготовка к дальнейшей работе.",
        "url": "https://drive.google.com/uc?export=download&id=1XQHVjSdVOcXGq70N2wo733xVip0cbgbu",
    },
    {
        "state": "Сильный перегруз / напряжение",
        "title": "Reset 02 — Глубокое обнуление",
        "description": "Глубокое завораживающее снижение перегрузки.",
        "url": "https://drive.google.com/uc?export=download&id=1Al1sv5vzf4eEIAcgAQFZYMwTKBZqCiS6",
    },
    {
        "state": "Усталость / нужно восстановиться",
        "title": "Reset 03 — Восстановительное обнуление",
        "description": "Мягкое расслабленное восстановление и снижение активности.",
        "url": "https://drive.google.com/uc?export=download&id=1KwVQ836RK_pFPMt7LUkk8OX6yV8TXPlW",
    },
]


# =========================
# ARCHITECT
# =========================

ARCHITECT_SESSIONS = [
    {
        "state": "Мысли разбросаны",
        "title": "Architect 01 — Structure",
        "description": "Разложить мысли и создать поле структуры.",
        "url": "https://drive.google.com/uc?export=download&id=1AtQbr0wpTAzcPr9RWoKc1puXnINLy_os",
    },
    {
        "state": "Не могу выбрать главное",
        "title": "Architect 02 — Select",
        "description": "Выделить главное и убрать лишнее.",
        "url": "https://drive.google.com/uc?export=download&id=1T059GG3UYuhYKDuuooUbJsXU8xi2DGYX",
    },
    {
        "state": "Не могу удержать внимание",
        "title": "Architect 03 — Focus",
        "description": "Удержать внимание на выбранном объекте.",
        "url": "https://drive.google.com/uc?export=download&id=1tpV5mc85ekUybhG5xw3EkTcQsquR3Rj5",
    },
    {
        "state": "Мешают эмоции",
        "title": "Architect 04 — Cold Mode",
        "description": "Холодная ясность и снижение эмоционального шума.",
        "url": "https://drive.google.com/uc?export=download&id=1D_Uyo5COFwiNruXH1B5Ir3XN0vwsc3BA",
    },
    {
        "state": "Нужно перейти к действию",
        "title": "Architect 05 — Action",
        "description": "Переход к действию и включение импульса.",
        "url": "https://drive.google.com/uc?export=download&id=1NJ_f9dorzVgEhKkEAqhD_qyngJFPcbY-",
    },
]


# =========================
# DREAM
# =========================

DREAM_SESSIONS = [
    {
        "state": "Не могу отключиться и уснуть",
        "title": "Dream 01 — Продавец снов",
        "description": "Мягкий вход в сон и появление образного поля.",
        "url": "https://drive.google.com/uc?export=download&id=1R-i8knbt_gFn6pGcBb_Bab4gMwcyD1m1",
    },
    {
        "state": "Нужно глубже погрузиться в сон",
        "title": "Dream 02 — Углубление сна",
        "description": "Углубление сонного состояния.",
        "url": "https://drive.google.com/uc?export=download&id=1jwrNTGwBT-yJKBbAB7igglfwgqYU8UmX",
    },
    {
        "state": "Нужно удержать сонное состояние",
        "title": "Dream 03 — Стабилизация сна",
        "description": "Удержание сна, снижение активности и затемнение восприятия.",
        "url": "https://drive.google.com/uc?export=download&id=1MweML-ABNb4Ljy-tcSlzmvR4EDdaF3ih",
    },
]


# =========================
# ПРОТОКОЛЫ
# =========================

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

    "Лёгкий перегруз / внутренний шум": [RESET_SESSIONS[0]] + ARCHITECT_SESSIONS,
    "Сильный перегруз / напряжение": [RESET_SESSIONS[1]],
    "Усталость / нужно восстановиться": [RESET_SESSIONS[2]],

    "Мысли разбросаны": ARCHITECT_SESSIONS,
    "Не могу выбрать главное": ARCHITECT_SESSIONS[1:],
    "Не могу удержать внимание": ARCHITECT_SESSIONS[2:],
    "Мешают эмоции": ARCHITECT_SESSIONS[3:],
    "Нужно перейти к действию": ARCHITECT_SESSIONS[4:],

    "Не могу отключиться и уснуть": DREAM_SESSIONS,
    "Нужно глубже погрузиться в сон": DREAM_SESSIONS[1:],
    "Нужно удержать сонное состояние": DREAM_SESSIONS[2:],

    "Только Reset": RESET_SESSIONS,
    "Только Architect": ARCHITECT_SESSIONS,
    "Только Dream": DREAM_SESSIONS,
}


POSITIVE_RESULTS = [
    "Стало спокойнее",
    "Появилась структура",
    "Удалось выбрать главное",
    "Фокус усилился",
    "Появилась холодная ясность",
    "Появился импульс к действию",
    "Появилась сонливость / расслабление",
    "Стало глубже",
]

NEUTRAL_RESULTS = ["Не почувствовал изменений"]
NEGATIVE_RESULTS = ["Появился дискомфорт"]


def save_log(request, session_title, state, result, action):
    file_exists = LOG_FILE.exists()

    with LOG_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(
                ["datetime", "request", "session", "state", "result", "action"]
            )

        writer.writerow(
            [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                request,
                session_title,
                state,
                result,
                action,
            ]
        )


def reset_protocol():
    st.session_state.step = 0
    st.session_state.history = []
    st.session_state.repeat_count = 0
    st.rerun()


def analyze_final_state():
    history = st.session_state.history

    positive = sum(
        1 for h in history if any(p in h["result"] for p in POSITIVE_RESULTS)
    )
    neutral = sum(1 for h in history if "Не почувствовал" in h["result"])
    negative = sum(1 for h in history if "дискомфорт" in h["result"].lower())

    if negative > 0:
        return (
            "negative",
            "Обнаружен дискомфорт. Рекомендуется вернуться к Reset или остановить протокол.",
        )

    if positive >= max(1, len(history) / 2):
        return (
            "positive",
            "Состояние изменилось. Протокол можно считать результативным.",
        )

    if neutral > 0:
        return (
            "neutral",
            "Результат частичный. Рекомендуется повторить протокол или выбрать более мягкий вход.",
        )

    return (
        "neutral",
        "Состояние изменилось, но требует дополнительной работы.",
    )


# =========================
# SESSION STATE
# =========================

if "active_request" not in st.session_state:
    st.session_state.active_request = None

if "step" not in st.session_state:
    st.session_state.step = 0

if "history" not in st.session_state:
    st.session_state.history = []

if "repeat_count" not in st.session_state:
    st.session_state.repeat_count = 0


# =========================
# ИНТЕРФЕЙС
# =========================

st.divider()

request = st.radio("Что сейчас мешает?", list(REQUESTS.keys()))

if st.session_state.active_request != request:
    st.session_state.active_request = request
    st.session_state.step = 0
    st.session_state.history = []
    st.session_state.repeat_count = 0

protocol = REQUESTS[request]
step = st.session_state.step

st.divider()


if step >= len(protocol):
    st.success("Протокол завершён.")

    st.markdown("### Итоги прохождения")

    if st.session_state.history:
        for item in st.session_state.history:
            st.write(f"**{item['session']}** — {item['result']}")
    else:
        st.write("Ответы пока не зафиксированы.")

    status, message = analyze_final_state()

    st.markdown("### Итоговое состояние")

    if status == "positive":
        st.success(message)
    elif status == "negative":
        st.error(message)
    else:
        st.warning(message)

    if st.button("Повторить протокол"):
        reset_protocol()

else:
    item = protocol[step]
    video_url = item["url"]

    st.markdown(f"## Шаг {step + 1} из {len(protocol)}")
    st.markdown("### Ваше состояние")
    st.write(item["state"])

    st.markdown("### Рекомендуемая сессия")
    st.write(f"**{item['title']}**")
    st.write(item["description"])

    st.markdown("### Как использовать")
    st.write("1. Используйте наушники")
    st.write("2. Не отвлекайтесь")
    st.write("3. Не используйте при управлении техникой")
    st.write("4. При дискомфорте остановите сессию")

    st.video(video_url)

    result = st.radio(
        "Что изменилось?",
        [
            "Пока не проходил",
            "Стало спокойнее",
            "Появилась структура",
            "Удалось выбрать главное",
            "Фокус усилился",
            "Появилась холодная ясность",
            "Появился импульс к действию",
            "Появилась сонливость / расслабление",
            "Стало глубже",
            "Не почувствовал изменений",
            "Появился дискомфорт",
        ],
    )

    if result in POSITIVE_RESULTS:
        st.success("Состояние изменилось. Рекомендуется перейти к следующему шагу.")
        action = "next"

    elif result in NEUTRAL_RESULTS:
        if st.session_state.repeat_count == 0:
            st.warning("Эффект не зафиксирован. Рекомендуется повторить текущую сессию один раз.")
            action = "repeat"
        else:
            st.warning("Повтор уже был. Рекомендуется перейти к следующему шагу.")
            action = "next"

    elif result in NEGATIVE_RESULTS:
        st.error("Появился дискомфорт. Рекомендуется вернуться к Reset или остановить протокол.")
        action = "reset_or_stop"

    else:
        action = None

    if result != "Пока не проходил":
        if action == "next":
            if st.button("Продолжить"):
                save_log(request, item["title"], item["state"], result, "next")
                st.session_state.history.append(
                    {
                        "session": item["title"],
                        "state": item["state"],
                        "result": result,
                    }
                )
                st.session_state.step += 1
                st.session_state.repeat_count = 0
                st.rerun()

        elif action == "repeat":
            if st.button("Повторить"):
                save_log(request, item["title"], item["state"], result, "repeat")
                st.session_state.history.append(
                    {
                        "session": item["title"],
                        "state": item["state"],
                        "result": result + " → повтор",
                    }
                )
                st.session_state.repeat_count += 1
                st.rerun()

        elif action == "reset_or_stop":
            col1, col2 = st.columns(2)

            with col1:
                if st.button("Вернуться к Reset"):
                    save_log(request, item["title"], item["state"], result, "return_to_reset")
                    st.session_state.history.append(
                        {
                            "session": item["title"],
                            "state": item["state"],
                            "result": result + " → возврат к Reset",
                        }
                    )
                    st.session_state.step = 0
                    st.session_state.repeat_count = 0
                    st.rerun()

            with col2:
                if st.button("Остановить протокол"):
                    save_log(request, item["title"], item["state"], result, "stop")
                    st.session_state.history.append(
                        {
                            "session": item["title"],
                            "state": item["state"],
                            "result": result + " → остановка",
                        }
                    )
                    st.session_state.step = len(protocol)
                    st.session_state.repeat_count = 0
                    st.rerun()

    st.divider()

    if st.button("Сбросить протокол"):
        reset_protocol()


# =========================
# ЖУРНАЛ
# =========================

st.divider()

with st.expander("Журнал прохождения"):
    if LOG_FILE.exists():
        st.write(f"Файл журнала: `{LOG_FILE}`")
        st.dataframe(
            list(csv.DictReader(LOG_FILE.open("r", encoding="utf-8"))),
            use_container_width=True,
        )
    else:
        st.write("Журнал пока пуст.")
