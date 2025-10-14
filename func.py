import re

def parse_str_array_field(text: str):
    """'a, b, c' -> ['a','b','c']; пустое -> None"""
    if not text or not text.strip():
        return None
    return [t.strip() for t in text.split(",") if t.strip()]

def parse_int(text: str):
    try:
        return int(text.strip())
    except Exception:
        return None

def parse_bool(text: str):
    """
    Преобразует строку из Combobox в bool или None:
    "" -> None, "true" -> True, "false" -> False (регистронезависимо)
    """
    if text is None:
        return None
    t = text.strip().lower()
    if t == "":
        return None
    if t == "true":
        return True
    if t == "false":
        return False
    return None


# --- Контекстное меню для Entry/ttk.Entry ---
def add_context_menu(widget_list):
    import tkinter as tk
    from tkinter import ttk

    menu = tk.Menu(tearoff=0)

    def copy():
        w = tk._default_root.focus_get()
        if isinstance(w, (tk.Entry, ttk.Entry)):
            try:
                text = w.selection_get()
                w.clipboard_clear()
                w.clipboard_append(text)
            except tk.TclError:
                pass

    def cut():
        w = tk._default_root.focus_get()
        if isinstance(w, (tk.Entry, ttk.Entry)):
            try:
                text = w.selection_get()
                w.clipboard_clear()
                w.clipboard_append(text)
                w.delete("sel.first", "sel.last")
            except tk.TclError:
                pass

    def paste():
        w = tk._default_root.focus_get()
        if isinstance(w, (tk.Entry, ttk.Entry)):
            try:
                text = w.clipboard_get()
            except tk.TclError:
                return
            state = w.cget("state") if hasattr(w, "cget") else None
            if state == "disabled":
                return
            restored = False
            if state == "readonly":
                w.config(state="normal")
                restored = True
            try:
                try:
                    sel_start = w.index("sel.first")
                    sel_end = w.index("sel.last")
                    w.delete(sel_start, sel_end)
                    w.insert(sel_start, text)
                except tk.TclError:
                    w.insert("insert", text)
            except Exception:
                pass
            if restored:
                w.config(state="readonly")

    menu.add_command(label="Copy", command=copy)
    menu.add_command(label="Cut", command=cut)
    menu.add_command(label="Paste", command=paste)

    def show_menu(event):
        menu.tk_popup(event.x_root, event.y_root)

    for w in widget_list:
        w.bind("<Button-3>", show_menu)


def validate_filename(filename: str) -> bool:
    """
    Проверяет, что имя файла допустимо для Windows:
    - Не содержит запрещённые символы: <>:"/\|?*
    - Не заканчивается пробелом или точкой
    - Допускает кириллицу, латиницу, цифры, пробел, дефис, подчёркивание и точку (для расширения)
    """
    if not filename:
        return True
    
    forbidden_chars = '<>:"/\\|?*'
    if any(c in forbidden_chars for c in filename):
        return False
    if filename[-1] in (' ', '.'):
        return False
    return True


def parse_int_array_field(text: str):
    """
    Преобразует строку формата "123, 456, 789" в список [123,456,789].
    Допускаются лишние пробелы и запятые в конце/начале.
    Пустая строка -> None.
    """
    if not text or not text.strip():
        return None
    
    parts = [p.strip() for p in text.split(",")]
    nums = []
    for p in parts:
        if not p:
            continue
        try:
            nums.append(int(p))
        except ValueError:
            continue

    return nums if nums else None


def validate_int_array_input(s: str) -> bool:
    """
    Валидатор для ввода "число, число, число" в Entry (используется как validatecommand).
    Правила:
    - пустая строка допустима (пользователь ещё вводит)
    - допускаются только цифры, запятые и пробелы
    - запрещён ведущий символ ','
    - запрещены подряд идущие запятые в любом виде: ',,' или ', ,', ',  ,' и т.п.
    - запрещены двойные пробелы
    - разрешены промежуточные состояния:
        "123", "123,", "123, ", "123, 4", "123,45" и т.п.
      — то есть пользователь может вводить запятую, а затем дописывать пробел/число.
    - итоговое корректное выражение соответствует паттерну: "число(, число)*" (один пробел после запятой опционален)
    """
    # пустой ввод — разрешён (пользователь ещё формирует значение)
    if s == "":
        return True

    # 1) разрешённые символы только: цифры, запятая, пробел
    if any(ch not in "0123456789, " for ch in s):
        return False

    # 2) не должен начинаться с запятой
    if s[0] == ",":
        return False

    # 3) не допускаем подряд идущие пробелы
    if "  " in s:
        return False

    # 4) не допускаем последовательности "запятая … запятая" (даже если между ними пробелы)
    #    это ловит ',,', ', ,', ',  ,' и т.д.
    if re.search(r',\s*,', s):
        return False

    # 5) окончательная/промежуточная маска:
    #    \d+            — одна или более цифр
    #    (?:,\s?\d*)*   — ноль или более групп: ',' + (опционально один пробел) + (0+ цифр)
    #                   (\d* позволяет промежуточное состояние, например "123," или "123, ")
    #    Примеры, которые пройдут:
    #      '123', '123,', '123, ', '123,4', '123, 45', '123,45,678', '123, 45, '
    if re.fullmatch(r'\d+(?:,\s?\d*)*', s):
        return True

    # В остальных случаях — запрещаем
    return False


def get_int_array_from_entry(entry_widget):
    """
    Универсальный парсер массива чисел из Tkinter.Entry.
    Возвращает список int или None.
    """
    text = entry_widget.get().strip()
    if not text:
        return None
    return parse_int_array_field(text)