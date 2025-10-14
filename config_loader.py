import os
import re

SETTINGS_FILE = "settings.cfg"

def load_settings():
    """
    Загружает настройки из settings.cfg (если файл существует).
    Возвращает dict с найденными значениями.
    """
    settings = {}
    if not os.path.exists(SETTINGS_FILE):
        return settings

    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Парсим строки вида KEY=VALUE или KEY="VALUE"
            match = re.match(r'^(\w+)\s*=\s*"?([^"]+)"?$', line)
            if match:
                key, value = match.groups()
                # Преобразуем типы
                if key in ("PAUSE",):
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                elif key in ("MAX_CARDS",):
                    try:
                        value = int(value)
                    except ValueError:
                        pass
                settings[key] = value

    return settings
