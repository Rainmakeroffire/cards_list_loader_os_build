import requests
import time
import json
import urllib3
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from config import *


def build_curl(url: str, headers: Dict[str, str], body: Dict[str, Any], params: Dict[str, str]) -> str:
    curl = f"curl -X POST \"{url}"
    if params:
        q = "&".join(f"{k}={v}" for k, v in params.items())
        curl += f"?{q}"
    curl += "\""
    for k, v in headers.items():
        curl += f" -H '{k}: {v}'"
    curl += f" -d '{json.dumps(body, ensure_ascii=False)}'"
    return curl


def log_request(response: requests.Response, curl_cmd: str, log_file: str):
    with open(log_file, "a", encoding="utf-8") as f:
        now = datetime.now(timezone.utc).astimezone()
        f.write(f"Дата и время запроса: {now.isoformat()}\n")
        f.write(f"cURL: {curl_cmd}\n")
        f.write(f"HTTP статус: {response.status_code}\n")
        try:
            pretty_json = json.dumps(response.json(), ensure_ascii=False, indent=2)
        except Exception:
            pretty_json = response.text
        f.write(f"Ответ JSON:\n{pretty_json}\n\n")


def get_all_cards(
    filters: Optional[Dict[str, Any]],
    sort: Optional[Dict[str, Any]],
    cursor: Dict[str, Any],
    locale: str,
    use_token: bool,
    token: str = "",
    x_supplier: str = "",
    x_user: str = "",
    max_cards: int = MAX_CARDS,
    pause: float = PAUSE,
    service_url: Optional[str] = None,
    log_file: str = LOG_FILE,
) -> List[Dict[str, Any]]:

    all_cards = []
    start_time = time.time()

    if use_token:
        url = API_URL_TOKEN
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        extra_args = {}
        url_for_log = API_URL_TOKEN
    else:
        url = service_url or API_URL_NO_TOKEN
        headers = {
            "X-Supplier-Id": x_supplier,
            "X-User-Id": x_user,
            "Content-Type": "application/json"
        }
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        extra_args = {"verify": False}
        url_for_log = API_URL_TOKEN  # имитация в логе

    open(log_file, "w", encoding="utf-8").close() #очистка лога

    while True:
        body = {"settings": {"cursor": cursor}}
        if filters:
            body["settings"]["filter"] = filters
        if sort:
            body["settings"]["sort"] = sort

        headers_for_log = dict(headers)
        if not use_token:
            headers_for_log.pop("X-Supplier-Id", None)
            headers_for_log.pop("X-User-Id", None)

        curl_params = {"locale": locale} if locale else {}
        curl_cmd = build_curl(url_for_log, headers_for_log, body, curl_params)

        try:
            response = requests.post(url, headers=headers, params={"locale": locale}, json=body, **extra_args)
            log_request(response, curl_cmd, log_file)
        except Exception as e:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"Ошибка при запросе: {str(e)}\n")
            break

        if response.status_code != 200:
            break

        data = response.json()
        cards = data.get("cards", [])
        all_cards.extend(cards)

        if len(all_cards) >= max_cards:
            all_cards = all_cards[:max_cards]
            break

        cur = data.get("cursor", {})
        total = cur.get("total", 0)
        if total < cursor.get("limit", 100):
            break

        cursor = {
            "updatedAt": cur.get("updatedAt"),
            "nmID": cur.get("nmID"),
            "limit": cursor.get("limit", 100)
        }

        time.sleep(pause)

    duration = time.time() - start_time
    with open(log_file, "a", encoding="utf-8") as f:
        f.write("=== Итог ===\n")
        f.write(f"Общая продолжительность: {duration:.2f} секунд\n")
        f.write(f"Всего карточек получено: {len(all_cards)}\n")

    return all_cards
