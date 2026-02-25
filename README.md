# mm-bot-cloud (Telegram bot + cr_cc_history.py)

Что делает:
- Telegram-бот принимает команду `/update` и запускает `cr_cc_history.py`
- `cr_cc_history.py` обновляет историю боёв в `mm.xlsx`
- Бот присылает обновлённый `mm.xlsx` обратно в Telegram

## Важно про mm.xlsx
- Файл должен лежать в `./data/mm.xlsx` (это volume, переживает перезапуски).
- Скрипт использует переменную окружения `MM_XLSX_PATH` (по умолчанию `/app/data/mm.xlsx`).

## Переменные окружения
Скопируй `.env.example` -> `.env` и заполни:
- `TG_BOT_TOKEN`
- `TG_ALLOWED_USER_ID` (твой numeric id)
- токен Clash Royale API (имя переменной зависит от Settings!B2 в mm.xlsx)

Пример: если в `Settings!B2` стоит `CR_OFFICIAL_TOKEN`, то в `.env` должно быть `CR_OFFICIAL_TOKEN=...`.

## Запуск локально (Docker Compose)
```bash
docker compose up -d --build
docker compose logs -f
```

## Telegram команды
- `/start`
- `/update` — обновить и прислать mm.xlsx
- `/send` — прислать текущий mm.xlsx
- `/status` — показать наличие/размер файла

## Деплой в облако
- Для Railway/Render/Fly: используй Dockerfile из `app/`, подключи persistent disk/volume в `/app/data`
