# @iwanTriker, 2026


import customtkinter as ctk
import requests
import os
import zipfile
import shutil
import gdown
import json
import threading
from pathlib import Path
from tkinter import filedialog

#Prefers
LIST_FILE_ID = "13V3sRpjRNpaWxPs2CzeVNrsfMWDQP0wd"
MODS_FILE_ID = "1hrnB2_qhUa4DH7LBoDvoy24NCUC4PgFL"
CONFIG_FILE = "config.json"
TEMP_ZIP = "temp.zip"

#PATH
DEFAULT_PATH = str(Path(os.getenv('APPDATA')) / ".tlauncher" / "legacy" / "Minecraft" / "game" / "mods")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ModManager")
        self.geometry("500x400")
        self.resizable(False, False)

        #Startup
        self.config = self.load_config()
        self.current_version = self.config.get("version", "0.0.0")
        self.mods_path = self.config.get("path", DEFAULT_PATH)

        #UI
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.label = ctk.CTkLabel(self.main_frame, text="Modpack Updater", font=("Segoe UI", 24, "bold"))
        self.label.pack(pady=(15, 5))

        self.ver_label = ctk.CTkLabel(self.main_frame, text=f"Версия модов: {self.current_version}", font=("Segoe UI", 13))
        self.ver_label.pack(pady=0)

        #Path
        self.path_label = ctk.CTkLabel(self.main_frame, text=f"Путь: ...{self.mods_path[-40:]}", font=("Segoe UI", 10), text_color="gray")
        self.path_label.pack(pady=5)

        self.status_label = ctk.CTkLabel(self.main_frame, text="Готов к работе", font=("Segoe UI", 13, "italic"))
        self.status_label.pack(pady=(10, 5))

        self.progress = ctk.CTkProgressBar(self.main_frame, width=380)
        self.progress.set(0)
        self.progress.pack(pady=10)

        #StateBT
        self.btn_update = ctk.CTkButton(self.main_frame, text="ПРОВЕРИТЬ И ОБНОВИТЬ", font=("Segoe UI", 14, "bold"), height=45, fg_color="#1f538d", command=self.start_update_thread)
        self.btn_update.pack(pady=10)

        #ChangePaths
        self.bottom_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.bottom_frame.pack(pady=10)

        self.btn_open = ctk.CTkButton(self.bottom_frame, text="Открыть папку", width=140, command=self.open_folder)
        self.btn_open.grid(row=0, column=0, padx=10)

        self.btn_path = ctk.CTkButton(self.bottom_frame, text="Изменить путь", width=140, fg_color="#3d3d3d", command=self.change_path)
        self.btn_path.grid(row=0, column=1, padx=10)                                                        

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {"version": "0.0.0", "path": DEFAULT_PATH}
        
    APP_VERSION_URL = "nul"
    EXE_DOWNLOAD_ID = "null"

    def check_app_self_update(current_app_version):
        try:
            response = requests.get(APP_VERSION_URL).json()
            remote_app_version = response.get("app_version")
            
            if remote_app_version != current_app_version:
                #Sownload
                new_exe_path = "updater_new.exe"
                gdown.download(f'https://drive.google.com/uc?id={EXE_DOWNLOAD_ID}', new_exe_path, quiet=True)
                
                #Replace.bat
                with open("update.bat", "w") as f:
                    f.write(f"""
                    @echo off
                    timeout /t 2 /nobreak > nul
                    del "updater.exe"
                    ren "{new_exe_path}" "updater.exe"
                    start "" "updater.exe"
                    del "%~f0"
                    """)
                
                #batopn
                os.startfile("update.bat")
                os._exit(0)
        except:
            pass

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"version": self.current_version, "path": self.mods_path}, f)

    def open_folder(self):
        if os.path.exists(self.mods_path):
            os.startfile(self.mods_path)
        else:
            self.status_label.configure(text="Ошибка: Папка не найдена!", text_color="red")

    def change_path(self):
        new_path = filedialog.askdirectory(initialdir=self.mods_path, title="Выберите папку mods")
        if new_path:
            self.mods_path = new_path
            self.path_label.configure(text=f"Путь: ...{self.mods_path[-40:]}")
            self.save_config()

    def start_update_thread(self):
        self.btn_update.configure(state="disabled")
        threading.Thread(target=self.check_and_update, daemon=True).start()

    def check_and_update(self):
        try:
            self.status_label.configure(text="🔍 Проверка версии на сервере...", text_color="white")
            list_url = f"https://docs.google.com/uc?export=download&id={LIST_FILE_ID}"
            data = requests.get(list_url).json()
            remote_version = data.get("version")

            if remote_version != self.current_version:
                self.status_label.configure(text=f"📦 Найдено обновление: {remote_version}")
                self.progress.set(0.1)

                #Download
                self.status_label.configure(text="📥 Загрузка архива...")
                url = f'https://drive.google.com/uc?id={MODS_FILE_ID}'
                gdown.download(url, TEMP_ZIP, quiet=True)
                self.progress.set(0.6)

                #Install
                self.status_label.configure(text="Установка...")
                p = Path(self.mods_path)
                if not p.exists(): p.mkdir(parents=True)
                
                for item in os.listdir(p):
                    item_p = p / item
                    if os.path.isfile(item_p): os.unlink(item_p)
                    elif os.path.isdir(item_p): shutil.rmtree(item_p)

                with zipfile.ZipFile(TEMP_ZIP, 'r') as zip_ref:
                    zip_ref.extractall(p)
                
                os.remove(TEMP_ZIP)

                #Saving
                self.current_version = remote_version
                self.save_config()
                self.ver_label.configure(text=f"Версия модов: {self.current_version}")
                self.status_label.configure(text="✅ Успешно обновлено!", text_color="#4BB543")
                self.progress.set(1.0)
            else:
                self.status_label.configure(text="У вас последняя версия", text_color="#4BB543")
                self.progress.set(1.0)

        except Exception as e:
            self.status_label.configure(text=f"💀 Ошибка: {str(e)[:35]}", text_color="#FF9494")
        
        self.btn_update.configure(state="normal")

if __name__ == "__main__":
    app = App()
    app.mainloop()