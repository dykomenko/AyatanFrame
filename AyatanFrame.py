import os
import time
import ctypes
import winsound
import sys

# Скрытие консоли
def hide_console():
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# Определяем путь к ресурсу внутри .exe
def resource_path(relative_path):
    try:
        # Временный путь от PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Пути
log_path = os.path.expandvars(r"%userprofile%\AppData\Local\Warframe\EE.log")
sound_path = resource_path("uspeh.wav")

# Звук
def play_sound():
    if os.path.exists(sound_path):
        try:
            winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            print("Ошибка звука:", e)
            winsound.Beep(1000, 300)
    else:
        print("Файл звука не найден.")
        winsound.Beep(800, 300)

# Чтение нового из лога
def watch_log():
    try:
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            f.seek(0, os.SEEK_END)
            while True:
                pos = f.tell()
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    f.seek(pos)
                    continue

                if "Resource load completed" in line and "FusionTreasure" in line:
                    print("✅ Найдено:", line.strip())
                    play_sound()
    except Exception as e:
        print("Ошибка чтения:", e)
        time.sleep(5)
        watch_log()

if __name__ == "__main__":
    hide_console()  # Включи, если хочешь без окна
    watch_log()
