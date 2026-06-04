import os
import sys
import ctypes
import subprocess
import tkinter as tk
from tkinter import scrolledtext  # Для удобного текстового поля с прокруткой
import winsound
from PIL import Image, ImageTk

TARGET_DNS = "111.88.96.50"


# -----------------------------
# Права администратора
# -----------------------------

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


# -----------------------------
# Пути ресурсов
# -----------------------------

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# -----------------------------
# Определение активного адаптера
# -----------------------------

def get_active_adapter():
    try:
        ps_cmd = (
            "Get-NetRoute -DestinationPrefix 0.0.0.0/0 | "
            "Get-NetIPInterface | "
            "Select-Object -ExpandProperty InterfaceAlias"
        )

        result = subprocess.run(
            ["powershell", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            encoding="utf-8",
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        adapter_name = result.stdout.strip()

        if adapter_name:
            return adapter_name.split("\n")[0].strip()

    except Exception as e:
        print(e)

    return "Wi-Fi"


# -----------------------------
# Звук
# -----------------------------

def play_success_sound():
    try:
        winsound.PlaySound(
            "Notification.Default",
            winsound.SND_ALIAS | winsound.SND_ASYNC
        )
    except:
        pass


# -----------------------------
# Проверка статуса
# -----------------------------

def check_current_status():
    adapter = get_active_adapter()

    try:
        result = subprocess.run(
            [
                "netsh",
                "interface",
                "ip",
                "show",
                "dns",
                f"name={adapter}"
            ],
            capture_output=True,
            text=True,
            encoding="cp866",
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        if TARGET_DNS in result.stdout:
            status_label.config(
                text="Управление доступом Gemini\nСтатус: ДОСТУП ЕСТЬ",
                fg="#39ff14"
            )
        else:
            status_label.config(
                text="Управление доступом Gemini\nСтатус: ДОСТУПА НЕТ",
                fg="#ff3333"
            )

    except Exception:
        status_label.config(
            text="Управление доступом Gemini\nСтатус: НЕИЗВЕСТНО",
            fg="#ffaa00"
        )


# -----------------------------
# Включить
# -----------------------------

def enable_gemini():
    adapter = get_active_adapter()
    try:
        subprocess.run(
            [
                "netsh",
                "interface",
                "ip",
                "set",
                "dns",
                f"name={adapter}",
                "source=dhcp"
            ],
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        subprocess.run(
            [
                "netsh",
                "interface",
                "ip",
                "set",
                "dns",
                f"name={adapter}",
                "source=static",
                "address=111.88.96.50",
                "register=primary"
            ],
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        subprocess.run(
            [
                "netsh",
                "interface",
                "ip",
                "add",
                "dns",
                f"name={adapter}",
                "index=2",
                "address=111.88.96.51"
            ],
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        status_label.config(
            text="Управление доступом Gemini\nСтатус: ДОСТУП ЕСТЬ",
            fg="#39ff14"
        )
        play_success_sound()

    except subprocess.CalledProcessError:
        status_label.config(
            text="Ошибка: нужны права администратора",
            fg="#ffaa00"
        )


# -----------------------------
# Выключить
# -----------------------------

def disable_gemini():
    adapter = get_active_adapter()
    try:
        subprocess.run(
            [
                "netsh",
                "interface",
                "ip",
                "set",
                "dns",
                f"name={adapter}",
                "source=dhcp"
            ],
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        status_label.config(
            text="Управление доступом Gemini\nСтатус: ДОСТУПА НЕТ",
            fg="#ff3333"
        )
        play_success_sound()

    except subprocess.CalledProcessError:
        status_label.config(
            text="Ошибка изменения конфигурации",
            fg="#ffaa00"
        )


# -----------------------------
# Окно "ИНФО" (Инструкция)
# -----------------------------

def open_info_window():
    # Создаем дочернее окно поверх основного
    info_win = tk.Toplevel(root)
    info_win.title("Инструкция и Сведения")
    info_win.geometry("500x400")
    info_win.resizable(False, False)
    info_win.configure(bg="#050608")
    
    # Делаем окно модальным (пока не закроют, главное окно неактивно) - по желанию
    info_win.transient(root)
    info_win.grab_set()

    # Попытка установить иконку дочернему окну
    try:
        info_win.iconphoto(False, app_icon)
    except:
        pass

    # Заголовок внутри окна
    title_lbl = tk.Label(
        info_win, 
        text="ИНФОРМАЦИЯ", 
        font=("Consolas", 14, "bold"), 
        bg="#050608", 
        fg="#39ff14"
    )
    title_lbl.pack(pady=15)

    # Текстовая область с полосой прокрутки (Scrollbar) для вашей инструкции
    info_text = scrolledtext.ScrolledText(
        info_win, 
        font=("Consolas", 10), 
        bg="#0d0e11", 
        fg="#bdc3c7",
        insertbackground="#39ff14", # Цвет курсора
        bd=0, 
        highlightthickness=1,
        highlightbackground="#191919",
        highlightcolor="#39ff14",
        wrap=tk.WORD
    )
    info_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

    # --- ТЕКСТ ИНСТРУКЦИИ ---
    instruction_content = (
        "==================================================\n"
        "          ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ\n"
        "==================================================\n\n"
        "1. ОБЩИЕ СВЕДЕНИЯ:\n"
        "Данная программа предназначена для автоматического\n"
        "переключения конфигурации DNS-серверов активного\n"
        "сетевого адаптера для обхода ограничений Gemini.\n\n"
        "2. ПОРЯДОК РАБОТЫ:\n"
        "• Кнопка [ВКЛЮЧИТЬ ДОСТУП] прописывает выделенные\n"
        "  адреса DNS (111.88.96.50 / 111.88.96.51).\n"
        "• Кнопка [ВЫКЛЮЧИТЬ ДОСТУП] возвращает настройки\n"
        "  в автоматический режим (DHCP).\n\n"
        "3. ВОЗМОЖНЫЕ ПРОБЛЕМЫ:\n"
        "• Баги (сам когда тестировал не выявил)\n"
        "  Ошибки\n"
        "• Не судите строго :)\n\n"
        "--------------------------------------------------\n"
        "Программа была сделана по сайту xbox-dns.ru\n"
        "Версия: 1.0 Разработчик программы - тг @Andrei_system"
    )
    
    info_text.insert(tk.END, instruction_content)
    info_text.config(state=tk.DISABLED) # Запрещаем редактирование текста пользователем

    # Кнопка закрытия окна
    btn_close = tk.Button(
        info_win,
        text="ЗАКРЫТЬ",
        command=info_win.destroy,
        font=("Consolas", 10, "bold"),
        bg="#191919",
        fg="#8f8f8f",
        activebackground="#0d0e11",
        activeforeground="#ff3333",
        bd=0,
        highlightthickness=0,
        cursor="hand2"
    )
    btn_close.pack(pady=15)


# -----------------------------
# Перезапуск от администратора
# -----------------------------

if not is_admin():
    script = os.path.abspath(sys.argv[0])
    ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        sys.executable,
        f'"{script}"',
        None,
        1
    )
    sys.exit()


# -----------------------------
# GUI
# -----------------------------

root = tk.Tk()
root.title("Gemini Unlocker")
root.resizable(False, False)

BG_COLOR = "#0d0e11"
GREEN = "#39ff14"
RED = "#ff3333"

try:
    app_icon = tk.PhotoImage(file=resource_path("icon.png"))
    root.iconphoto(False, app_icon)
except:
    pass

try:
    bg_image = Image.open(resource_path("background.jpg"))
    img_width, img_height = bg_image.size

    root.geometry(f"{img_width}x{img_height}")

    bg_photo = ImageTk.PhotoImage(bg_image)

    bg_label = tk.Label(
        root,
        image=bg_photo,
        borderwidth=0,
        highlightthickness=0
    )
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

except Exception:
    img_width = 1024
    img_height = 640

    root.geometry(f"{img_width}x{img_height}")
    root.configure(bg=BG_COLOR)


# ---------------------------------
# Hover эффекты для кнопок
# ---------------------------------

def on_enter_enable(event):
    btn_enable.config(fg=GREEN)

def on_leave_enable(event):
    btn_enable.config(fg="#8f8f8f")

def on_enter_disable(event):
    btn_disable.config(fg=RED)

def on_leave_disable(event):
    btn_disable.config(fg="#8f8f8f")

def on_enter_info(event):
    btn_info.config(fg="#00ffff") # При наведении текст становится бирюзовым

def on_leave_info(event):
    btn_info.config(fg="#5f5f5f") # В покое кнопка почти сливается


# ---------------------------------
# ВКЛЮЧИТЬ
# ---------------------------------

btn_enable = tk.Button(
    root,
    text="ВКЛЮЧИТЬ ДОСТУП",
    command=enable_gemini,
    font=("Consolas", 12, "bold"),
    bg="#191919",
    fg="#8f8f8f",
    activebackground="#050608",
    activeforeground=GREEN,
    bd=0,
    highlightthickness=0,
    relief="flat",
    cursor="hand2"
)

btn_enable.place(
    x=512,
    y=145,
    width=415,
    height=55,
    anchor="center"
)

btn_enable.bind("<Enter>", on_enter_enable)
btn_enable.bind("<Leave>", on_leave_enable)


# ---------------------------------
# ВЫКЛЮЧИТЬ
# ---------------------------------

btn_disable = tk.Button(
    root,
    text="ВЫКЛЮЧИТЬ ДОСТУП",
    command=disable_gemini,
    font=("Consolas", 12, "bold"),
    bg="#191919",
    fg="#8f8f8f",
    activebackground="#050608",
    activeforeground=RED,
    bd=0,
    highlightthickness=0,
    relief="flat",
    cursor="hand2"
)

btn_disable.place(
    x=512,
    y=495,
    width=300,
    height=55,
    anchor="center"
)

btn_disable.bind("<Enter>", on_enter_disable)
btn_disable.bind("<Leave>", on_leave_disable)


# ---------------------------------
# Статус
# ---------------------------------

status_label = tk.Label(
    root,
    text="Управление доступом Gemini\nСтатус: Проверка...",
    font=("Consolas", 11, "bold"),
    fg=GREEN,
    bg="#000000",
    justify="left"
)

status_label.place(
    x=820,
    y=415,
    width=380,
    height=105,
    anchor="center"
)


# ---------------------------------
# КНОПКА ИНФО
# ---------------------------------

btn_info = tk.Button(
    root,
    text="[ ИНФО ]",
    command=open_info_window,
    font=("Consolas", 11, "bold"),
    bg="#191919",             
    fg="#5f5f5f",             # Тусклый цвет текста по умолчанию
    activebackground=BG_COLOR,
    activeforeground="#00ffff",
    bd=0,
    highlightthickness=0,
    relief="flat",
    cursor="hand2"
)


btn_info.place(
    x=960,
    y=580,
    width=100,
    height=35,
    anchor="center"
)

btn_info.bind("<Enter>", on_enter_info)
btn_info.bind("<Leave>", on_leave_info)


root.after(200, check_current_status)
root.mainloop()