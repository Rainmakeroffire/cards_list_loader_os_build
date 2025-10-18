import tkinter as tk
from tkinter import ttk
# from PIL import ImageTk
from func import add_context_menu, validate_filename, validate_int_array_input 
from config_loader import load_settings


def create_main_window():
    settings = load_settings()

    root = tk.Tk()
    root.title("Cards List Loader")
    root.geometry("1050x685")
    root.resizable(False, False)

    # icon = ImageTk.PhotoImage(file="img/favicon-16x16.png")
    # root.iconphoto(False, icon)

    # --- Основные колонки ---
    main_frame = tk.Frame(root, bg="", highlightthickness=0)
    main_frame.pack(fill="both", expand=True, padx=10, pady=5)

    left_frame = tk.Frame(main_frame)
    left_frame.pack(side="left", fill="both", expand=True)

    right_frame = tk.Frame(main_frame, width=120)
    right_frame.pack(side="right", fill="y")

    # --- Авторизация (вся ширина первой колонки) ---
    auth_frame = ttk.LabelFrame(left_frame, text="Авторизация")
    auth_frame.pack(fill="x", pady=5, padx=(0, 5))

    auth_mode = tk.StringVar(value="no_token")
    rb_token = ttk.Radiobutton(auth_frame, text="По токену", variable=auth_mode, value="token")
    rb_no_token = ttk.Radiobutton(auth_frame, text="Без токена", variable=auth_mode, value="no_token")
    rb_token.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    rb_no_token.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    token_frame = ttk.LabelFrame(auth_frame, text="По токену")
    token_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
    ttk.Label(token_frame, text="Token:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    token_entry = ttk.Entry(token_frame, width=50, state="readonly")
    token_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    no_token_frame = ttk.LabelFrame(auth_frame, text="Без токена")
    no_token_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
    ttk.Label(no_token_frame, text="X-Supplier-Id:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    x_supplier_entry = ttk.Entry(no_token_frame, width=30)
    x_supplier_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    ttk.Label(no_token_frame, text="X-User-Id:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    x_user_entry = ttk.Entry(no_token_frame, width=30)
    x_user_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    # Подставляем TOKEN из settings
    if "TOKEN" in settings:
        token_entry.config(state="normal")
        token_entry.delete(0, "end")
        token_entry.insert(0, str(settings["TOKEN"]))
        token_entry.config(state="readonly")

    def toggle_auth_fields(*args):
        if auth_mode.get() == "token":
            token_entry.config(state="normal")
            x_supplier_entry.config(state="disabled")
            x_user_entry.config(state="disabled")
        else:
            token_entry.config(state="readonly")
            x_supplier_entry.config(state="normal")
            x_user_entry.config(state="normal")

    auth_mode.trace_add("write", toggle_auth_fields)
    toggle_auth_fields()

    # --- Горизонтальное деление внутри первой колонки ---
    bottom_frame = tk.Frame(left_frame)
    bottom_frame.pack(fill="both", expand=True)

    left_bottom = tk.Frame(bottom_frame)
    left_bottom.pack(side="left", fill="both", expand=True)

    right_bottom = tk.Frame(bottom_frame, width=210)
    right_bottom.pack(side="right", fill="y", padx=5)

    # --- Query Params ---
    query_frame = ttk.LabelFrame(left_bottom, text="Query Params")
    query_frame.pack(fill="x", pady=5)
    ttk.Label(query_frame, text="locale:").pack(side="left", padx=5)
    locale_var = tk.StringVar(value="")
    locale_combo = ttk.Combobox(query_frame, textvariable=locale_var,
                                values=["", "ru", "en", "zh"], width=10, state="readonly")
    locale_combo.pack(side="left", padx=5, pady=(0, 5))

    # --- Request Body Schema ---
    body_frame = ttk.LabelFrame(left_bottom, text="Request Body Schema")
    body_frame.pack(fill="both", expand=True, pady=5)

    # sort
    sort_frame = ttk.LabelFrame(body_frame, text="sort")
    sort_frame.pack(fill="x", padx=5, pady=5)
    ttk.Label(sort_frame, text="ascending:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    ascending_var = tk.StringVar(value="")
    ascending_combo = ttk.Combobox(sort_frame, textvariable=ascending_var,
                                   values=["", "true", "false"], width=10, state="readonly")
    ascending_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    # filter
    filter_frame = ttk.LabelFrame(body_frame, text="filter")
    filter_frame.pack(fill="x", padx=5, pady=5)

    ttk.Label(filter_frame, text="withPhoto:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    with_photo_var = tk.StringVar(value="-1")
    with_photo_combo = ttk.Combobox(filter_frame, textvariable=with_photo_var,
                                    values=["-1", "0", "1"], width=5, state="readonly")
    with_photo_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    ttk.Label(filter_frame, text="textSearch:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    text_search_entry = ttk.Entry(filter_frame, width=40)
    text_search_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    ttk.Label(filter_frame, text="tagIDs (через запятую):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    tag_ids_entry = ttk.Entry(filter_frame, width=40)
    tag_ids_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
    vcmd_int_array = (root.register(lambda s: validate_int_array_input(s)), "%P")
    tag_ids_entry.config(validate="key", validatecommand=vcmd_int_array)

    ttk.Label(filter_frame, text="allowedCategoriesOnly:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
    allowed_categories_var = tk.StringVar(value="")
    allowed_categories_combo = ttk.Combobox(filter_frame, textvariable=allowed_categories_var,
                                            values=["", "true", "false"], width=10, state="readonly")
    allowed_categories_combo.grid(row=3, column=1, padx=5, pady=5, sticky="w")

    ttk.Label(filter_frame, text="objectIDs (через запятую):").grid(row=4, column=0, padx=5, pady=5, sticky="w")
    object_ids_entry = ttk.Entry(filter_frame, width=40)
    object_ids_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")
    vcmd_int_array = (root.register(lambda s: validate_int_array_input(s)), "%P")
    object_ids_entry.config(validate="key", validatecommand=vcmd_int_array)

    ttk.Label(filter_frame, text="brands (через запятую):").grid(row=5, column=0, padx=5, pady=5, sticky="w")
    brands_entry = ttk.Entry(filter_frame, width=40)
    brands_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")

    ttk.Label(filter_frame, text="imtID:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
    imt_id_entry = ttk.Entry(filter_frame, width=20)
    imt_id_entry.grid(row=6, column=1, padx=5, pady=5, sticky="w")

    # cursor
    cursor_frame = ttk.LabelFrame(body_frame, text="cursor")
    cursor_frame.pack(fill="x", padx=5, pady=5)

    ttk.Label(cursor_frame, text="limit:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    limit_entry = ttk.Entry(cursor_frame, width=10)
    limit_entry.insert(0, "100")
    limit_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    vcmd_int = (root.register(lambda s: s == "" or s.isdigit()), "%P")
    limit_entry.config(validate="key", validatecommand=vcmd_int)

    ttk.Label(cursor_frame, text="updatedAt:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    updated_at_entry = ttk.Entry(cursor_frame, width=30)
    updated_at_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    ttk.Label(cursor_frame, text="nmID:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    cursor_nm_id_entry = ttk.Entry(cursor_frame, width=30)
    cursor_nm_id_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    # --- Дополнительные настройки (справа) ---
    extra_frame = ttk.LabelFrame(right_bottom, text="Дополнительные настройки")
    extra_frame.pack(fill="both", expand=True, pady=5)

    ttk.Label(extra_frame, text="Лимит выгрузки:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    max_cards_entry = ttk.Entry(extra_frame, width=15, validate="key")
    max_cards_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    vcmd_int = (root.register(lambda s: s == "" or s.isdigit()), "%P")
    max_cards_entry.config(validate="key", validatecommand=vcmd_int)

    if "MAX_CARDS" in settings:
        max_cards_entry.insert(0, str(settings["MAX_CARDS"]))

    ttk.Label(extra_frame, text="Интервал (сек.):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    pause_entry = ttk.Entry(extra_frame, width=15, validate="key")
    pause_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
    vcmd_float = (root.register(
        lambda s: (
            s == ""
            or s.isdigit()
            or (s.count(".") == 1 and s.replace(".", "").isdigit())
        )
    ), "%P")
    pause_entry.config(validate="key", validatecommand=vcmd_float)

    if "PAUSE" in settings:
        pause_entry.insert(0, str(settings["PAUSE"]))

    ttk.Label(extra_frame, text="Служебный URL:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    service_url_entry = ttk.Entry(extra_frame, width=40)
    service_url_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    if "API_URL_NO_TOKEN" in settings:
        service_url_entry.insert(0, str(settings["API_URL_NO_TOKEN"]))

    ttk.Label(extra_frame, text="Имя лог-файла:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
    log_file_entry = ttk.Entry(extra_frame, width=30)
    log_file_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
    vcmd_filename = (root.register(lambda s: validate_filename(s)), "%P")
    log_file_entry.config(validate="key", validatecommand=vcmd_filename)

    if "LOG_FILE" in settings:
        log_file_entry.insert(0, str(settings["LOG_FILE"]))

    # --- Кнопка справа (вторая колонка) ---
    run_button = tk.Button(right_frame, text="Запросить карточки")
    run_button.pack(anchor="n", padx=30, pady=13)

    # Контекстное меню
    all_entries = [
        token_entry, x_supplier_entry, x_user_entry,
        text_search_entry, tag_ids_entry, object_ids_entry, brands_entry, imt_id_entry,
        limit_entry, updated_at_entry, cursor_nm_id_entry,
        max_cards_entry, pause_entry, service_url_entry, log_file_entry
    ]
    add_context_menu(all_entries)

    return {
        "root": root,
        "run_button": run_button,
        "auth_mode": auth_mode,
        "token_entry": token_entry,
        "x_supplier_entry": x_supplier_entry,
        "x_user_entry": x_user_entry,
        "locale_var": locale_var,
        "ascending_var": ascending_var,
        "with_photo_var": with_photo_var,
        "text_search_entry": text_search_entry,
        "tag_ids_entry": tag_ids_entry,
        "allowed_categories_var": allowed_categories_var,
        "object_ids_entry": object_ids_entry,
        "brands_entry": brands_entry,
        "imt_id_entry": imt_id_entry,
        "limit_entry": limit_entry,
        "updated_at_entry": updated_at_entry,
        "cursor_nm_id_entry": cursor_nm_id_entry,
        "max_cards_entry": max_cards_entry,
        "pause_entry": pause_entry,
        "service_url_entry": service_url_entry,
        "log_file_entry": log_file_entry,
    }
