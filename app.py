from tkinter import messagebox
from root import create_main_window
from script import get_all_cards
from func import parse_int, parse_str_array_field, parse_bool, get_int_array_from_entry

def run_request(ui):
    use_token = (ui["auth_mode"].get() == "token")
    token = ui["token_entry"].get().strip()
    x_supplier = ui["x_supplier_entry"].get().strip()
    x_user = ui["x_user_entry"].get().strip()
    locale = ui["locale_var"].get()

    sort = {}
    asc = parse_bool(ui["ascending_var"].get())
    if asc is not None:
        sort["ascending"] = asc
    if not sort:
        sort = None

    filters = {}
    with_photo = ui["with_photo_var"].get()
    if with_photo:
        filters["withPhoto"] = int(with_photo)
    text_search = ui["text_search_entry"].get().strip()
    if text_search:
        filters["textSearch"] = text_search
    tag_ids = get_int_array_from_entry(ui["tag_ids_entry"])
    if tag_ids:
        filters["tagIDs"] = tag_ids
    allowed = parse_bool(ui["allowed_categories_var"].get())
    if allowed is not None:
        filters["allowedCategoriesOnly"] = allowed
    obj_ids = get_int_array_from_entry(ui["object_ids_entry"])
    if obj_ids:
        filters["objectIDs"] = obj_ids
    brands = parse_str_array_field(ui["brands_entry"].get())
    if brands:
        filters["brands"] = brands
    imt_id = parse_int(ui["imt_id_entry"].get())
    if imt_id is not None:
        filters["imtID"] = imt_id
    if not filters:
        filters = None

    cursor = {}
    limit = parse_int(ui["limit_entry"].get()) or 100
    cursor["limit"] = limit
    updated_at = ui["updated_at_entry"].get().strip()
    if updated_at:
        cursor["updatedAt"] = updated_at
    cursor_nm_id = parse_int(ui["cursor_nm_id_entry"].get())
    if cursor_nm_id is not None:
        cursor["nmID"] = cursor_nm_id

    kwargs = {}
    max_cards_text = ui["max_cards_entry"].get().strip()
    if max_cards_text:
        max_cards = parse_int(max_cards_text)
        if max_cards is not None:
            kwargs["max_cards"] = max_cards

    pause_text = ui["pause_entry"].get().strip()
    if pause_text:
        try:
            kwargs["pause"] = float(pause_text)
        except ValueError:
            pass

    service_url = ui["service_url_entry"].get().strip()
    if service_url:
        kwargs["service_url"] = service_url

    log_file = ui["log_file_entry"].get().strip()
    if log_file:
        if not log_file.lower().endswith(".txt"):
            log_file += ".txt"
        kwargs["log_file"] = log_file

    try:
        cards = get_all_cards(
            filters=filters,
            sort=sort,
            cursor=cursor,
            locale=locale,
            use_token=use_token,
            token=token,
            x_supplier=x_supplier,
            x_user=x_user,
            **kwargs
        )
        messagebox.showinfo("Готово", f"Получено карточек: {len(cards)}")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        print("OK")
        sys.exit(0)

    ui = create_main_window()
    ui["run_button"].config(command=lambda: run_request(ui))
    ui["root"].mainloop()
