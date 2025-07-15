import os
import sys
import time
import threading
import datetime
import json
import pystray
from pystray import MenuItem as item
from PIL import Image
import pygame
import psutil
import re

LOG_FILE = os.path.expandvars(r"%userprofile%/AppData/Local/Warframe/EE.log")
SAVE_LOG = "ayatan_log.txt"
CONFIG_FILE = "config.json"
SOUND_FILE = "uspeh.wav"
ICON_PATH = "icon.png"

detections = []
volume = 1.0
watching = True
sound = None
pygame_initialized = False

def load_config():
    global volume
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                volume = float(data.get("volume", 1.0))
        except Exception:
            volume = 1.0

def save_config():
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({"volume": volume}, f)
    except Exception:
        pass

def init_audio():
    global sound, pygame_initialized
    try:
        if not pygame_initialized:
            pygame.mixer.init()
            pygame_initialized = True
        if os.path.exists(SOUND_FILE):
            sound = pygame.mixer.Sound(SOUND_FILE)
            sound.set_volume(volume)
    except Exception as e:
        print(f"Ошибка инициализации аудио: {e}")

def play_sound():
    if sound and pygame_initialized:
        try:
            sound.set_volume(volume)
            sound.play()
        except Exception:
            pass

def is_warframe_running():
    """Проверяет, запущен ли процесс Warframe.x64.exe"""
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == 'warframe.x64.exe':
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False

def watch_log():
    global detections, watching
    last_position = 0
    warframe_running = False
    last_check = 0
    pattern = re.compile(r'resource loa.*?treasures/oro', re.IGNORECASE)
    
    while watching:
        try:
            now = time.time()
            # Проверяем процесс раз в 20 секунд
            if now - last_check > 20:
                warframe_running = is_warframe_running()
                last_check = now
            if not warframe_running:
                time.sleep(5)
                continue
            if not os.path.exists(LOG_FILE):
                time.sleep(5)
                continue
                
            with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                # Читаем весь файл с начала, если это первая проверка
                if last_position == 0:
                    f.seek(0)
                else:
                    # Проверяем, не изменился ли размер файла
                    current_size = os.path.getsize(LOG_FILE)
                    if current_size < last_position:
                        # Файл был перезаписан, начинаем с начала
                        f.seek(0)
                        last_position = 0
                    else:
                        f.seek(last_position)
                
                # Читаем все новые строки
                new_lines = []
                while True:
                    line = f.readline()
                    if not line:
                        break
                    new_lines.append(line.strip())
                
                # Обрабатываем новые строки
                for line in new_lines:
                    if pattern.search(line):
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        entry = f"{timestamp} - {line}"
                        detections.append(entry)
                        
                        try:
                            with open(SAVE_LOG, "a", encoding="utf-8") as logf:
                                logf.write(entry + "\n")
                        except Exception:
                            pass
                        
                        play_sound()
                
                last_position = f.tell()
                
        except Exception as e:
            print(f"Ошибка отслеживания лога: {e}")
            time.sleep(0.5)
        
        time.sleep(0.5)

def set_volume_0():
    global volume
    volume = 0.0
    if sound:
        sound.set_volume(volume)
    save_config()

def set_volume_25():
    global volume
    volume = 0.25
    if sound:
        sound.set_volume(volume)
    save_config()

def set_volume_50():
    global volume
    volume = 0.5
    if sound:
        sound.set_volume(volume)
    save_config()

def set_volume_75():
    global volume
    volume = 0.75
    if sound:
        sound.set_volume(volume)
    save_config()

def set_volume_100():
    global volume
    volume = 1.0
    if sound:
        sound.set_volume(volume)
    save_config()

