import os
import asyncio
import subprocess
from pathlib import Path

from telegram import Update
from telegram.ext import MessageHandler, filters
from telegram.ext import Application, CommandHandler, ContextTypes

TG_TOKEN = os.environ["TG_BOT_TOKEN"]
ALLOWED_USER_ID = int(os.environ.get("TG_ALLOWED_USER_ID", "0"))

DATA_DIR = Path(os.environ.get("DATA_DIR", "/app/data"))
MM_XLSX = Path(os.environ.get("MM_XLSX_PATH", str(DATA_DIR / "mm.xlsx")))
LOG_DIR = DATA_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LAST_LOG = LOG_DIR / "last_run.log"

def allowed(update: Update) -> bool:
    u = update.effective_user
    return bool(u and u.id == ALLOWED_USER_ID)

def build_cmd():
    # Скрипт должен обновлять файл MM_XLSX (по умолчанию /app/data/mm.xlsx)
    return ["python", "cr_cc_history.py"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return
    await update.message.reply_text(
        "Команды:\n"
        "/update — обновить mm.xlsx (запустить cr_cc_history.py)\n"
        "/send — прислать текущий mm.xlsx\n"
        "/status — статус"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return
    exists = MM_XLSX.exists()
    size = MM_XLSX.stat().st_size if exists else 0
    await update.message.reply_text(f"mm.xlsx exists={exists}, size={size} bytes, path={MM_XLSX}")

async def send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return
    if not MM_XLSX.exists():
        await update.message.reply_text("mm.xlsx не найден. Положи его в volume ./data как data/mm.xlsx")
        return
    await update.message.reply_document(MM_XLSX.open("rb"), filename="mm.xlsx")

async def update_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return

    await update.message.reply_text("Запускаю обновление…")

    def _run():
        env = os.environ.copy()
        env.setdefault("MM_XLSX_PATH", str(MM_XLSX))
        p = subprocess.run(build_cmd(), cwd="/app", capture_output=True, text=True, env=env)
        LAST_LOG.write_text(
            f"RC={p.returncode}\n\nSTDOUT:\n{p.stdout}\n\nSTDERR:\n{p.stderr}\n",
            encoding="utf-8"
        )
        return p.returncode, p.stdout, p.stderr

    rc, out, err = await asyncio.to_thread(_run)

    await update.message.reply_text(
        f"Готово. RC={rc}\n"
        f"STDOUT(last 1200):\n{out[-1200:]}\n\n"
        f"STDERR(last 1200):\n{err[-1200:]}"
    )

    if MM_XLSX.exists():
        await update.message.reply_document(MM_XLSX.open("rb"), filename="mm.xlsx")
    else:
        await update.message.reply_text("После выполнения mm.xlsx не найден. Проверь лог /status и last_run.log")

def main():
    app = Application.builder().token(TG_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("send", send))
    app.add_handler(CommandHandler("update", update_cmd))
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
