import numpy as np
import sounddevice as sd
import time
import win32gui
import win32con
import win32api
import random
import ctypes
import msvcrt
import sys
import threading

sample_rate = 44100
intensity = 0.0
user32 = ctypes.windll.user32

def spawn_msgbox():
    messages = ["Where am I?", "Who are you?", "Something is wrong...", "Stop it.", "I can feel them.", "system_corrupted.exe", "YOU ARE NEXT", "I'm dead??", "I'm dead!!!"]
    button_styles = [0x0, 0x1, 0x2, 0x3, 0x4, 0x5]
    icons = [0x10, 0x20, 0x30, 0x40]
    msg = random.choice(messages)
    style = random.choice(button_styles) | random.choice(icons) | 0x40000
    user32.MessageBoxW(0, msg, "FATAL ERROR", style)

def show_warnings():
    MB_YESNO = 0x04
    MB_ICONWARNING = 0x30
    MB_ICONERROR = 0x10
    IDYES = 6
    if user32.MessageBoxW(0, "WARNING: System Impact\nAre you running this inside a VIRTUAL MACHINE?", "WARNING", MB_YESNO | MB_ICONWARNING) != IDYES:
        sys.exit()
    if user32.MessageBoxW(0, "FINAL CONFIRMATION\nDo you want to proceed at your own risk?", "FINAL CONFIRMATION", MB_YESNO | MB_ICONERROR) != IDYES:
        sys.exit()

def rename_windows(hwnd, lParam):
    if win32gui.IsWindowVisible(hwnd):
        win32gui.SetWindowText(hwnd, "I'm dead?")

def audio_callback(outdata, frames, time_info, status):
    global intensity
    t = (np.arange(frames) + audio_callback.t) / sample_rate
    audio_callback.t += frames
    bass = np.sin(2 * np.pi * 40 * t)
    jackpot = np.sin(2 * np.pi * (800 + 500 * np.sin(5 * t)) * t)
    noise = np.random.uniform(-1, 1, frames)
    intensity += 0.01 
    if intensity > 3.0: intensity = 3.0
    sound = (bass * (1 + intensity * 10) + 0.5 * jackpot + 0.3 * noise)
    sound = np.tanh(sound * (2 + intensity * 15)) 
    sound = np.clip(sound, -1, 1)
    outdata[:] = sound.reshape(-1, 1)

audio_callback.t = 0

if __name__ == "__main__":
    show_warnings()
    hdc = win32gui.GetDC(0)
    sw = win32api.GetSystemMetrics(0)
    sh = win32api.GetSystemMetrics(1)

    start_time = time.time()

    try:
        with sd.OutputStream(callback=audio_callback, samplerate=sample_rate, channels=1):
            while True:
                win32gui.BitBlt(hdc, random.randint(-20, 20), random.randint(-20, 20), sw, sh, hdc, 0, 0, win32con.SRCCOPY)
                win32gui.EnumWindows(rename_windows, None)

                if time.time() - start_time > 1.0:
                    if random.random() < 0.15:
                        threading.Thread(target=spawn_msgbox, daemon=True).start()

                if intensity > 0.5:
                    if random.random() > 0.85:
                        win32gui.BitBlt(hdc, random.randint(0, sw), 0, random.randint(50, 200), sh, hdc, random.randint(0, sw), 0, win32con.SRCCOPY)
                    
                if intensity > 1.0:
                    if random.random() > 0.94:
                        win32gui.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, 0, win32con.NOTSRCCOPY)
                    win32gui.BitBlt(hdc, random.randint(-10, 10), 2, sw, sh, hdc, 0, 0, win32con.SRCCOPY)

                if intensity > 2.0:
                    win32gui.StretchBlt(hdc, random.randint(0, 30), random.randint(0, 30), sw - 60, sh - 60, hdc, 0, 0, sw, sh, win32con.SRCCOPY)
                    if random.random() > 0.7:
                        win32gui.PatBlt(hdc, random.randint(0, sw), random.randint(0, sh), random.randint(100, 400), random.randint(100, 400), win32con.DSTINVERT)

                if msvcrt.kbhit():
                    if msvcrt.getch().lower() == b'q':
                        break
                time.sleep(0.01)
    except:
        pass
    finally:
        win32gui.InvalidateRect(0, None, True)
        win32gui.ReleaseDC(0, hdc)
