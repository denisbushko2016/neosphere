import csv
import secrets
import string
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ACCESS_FILE = DATA_DIR / "access_codes.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)


def generate_code():
    alphabet = string.ascii_uppercase + string.digits

    part1 = "".join(secrets.choice(alphabet) for _ in range(4))
    part2 = "".join(secrets.choice(alphabet) for _ in range(4))

    return f"NS-{part1}-{part2}"


def ensure_file():
    if not ACCESS_FILE.exists():
        with ACCESS_FILE.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["code", "type", "activated_at", "expires_at", "status"],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "code": "NEO-ADMIN-2026",
                    "type": "admin",
                    "activated_at": "",
                    "expires_at": "",
                    "status": "active",
                }
            )


def load_codes():
    ensure_file()

    with ACCESS_FILE.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_codes(rows):
    with ACCESS_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["code", "type", "activated_at", "expires_at", "status"],
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    rows = load_codes()
    existing_codes = {row["code"] for row in rows}

    while True:
        code = generate_code()
        if code not in existing_codes:
            break

    rows.append(
        {
            "code": code,
            "type": "client",
            "activated_at": "",
            "expires_at": "",
            "status": "new",
        }
    )

    save_codes(rows)

    print()
    print("[OK] Новый клиентский ключ создан:")
    print(code)
    print()
    print(f"Файл обновлён: {ACCESS_FILE}")
    print()
    print("Отправь клиенту:")
    print("----------------")
    print(f"Ваш код доступа NeoSphere: {code}")
    print("Срок действия: 30 дней с момента первой активации.")
    print("----------------")


if __name__ == "__main__":
    main()