def show_stats():
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        stats = f"Найдено Ayatan: {len(detections)}\n"
        if detections:
            stats += f"Последнее: {detections[-1]}\n"
        stats += f"Громкость: {int(volume * 100)}%\n"
        stats += f"Файл лога: {LOG_FILE}\n"
        stats += f"Сохранено в: {SAVE_LOG}"
        
        # Создаем модальное окно
        root = tk.Tk()
        root.title("Статистика AyatanFrame")
        root.geometry("400x200")
        root.resizable(False, False)
        
        # Центрируем окно
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (400 // 2)
        y = (root.winfo_screenheight() // 2) - (200 // 2)
        root.geometry(f"400x200+{x}+{y}")
        
        # Делаем окно модальным
        root.transient()
        root.grab_set()
        
        # Создаем содержимое
        text_widget = tk.Text(root, wrap=tk.WORD, height=8, width=50)
        text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, stats)
        text_widget.config(state=tk.DISABLED)  # Только для чтения
        
        # Кнопка OK
        ok_button = tk.Button(root, text="OK", command=root.destroy, width=10)
        ok_button.pack(pady=(0, 10))
        
        # Обработчик закрытия окна
        root.protocol("WM_DELETE_WINDOW", root.destroy)
        
        # Фокус на кнопку
        ok_button.focus_set()
        
        # Запускаем окно
        root.mainloop()
        
    except Exception as e:
        print(f"Ошибка показа статистики: {e}")

def open_log_file():
    try:
        if os.path.exists(SAVE_LOG):
            os.startfile(SAVE_LOG)
        else:
            import tkinter as tk
            from tkinter import messagebox
            
            # Создаем модальное окно
            root = tk.Tk()
            root.title("Информация")
            root.geometry("300x100")
            root.resizable(False, False)
            
            # Центрируем окно
            root.update_idletasks()
            x = (root.winfo_screenwidth() // 2) - (300 // 2)
            y = (root.winfo_screenheight() // 2) - (100 // 2)
            root.geometry(f"300x100+{x}+{y}")
            
            # Делаем окно модальным
            root.transient()
            root.grab_set()
            
            # Сообщение
            label = tk.Label(root, text="Файл лога еще не создан", pady=20)
            label.pack()
            
            # Кнопка OK
            ok_button = tk.Button(root, text="OK", command=root.destroy, width=10)
            ok_button.pack(pady=(0, 10))
            
            # Обработчик закрытия окна
            root.protocol("WM_DELETE_WINDOW", root.destroy)
            
            # Фокус на кнопку
            ok_button.focus_set()
            
            # Запускаем окно
            root.mainloop()
            
    except Exception as e:
        print(f"Ошибка открытия файла: {e}")

def test_sound():
    play_sound()

def on_quit(icon_param, item=None):
    global watching
    watching = False
    save_config()
    
    try:
        if pygame_initialized:
            pygame.mixer.quit()
    except Exception:
        pass
    
    try:
        if icon_param:
            icon_param.visible = False
            icon_param.stop()
    except Exception:
        pass
    
    os._exit(0)

def setup(icon_param):
    try:
        if os.path.exists(ICON_PATH):
            icon_param.icon = Image.open(ICON_PATH)
        else:
            # Создаем простую иконку если файл не найден
            icon_param.icon = Image.new('RGB', (64, 64), color=0xFF0000)
        
        icon_param.title = "AyatanFrame - Отслеживание логов"
        
        # Создаем меню с подменю для громкости
        volume_menu = pystray.Menu(
            item("0%", set_volume_0),
            item("25%", set_volume_25),
            item("50%", set_volume_50),
            item("75%", set_volume_75),
            item("100%", set_volume_100)
        )
        
        icon_param.menu = pystray.Menu(
            item("Статистика", show_stats),
            item("Открыть лог", open_log_file),
            item("Тест звука", test_sound),
            pystray.MenuItem("Громкость", volume_menu),
            pystray.Menu.SEPARATOR,
            item("Выход", on_quit)
        )
        
        icon_param.visible = True
        
    except Exception as e:
        print(f"Ошибка настройки трея: {e}")

def main():
    try:
        print("Запуск AyatanFrame...")
        load_config()
        init_audio()
        
        # Запускаем отслеживание логов
        log_thread = threading.Thread(target=watch_log, daemon=True)
        log_thread.start()
        
        print("Отслеживание логов запущено")
        print("Иконка в трее должна появиться")
        
        # Создаем иконку в трее
        icon = pystray.Icon("AyatanFrame")
        icon.run(setup)
        
    except KeyboardInterrupt:
        print("Получен сигнал прерывания")
        on_quit(None)
    except Exception as e:
        print(f"Ошибка запуска: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
