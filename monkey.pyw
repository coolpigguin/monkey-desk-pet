import calendar, copy, datetime, json, math, os, random, shutil
import struct, sys, threading, time, traceback, wave
import tkinter as tk
import tkinter.font as tkfont

try:
    import ctypes
    from ctypes import wintypes
except Exception:
    ctypes = None
    wintypes = None

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

KEY = '#010101'
TICK_MS = 100
SLEEP_AFTER = 180
HOME_DIR = os.path.expanduser('~')
SETTINGS = os.path.join(HOME_DIR, '.monkeypet.json')
BELL_WAV = os.path.join(HOME_DIR, '.monkeypet_bell.wav')
LOG = os.path.join(HOME_DIR, '.monkeypet.log')
LOG_LIMIT = 200_000
LOG_REPEAT_GAP = 60
MUTEX_NAME = 'Local\\MonkeyPetSingleInstance'
SIZES = [('小', 3), ('中', 4), ('大', 5), ('特大', 6), ('巨大', 8)]
SIZE_VALUES = {v for _, v in SIZES}
WEEK = ['一', '二', '三', '四', '五', '六', '日']
LABEL_MAX = 40
MAX_CATCHUP_MIN = 12 * 60

C_BG = '#1d1927'; C_CARD = '#272233'; C_CARD2 = '#322b42'; C_LINE = '#3d3550'
C_TEXT = '#f3ecdd'; C_MUTED = '#a297b4'; C_GOLD = '#f3c98b'; C_PINK = '#f7a8b8'
C_RED = '#e0796f'; C_OFF = '#4a4160'; C_GOLD_HI = '#ffdca8'; C_SHAKE = '#4a202c'
C_TIMER = '#fff3e6'

BW, BH = 64, 66
PX, PY = 2, 34
PET = 32
SHOW = ('drop', 'peel', 'eat', 'toss')
CLICKABLE = ('idle', 'happy', 'think')
CLICK_GAP_MS = 350
DRAG_THRESHOLD = 4

CHEW = 11
BITE_OPEN = 3
FALL = 9
THINK_PAUSE = (18, 26)
DOTS_FROM = 6
DUR = {'happy': 8, 'think': 34, 'wake': 34, 'shock': 10, 'calm': 10,
       'drop': 12, 'peel': 12, 'eat': CHEW * 3, 'toss': 22, 'chime': 40}
BLINK_CHANCE = 0.02
BLINK_TICKS = 2
ALARM_BEEP_EVERY = 30
ALARM_BEEP_FOR = 600
ALARM_TIMEOUT = 3000
CHIME_TOAST_MS = 10000
DELETE_CONFIRM_MS = 3000
PEEL_START = (PX + 6, PY + 20, 2.2, -3.2)
PEEL_FLOOR = PY + 26
PEEL_GRAVITY = 0.55

DEFAULT_CFG = {'hat': True, 'size': 5, 'home': None, 'alarms': [],
               'hourly': {'on': False, 'from': 9, 'to': 22}}

SPRITES = {
    'idle1': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAB2klEQVR42u1Wr0/DQBh91zRzVAyBWQKCLBM1/AcVKNJMoAghwSFRzdIgEAjSLFNINCFTE2SZQvSPqCDLxAQaMUlIhtiuvV7vrndbu4SEz2x3u91736/3HfBvhnZ25C7Zzz8PTkzBAcD3HIzjBQBgMk9IrQQosO85wt+3JULKwGXAIiKbkCAq8OEoSNcvT8+4ur3JrasgYekeZMFFa1GtbEyA937v5Bruaa+UFE2XCQmtCBzuHxjldTgKtEnYOoeS935t2mKVhV9lokI00ZNCF1Dw+14EAHjoh7k/f799AAAa3Y4UXKULPPhknhBhCnhgao1up1QLykSJVVGjNqxqjrDeF4pwMk/IxflgORwFeLyM0v2717A09+N4kcl1vALjI8F7L+yCjESoVXj0Qlay28c/62/uUpQOdo/ohkyVU9amn1/59cxOAemdLAGpDuhUMW1XVTuuopFFwvccIM7WlmkR+Z5T8JpKMu89S0IW0cq6QDacKpuGOibTD9XI3pkOyF5VOyVQewqkndBq5jTDeByzFSy6RCfvsta2dcCphA4iP90PwrFQJdutZq4dpzNbOaC2VkKVGOk8UpUR4D3mq5iGVjYfdF7IRhFgCVDvROdMnubEtAg3AVHZL+Jr/Oy+21YDAAAAAElFTkSuQmCC',
    'idle2': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAABv0lEQVR42mNgGAVDDXgp6PxHpoe85YykWs7AwMDg48DHsOXAJwYGBgaGbQ+uMNLUATCLfRz4sMpT6hBGQpbjshibQ8hxBCM+y1esK4Hzl0yaxRCTl4bCp4YjmIhViGw5Nj62tEK2A9B9z2sYz6DjUkbQUbDoIsURRIWAvLA4SfG6Yl0J0Y5gIUbRlT1dVC9PYGmFhVDw4wPYEiKphRkTNsvryjoY6so6MDT/2nSD4demGwQtjwjqwZsbkLM21iho6qrAqpHNT4NgWYCvUEJPF9seXGFkYqAzQC7GMUJg24MrjBFBPf9XrCthaItCREHVsgqCcb/lwCdE0B6A+BRfNOBMhAhHVBCV8GC+QY5XNZU/UBZhh7Dgcl1EUM9/YoMUGdx68g6rQ3A5goVQEOFLRLDsSk52JLkuQK6W0X0NK5KRfY8M1FT+4CwZqZYLcFVOhGpMqmZDXOUHrvRCdQfQNA1QAtRkhFCyLMm1IXICwmYIMfGOK2cxEWM5LO56OnzgGFchBfMtuu9xlQOMxPiaUOMDX/FMVkkIA8g+LanYgpGKYRbgKp6JaaCSFALIDoDlZ2zqSGkZM5KaCMmxBB8AAGQN7YtBinRqAAAAAElFTkSuQmCC',
    'blink': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAB0klEQVR42u1Wr2/CQBT+jjTICjQCsRAEf0TFFGkQUwuZnpwiBDUxQRqCmpyeQCGWBoXgj6hYCAIxPYFclnRiu3K9vbu+K4VkyZ6hR6/3fe/X9w74N0frtbqp+vvnwYUrOACEgY94vQcALHeJOCkBCRwGPvn+WCKiCNwETBEpQ0LYwOeLYbZ+fnzCzd1tbl0FiRp3owpOralaKU1A955LSqbLhURhBLqXI/LZZvPFkE3CK9qQrKYZcLKaVq4tHif8JmCqEDltrRaqoMDvRxEA4GE6zn388fIKAKj3O0Zwmy7oaVnuEkGmQAeWVu93CrWgSJRUFXVqw6rmiOr9LwLLXSKur2YAgMkgwmQQsXMfr/cIAx9h4KPX6qZUF+jek0X4QyKdL8YscHmgKtnti0/ZuCmVDmMRllE0fVZs3t7z662XAcozVQJGHeBUsWxXWzt+R+MQiTDwgfVhXXMtIplnSpJ171USpohW1gWm4VTZNOSYST9sI/tsOmC6VZ2VwMlTYOyEZiOnGU7jWG8/6hBO3k2t7XHApYTOojD7fziOSZVsNxu5dtxsPeuAOloJbWLEuaRaI6B7rFexDK1pPnBuyE4RUAlI76h9Lldz4VqEZUBs9gWGKQD1aVGm6AAAAABJRU5ErkJggg==',
    'sleep1': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAABvElEQVR42u1Xr0/DQBR+tzTICTQCQRZE/4gJFGkQUwtBI1FN0yAmEKRpqpBoQqYmlmZqon9ExUIQE2hE5UJSBLxyvb7r/VgrSPaSZb11u+9773vv6w3gEIcwjMtTt+Tf/z04MwUHAPDGQ0izAgAAVtuc9UoAgb3xkLy/LxGmApcBU0RsSLA28PnCr9YvT89wc3dbW3dBYqD7RR6cWlO9Yk1AzF6XFMplQkJZAfciIK/bYr7wpSTEzx3VZvk6roDzddypj6y2OXN0yi8DphpRFbyHNCRA8FkQwSyIGj/eLTewW26U4NNJ0pgGsfR4n5TgIQ7JjY+uzpVe0GZKYvZGY2ijtSx4gkzWA4/XPxLcv4Za2qdZUbNrqhp887U6YZsPiOAIxIO/fXz+Xb87FSBaO++YjqxE00lS6nY1Hzw4AMDo7AsA3FLWF46OTjJtsUpYFRG8l/MAZpxmBYgyUaPLS0El18sU6MrVOQGZf3TyOO4iRBPSehiJzUdtogrUn2rsgQ44apdEXvWSecTo5Lg+hr9r2RgyWzsVR9H2mNYqAZ+pH6aNLkY5ZMA6p2WjClBeb2Jk1kZEkdn3DwnGN4Jk+BiVYifCAAAAAElFTkSuQmCC',
    'sleep2': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAABwElEQVR42u1Xr2/CQBh9R5rJCjRigjQT/BEVU6SZqGrI9OQUaaoQE6QhVZPTEygEISgEf0QFIQjE9ASSLOnUNcfx3Y/SIkj4EkKvR+69+773vjuAe9zj1qL/2CvE75sHZ1XBASDwXSzWBwDAcp+zqxLgwIHvkvN1iTATuAqYInIJCaYDn86G5fj78wuv728n4yZItGx/KIJTY0orFxOQd29LipdLR0KeM2ag9xyTz7qYzoYkCdHG/NkxLZavJiVwvprU9r1oYZIAlX4VMCVE29RzsbYo8FGcYhSnZ4sc5xsc5xsjeBRmpBvk3StL8DFJyIUfXp6MvcCmKYnzLVwhKAEu9zmTd39GYLnPWRRmAIDxIMV4kFrXfrE+IPDd8iMqXS6D+N6hmEZhVkxniRU435XYsrc/v/C6pXkLXUkcVY2iMCtkb/PsUM1HBBfD6/5pSbA6deV25VmRwU+I7ZxmRMhrLLdk1dmgy1bjLlDZt5HTsImgbOhUrT+1iCm8ThvbHX1XcGzAeQvN0qB8P0wWajBBjF6nrb2osCqqVx29dW5J2gzIO5ZVzMuhArY5FyplQCRg0oLt3ZBd2oTq/h/g8Q8SuPfF3bJ2sQAAAABJRU5ErkJggg==',
    'shock': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAB5UlEQVR42tVWv0/CQBh91zTGiUEGFhMgMcQB/BuYgTgwMTg7OjEwOxnTydHZgTgwGOhM/BfoYAgJNXFx0MHRkMDi1etxv1tIuKRpob1773v3vu8+4NBGq1Jfs/eDBye24ADQaRYwnv4AAMI4IjslQIE7zYLwfVYiRAcuAxYRcSFBVODDUR8A0OsGAAD6GwCeHh5zIeHpPuh1A0yWM0yWs4QIAFzdXGu94kyARk/By8USysWSlgTdLhsS3i7SdTjqG5PwdQu1qw28f30CANrVRsoHeQxfZT6WBG9CmREzZQEPzo/fl7fk+Tl+daoLrUp9zb7zVe5nVTCtBTpw9h7GEfFk4BfHq+SiZI4uz5PLdfCFLaVAGEek1w207pUVoWTx6X+EsvpA321tQRhHRJVCPDiVnY2sdrb6e0rvN3uIKT0QxhEBR4L1hErS+cc3RyRNgldGakKRkXhlqDlV6ZgiMd1W1nMxER81Lcls9Kr5bCDGBHSlVXY4URVk83M9C27vB9ZzdnIY2TQueyUg6q72roAzgSzd73zhC4uQth8QZYBokSxNq28CTtkHd53k//5gLCzTtdOTVD2YL3ylgsQ1702qoUmXrFSAj5h3Md0O2QFl4hsrBVgCNDrRdzaGJbYmzCMr2LEBfIAWF2GnzzkAAAAASUVORK5CYII=',
    'happy': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAB10lEQVR42sVXLU8DQRCdvWwaFL/hBCEVG34DoqppKqoq0EjU5dIgUeRyqrKakKoK0lRVNPyGE6SpqEAjkITkMEy7nc7eftxBx9ztfey8mZ19b1ZAoHVjVXLPF9tC+MwjQxyjk+ksOXg3HOTegUQhzk3Rh5gISXnv+hwAAOarz1rpdwKAjtEpNR1E4wC6sSpNjjkgjQLoxqrUi+xpPIGbu9uDcRMgnItQd86NbdvTCwCNXnVSUJ3UCgqXyweENQOqk0KxzKBYZiwIzqazxBmEFUCxzNj7pkza0q/b18vb7r7Vb7OFWIsJq5xTq3I+HOTG3UCXxksLWv32fjB+NZKSzTleF9tCRPDPRolNUi4fDvLy6uyb/fn+eVRJQrvJV/sITanHd5LV81gdgTA5p4IEAHB5gf/upRujp99LY1NBELtq/fr9gwA5BEEzYyxCrpB0cbLpAgtidUxOQUVo0gU9+qoi1OvBGQBGbxIh03PMgomaozqRU3vIRn/bEzZhtGeITklCJ8lAMIBflgxyst5IloScxUivYAThqpq2flG4bj9uQgoCCUnng/VGViqk8Dn7USA6iNAuuXIJ8sfe7j4ZzZ2bE1tf0EgGMDruO5+zgfAtwjrHMM5+AH1ODeyieImRAAAAAElFTkSuQmCC',
    'hat_idle1': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAApklEQVR42u3TMQrCQBSE4X9hj2CRSuxsrMRKhPR7DpE9hedYxHOkF8QqWNmks0yRO8QiCBIxronp5qsfO/MerCGSmy1qgN024XAsAcjuN8NAJjY8hBSAa16wXM0B8P40uISN2foZ3hZCivfUQ65h+wS3SzTX6Ffkbfi8bsI/qVzCJCs7H91c4kvY9tbTfffWVV58nXE/XMO8ho/hHz9FRERERERkVA/juzdjYcSFUQAAAABJRU5ErkJggg==',
    'hat_idle2': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAApklEQVR42mNgIBF4Kej8Z6AiYCHV4rQUCQaGOQz/GRgYGLY9uMJIqQMYibV8xgx7BgYGBoZzZ24yGJmoMzAwMDBkZByk2BEsxPgaZjk6mDHDniEjg7LQYCHHYnRHQEKDPIdgKD5ihT+RvfGSYBDZ9gKvoTbHiHcEC7qv5erw+/rNmZsE1XiREBqMtMhayIAaOWUUjIJRMApGwSgYBaNgFIyCUTC8AQB22zh4ClIX/QAAAABJRU5ErkJggg==',
    'hat_blink': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAApklEQVR42u3TMQrCQBSE4X9hj2CRSuxsrMRKhPR7DpE9hedYxHOkF8QqWNmks0yRO8QiCBIxronp5qsfO/MerCGSmy1qgN024XAsAcjuN8NAJjY8hBSAa16wXM0B8P40uISN2foZ3hZCivfUQ65h+wS3SzTX6Ffkbfi8bsI/qVzCJCs7H91c4kvY9tbTfffWVV58nXE/XMO8ho/hHz9FRERERERkVA/juzdjYcSFUQAAAABJRU5ErkJggg==',
    'hat_sleep1': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAApklEQVR42mNgGGrAS0HnPzXNYyHV4rQUCQaGOQz/GRgYGLY9uMJIqQMYibV8xgx7BgYGBoZzZ24yGJmoMzAwMDBkZByk2BEsxPgaZjk6mDHDniEjg7LQYCHHYnRHQEKDPIdgKD5ihT+RvfGSYBDZ9gKvoTbHiHcEC7qv5erw+/rNmZsE1XiREBqMtMhayIAaOWUUjIJRMApGwSgYBaNgFIyCUUBTAAABQDh4CfIkjgAAAABJRU5ErkJggg==',
    'hat_sleep2': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAApklEQVR42mNgGAUkAi8Fnf/UNI+FVIvTUiQYGOYw/GdgYGDY9uAKI6UOYCTW8hkz7BkYGBgYzp25yWBkos7AwMDAkJFxkGJHsBDja5jl6GDGDHuGjAzKQoOFHIvRHQEJDfIcgqH4iBX+RPbGS4JBZNsLvIbaHCPeESzovparw+/rN2duElTjRUJoMNIiayEDauSUUTAKRsEoGAWjYBSMglEwCoY3AACLljh4XcoGPQAAAABJRU5ErkJggg==',
    'hat_shock': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAmUlEQVR42mNkIAJ4Kej8nzHDnoGBgYHh3JmbDEYm6gwMDAwMGRkHGbY9uMLIQAFgIWQxAwMDA8xydDBjhj1DRgbDfwYGBrIdwkKOxeiOgIQGeQ7BUHzECmI5LvDGS4JBZNsLvIbaHCPeESzovparw+/rN2duElTjRUJoMCJbTgtAaSIdBaNgFIyCUTAKRsEoGAWjYBSMguEPAMg3MGLu00FGAAAAAElFTkSuQmCC',
    'hat_happy': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAmUlEQVR42mNkIAJ4Kej8nzHDnoGBgYHh3JmbDEYm6gwMDAwMGRkHGbY9uMLIQAFgIWQxAwMDA8xydDBjhj1DRgbDfwYGBrIdwkKOxeiOgIQGeQ7BUHzECmI5LvDGS4JBZNsLvIbaHCPeESzovparw+/rN2duElTjRUJoMCJbTgtAaSIdBaNgFIyCUTAKRsEoGAWjYBSMguEPAMg3MGLu00FGAAAAAElFTkSuQmCC',
    'bell0': 'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAvUlEQVR42mNgoDFgJEWxl4LOfxh724MrROllorUPaG4ByQA5mIgBLKQavKJBhiGigeE/sfHASKzhKxpkMMQjGp4QtISJWMN5zfww5FY0yBAMMqIimdfMj+HzqU3UT0W4goYUXzBR4vpL5x7QNh/oGSnQPqMR8gXFFugZKeCNByZCEUwo9dDcBzSPA0IRzUhpYYYNIBcfWAu7Kr8/ZBvetomFcGmKroguVSa2oCOmuCbJqchBR6wvWSgJ30EBAEr+R29fM5PtAAAAAElFTkSuQmCC',
    'bell1': 'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAx0lEQVR42mNgoDFgJEWxl4LOfxh724MrROllorUPaG4ByQA5mIgBLKQavKJBhiGigeE/sfHASKzhKxpkMMQjGp4QtISkOOA180Phr2iQYfi0wOM/vmBjIsXwz6c2UT8V4QoedJ/g8gUTpa6/dO4BbfOBnpEC7TMaPl8QnUy3bssiKpLRky7RkUzIcFy+GDqFHa7IZqRWoYYNbHtwhRFvYVfl94dsw9s2sRBORdTwBSM5mrBZjKtUZSHXZcjBBwsOqlqAz1C6AgCk2U5rcAh5wwAAAABJRU5ErkJggg==',
    'bell2': 'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAxElEQVR42mNgoDFgJEWxl4LOfxh724MrROllorUPaG4ByQA5mIgBLKQavKJBhiGigeE/sfHASKzhKxpkMMQjGp4QtISJkMGfFnj837oti3aRzGvmx/D51CbqW4ArWJDBigYZgpHORK7rL517QNt8oGekQPuMRowvmHCF/9ZtWQQjlxhfMOGKXEKG0zwOaF7YERvJjOQWYtgAtmIDpbCr8vtDtuFtm1hw+4BWridYmmKzmNiqkuj6ADnYcAUDRRaQYyhdAQAVsk0whKzHqwAAAABJRU5ErkJggg==',
    'zz': 'iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAYAAADED76LAAAAJklEQVR42mNgIAAYGRgYGLwUdP5jk9z24AojVl24NNBIkjxHIgMAPYQOVyewD5UAAAAASUVORK5CYII=',
    'hold_open': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAB40lEQVR42u1Xv0vDQBT+rgRx6uDs4CDFIfg3dOgkwaFTEWdHpxKKg6OUkqmjs4g4dJDQqUPo35BBSocOzg4dpVAHfenl+i6Xu6aD4IPQvORy3/d+3ivwL5ZyceKv5d8/Dy5swQEgaNYRJ0sAwHiRir0SIOCgWWff70pEmMB1wBwRFxKiCPxl1M30p+Ejrm9vcnoVJGplF8rgnM7lijMB1Xq/FcJvhUZSFC4bEkYP+K0Q6WSAdDJgSXDyMuqWJmEkkE4G7H1VUjO5X5avt/fs0iWiTT/ZqoIicCJA8rqYWvcFFXy8SIXHbdJpR7l4khxcnm0WDadOTUnuomwIOu0I54er7JLJVHGOyNYDgKc+5LL34aoPALh77hU2oaxrJj97qJ5Qrd8iUCQ6cNpQbtmN0xUV8ZoLh/xM7NrN1LNi9vGZ1+deBkj7ygRYD+iSSD6cTOdC3hsbTwTNOpBsdM8miQg8TpaIk2jLE6r1KgnunWebzblk+9WpVO/D/v4nIh04iY7EbO6xIa651jUHbpuw1gTKTkeVDyRqWdpa3zg+yvUM5yTkNrD5jitvYVN+Ji9QP5DLkZJP11tEWbdzOSCTcB1SC0MQ9YPsvtuLtet050OZCdnZA2Qdt85mNBcuVVDFXzKSb1kXIpTvtiJzAAAAAElFTkSuQmCC',
    'hold_chew1': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAB3UlEQVR42u1XLW8CQRB921wIClFdgWgIgvAbEFXNBVFVUV1ZRQipqKgiBIWsbhoUormcQtyPONEQxInqCmRDQkU7x94ye/vRQzTpGG5gb9+b2Zm3A/BvjnbZ7Ozkzz8PLlzBASDsNRAlGwBAnKXiqAQIOOw12N9/S0SYwHXAHBEfEqIMfL4Y5P7z7Ak3d7cFvwoSJ7YLZXDO52rFm4AavS0pOi4XEsYMdC6G7HOZzRcDaxKBaUG6nOTA6XJSubYENunXAXOFaNPWcqEKDvxhOAYAPE5GhZc/X98AALV+WwtepgvqscRZKtgjUIHJav22UQtMoiSrqFMbVnWPyNEf1ECcpeL6arrr1rf5d/cvI6uzj5LNXq6TbzA1E2r0bBHGWSrQ7Oy69a0VOG0oS3brnAIoFpwavVGKbVKr3hWr94+ivw5yQNpTJqDVAV0VE6DpXihmY5+JsNcAkr0fuBQRgUfJBlEyPciEGr1KwksJS4vtxyfhIv046kSkAyfTkVitA/Z4vXWAA3ctWGcCttNR5QOJ2pKu0bfOTgua4V2E3AYu73GtLVzaz5QF0gO5Han4dBeUkxKqRGQSvkNq6RFMx2H+PBhF2nW6+8FmQvbOAEXHrXMZzYVPF1Txl4zsC6cAGfefkQl4AAAAAElFTkSuQmCC',
    'hold_chew2': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAB10lEQVR42u1XIW/CQBR+1zQLCjE9gVjIBOE3IKYWMoGqmJ6cahoygZhqSBVyellQCNJUIfojThAyUTE9UUlImNlrj+Nd7650S0j2DD249Pvee9/77gD4j3OLu05vL36ePTizBQcAGA7aEKc5AAAkGWe/SgCBh4M2+fupRJgOXAVMEalDglWBzxd+sX6bvcLD0+PBugkSjulGEZxaU1qpTUDO3pQUtsuGhLYCvduAfK6K+cI3JuHqNvDVtADmq2kjXiLqxDUpvwqYEqKNkSUZZw4FPglCmATh0Qu2yzVsl2stuDeKlNMgjzXZgpfpmHzxxf2N1gtUpiRrAvc48IchWjhZgSTjzBtF+35rV3z3/D426n2c5mV507LHFJFKESYZZ9Dp7futnRE4ZiT2tnuNCZREkowzJGZsxaZlFWPz+XW0Z/PhQpJxhmeLaNlKH1AJCQF154JpuDYzjOBxmkOcRkeVoLIvW0JX1LVlfCC2nzUaF+UduhPTaQq8yj9UejnJB2TwuuHYGkmd6F5dHoystQbkkbTNvsqiHVP14/yiDrxRRJoUZitnr3JFKyOSWyBWQmXPuhtzZQuicFg8++NYuU9lzyYX1NoVwHmm9tncjFkdETbxjwjjG93hFeh/pugAAAAAAElFTkSuQmCC',
    'hold_look': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAB4klEQVR42u1Xr0/DQBR+R5plhgkQGBImyDLRLOE/mECRZgKFIMEhUcuyIBCoZZlCogmZmiBNFaJ/RAVZJirQiEmypAh42/X6rnfv6AQJz2y39e773q/vXgH+jWlnTT+TP/88uOCCAwAE3QaE8RIAAKI0EVslgMBBt0H+/1siwgSuA6aIuJAQZeDTWX+9fnp4hMub69y6ChI7tg/K4NSaqhVnAqr3uydX4J8OjKQwXRwSVhE42j9g5XU661uT8GweSl7HW9OWHVP4y4wqRI6eFLoAwe8GIwAAuB8Pc5s/X94AAKDWa2vBy3RBBY/SRJApUIHRar22UQtMoiSrKKsNq7pHZO8LRRilibg4n2Sd+iq3+fZ5aMx9GC83ch1/g6mRUL0nuyBKEwFNP+vUVwVgChwPlCW7dYwO+BmVDvk3YRuyspzKNn//yK8X3hoQz5QJaHVAV8UIaLoX8tHYRCLoNgDizdrjFBGCh/ESwnhSiITqvUrCWQm1xfazRuFC/djqRKQDR9ORmC88Mr3OOkCBcwuWTcB2Oqp8IFFbkut963AvpxnORUgdwNlHtbbgtJ8pCqgHcjti8ekuKJYSqkRkEq5DamkKJqNg/b0/DK0HE867gnME0DvqOc5oLly6oIpXMrQv5x4ScGVayOYAAAAASUVORK5CYII=',
    'hands': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAX0lEQVR42mNgGAWjYBSMglEwCkbBKBgFo2CkA0ZiFHkp6PyHsbc9uMJIFwcgW7piXQlcPCKoh6qOYMJl+Yp1JSgW0wowDXQaYCGkYMW6EoaIoB6GAU0DtLB4FIwCGAAAhIUZoBPBbjAAAAAASUVORK5CYII=',
    'hands1': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAX0lEQVR42mNgGAWjYBSMglEwCkbBKBgFo2AUDDBgJEaRl4LOfxh724MrjHRxALKlK9aVwMUjgnqo6ggmXJavWFeCYjGtANNApwEWQgpWrCthiAjqYRjQNEALi0fBoAEAmqMZoGl7g1gAAAAASUVORK5CYII=',
    'think1': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAACXElEQVR42tVXMWjbQBR95x6hk7t3ymBMBpOlQ7bioUMpIoOGIkrmjJlEMB1C06GIoMmjt4IppoOHIkyHDqJbh1IwGorrQV0KKRSCu5hgcIfwxel057uTG0o/CCzd1733/3/3vwz87/Zkt7P+5+DbkGB/O+pJnjntyesAe92m3im98bElwlzANwJLlqQLKxLcBfzo5Lj0fNgfFL/lNWAApJ21icSduuAAsH/wANNPn7Vry8sM66t7L75d/TyvlQE57WenUWn95UXPuOZ1mxszwUwqF6PvPDoFAHz/dQkA+P3ldfGObm3YHyBJF9pT0lCBj8YhjGp3MNpnNA4rR5jrwFWWfbioRG6zJtpoHCLw46IkVqdg2B/g6e5DAMDO4Z7R//rdVwDA2/yj0bdhm8adw70KOAlPFqDKd2sCKiOli6fB1RpyHw/8uKiVqF6VBX5cXKauSNoK/Lh0ErhqmAR+bD3dvMf3kbz/YfQjkvIxZLadUG63r55FmC452q0VZnOO/bsrPH/Tq7Rp00wwamCSZ0xVChEMAKZLbjWQ5D5gJUIiIQ4fSulsfgPcbq2KZ9T9dOAiCadxLN63WyulHxGS6636iJnkGWvYgnvdJuiqQ1okI+7BcQtWIilMwkmeMWcNUPRJukCSLnB0cozROCylWky/TYZEfTDbNFLNZ3Neaiq2RtFTME4EZMGJJDYNMDFasZ+IBG5FA5vKKAuS2W6gKoGp7ZIgVcBWBKj+ceQh7CWVDwsdcBx5xTN6T9eOjaeANosjr7hs/HX3zgTkyOX7bf1ZnY5m+m+o64Aq+wNuXmWDMDPGewAAAABJRU5ErkJggg==',
    'think2': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAACVElEQVR42tVXP4jTUBj/vV44nO52pxtKuaHc4uB23OAgEm7IIEGcHZ3KURzEc5BwZOrYTShSHDpICA4Owc1BhCOD1A7RQThBOOJySKEO8oWXl/f6vtco4geFpu9Lfr/v3+9Lgf/d7uz1V/8cvA0J8aejTovc6ZneJsD+0Y7ZKfvtwyUiXMDXAiuWZCWLhOcCfv/hg9rvk9G4+q6eAWMg669sJLY2BQeAg5s3cP7uvfHs6iLH6nL3yafLb6cbZUBN++OTqHb+9GxoPfOPdtZmQti6XI6+f+sEAPD5+wUA4MeH59U9prPJaIwkK41T0tGBT2cDWLvdweg509mgMcKeCVxn+ZuzRuScM9mmswHCIK5KwpqCyWiMu3uHAIDt432r/89XHwEAL4u3Vt8ON43bx/sNcGo8tQF1vq0J6Iw6XZ4GV+uoOh4GcVUruXvbWJKVoN4Kg7g2CZ5umYRBzNpuRJYIc3zVMRRcJVTl9tm9COdXHvzb15G8/oqDa0s8ejFsyLRtJ1h7IC1yoSsFgc0XX2rXtoWk6gCrCYmEvHzWlYPUzwQuk3Bax7KyqVnpdZeYLzzjy4nuJSYtciG44LIsJ1mJXnep9eWQoADSIhce/oLVdoi0CdMiF849QNEnWYkkK7W7fxNdIFKCW3tK+Xzh0UJplEFNv1oKORinZSQD9bpLhEFckVA3nUkHTO+UrXrApn66MqqNyZ4CtQRciTYBswhQ/ePIx2CYWKMn4Djyq9/oPpMcW6eAHhZHfvXh+JuunQmokavXbf2FqwzrxEQ3btz/ir8ARxRoYIEjhxgAAAAASUVORK5CYII=',
    'think3': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAACXklEQVR42tVXMYgTQRR9kxsOG2NhIdh4RQhXHAdiYScpRZYrtpBFDuyuvGqRcIWohSzHVinTCUGCRQpZgoXFcp2FCGELiSm2ErQ6ck04ArE4/jI7O5OZ2XiIHxayO3/nvf//m/83wP9uT3b2Vv8cfBMS7G9HPc4zpz15HWCv09Q7pVc+tkSYC/haYMmSdG5FgruAHx4flZ4Pev3it7wG9IF0b2UisVUXHAD2Hz7A5MtX7driV4bV+a1XP85/v66VATntL19EpfU3p13jmtdprs0EM6lcjP7m/ecAgHu37wAAss+nxTu6tUGvjySda09JQwU+HIUwqt3BaJ/hKKwcYa4DV9nFt3eVyG3WRBuOQgR+XJTE6hQMen083XkEANg+2DX6X378DgD4kJ8ZfRu2adw+2K2Ak/BkAap8NyagMlK6eBpcrSH38cCPi1qJ6lVZ4MfFZeqKpK3Aj0sngauGSeDH1tPNe3wXyaefRj8iKR9DZtsJ5Xb79lmEyYKj3VpiOuPYv7HEyftupU2bZoJRA+M8Y6pSiGAAMFlwq4Ek9wErERIJcfhQSqezK+B2a1k8o+6nAxdJOI1j8b7dWir9iJBcb9VHzDjPWMMW3Os0QVcd0iIZcQ+Oa7ASSWESjvOMOWuAok/SOZJ0jsPjIwxHYSnVYvptMiTqg9mmkWo+nfFSU7E1ip6CcSIgC04ksW6AidGK/UQkcC0aWFdGWZDMdgNVCUxtlwSpArYiQPWPIw9hN6l8WOiA48grntF7unZsPAW0WRx5xWXjr7t3JiBHLt9v6s/qdDTTf0NdB1TZH3zyX4MofPduAAAAAElFTkSuQmCC',
    'hat_think1': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAsUlEQVR42mNkIBF4Kej8Z2BgYJgxw56BgYGB4dyZmwxGJuoMDAwMDBkZBxkYGBgYtj24wkiseSzEKtzQ4vJ/1pwXcIuxAZhcRgbD/7QUCYaAmj0EHcJELcvRHTJrzguGDS0u/yl2AHqQEwtg6mH6cQGcQXTECqLxjZcEg8i2FzgNIEXe5hhm2mAkJZFhA6TIY0ukjNgspwcgJaeMglEwCkbBKBgFo2AUjIJRMApGAU0BALhISMqvvhs4AAAAAElFTkSuQmCC',
    'hat_think2': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAsUlEQVR42mNkIBF4Kej8Z2BgYJgxw56BgYGB4dyZmwxGJuoMDAwMDBkZBxkYGBgYtj24wkiseSzEKtzQ4vJ/1pwXcIuxAZhcRgbD/7QUCYaAmj0EHcJELcvRHTJrzguGDS0u/yl2AHqQEwtg6mH6cQGcQXTECqLxjZcEg8i2FzgNIEXe5hhm2mAkJZFhA6TIY0ukjNgspwcgJaeMglEwCkbBKBgFo2AUjIJRMApGAU0BALhISMqvvhs4AAAAAElFTkSuQmCC',
    'hat_think3': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAsUlEQVR42mNkIBF4Kej8Z2BgYJgxw56BgYGB4dyZmwxGJuoMDAwMDBkZBxkYGBgYtj24wkiseSzEKtzQ4vJ/1pwXcIuxAZhcRgbD/7QUCYaAmj0EHcJELcvRHTJrzguGDS0u/yl2AHqQEwtg6mH6cQGcQXTECqLxjZcEg8i2FzgNIEXe5hhm2mAkJZFhA6TIY0ukjNgspwcgJaeMglEwCkbBKBgFo2AUjIJRMApGAU0BALhISMqvvhs4AAAAAElFTkSuQmCC',
    'sthink1': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAACFUlEQVR42u1Wr2/CQBh9bZpJBHJBIAiZ6B+BmFhIM4Eiy/TkFGnIBGJiaUjV5NySZUEhCEFN8B/MIEiDYAtmYojOLSRMsCsf1+tdrwWxZGfa3o++d+/e930H/DfNVi/ba/r88+CGLjgAOLUChuMQADCaT4yDEmDATq0gHM9LxFCBJwGLiGQhYcjAe/1W9P10/4DL66ud732QMFUTOq6HjushWCzRcb2on5JJ8kpmBeju7VMXAPD2+QEA+Hp93JnLK6HrCfMQ4drrt1IrYakmTF66wp3vq5kq88mayIg6+STmATpYraxw221rg8s8wIOP5hMjpoBzdgwAQvDvwRTfg6k0F6gMyOeVmAeC2XuiNY7OT3LXEbp7aRTcXXha8g/HIZxaAU6tgHrZXouigNYQZRTcPLdTgbMfUmmrldXvm70WHQftSyTQbPhRTLP3NGcaLJYckQ2J0XxiYBxXxYx7wIoWVysrNBs+oh8IEk5SSqYk+FJOv03Rgq2E2x/IyjIjQXcvI5ErFVOzNRt+dDwqJVIXo3rZXlMFgpkF2Z2AmZBlT1oxRUerNOFmUF1IeOA0LXUYUob07PjFOuCZqyEfPuw4eDLSSCgVEcxC4RoriwmzrhGFspIAu5gOxyF8z4n6W+2hMEtWS8WdcGTmSypQRtriIbv95LmkShXgd8yHI5M2z71QSwFKgO1ONE/nap5qYl4QWfsBuIMzKhK995cAAAAASUVORK5CYII=',
    'sthink2': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAACGElEQVR42u1WIW/CQBT+ShokArkgEIQg+iMQEwtpECiyTE9OEUImEBNLQ6om55YsCwpBCGqi/2AGQRoEWzATQzBHSJhgV67X17seBbFkz0Dba7/vffe9ew/4D82oFa0t//vnwQ1dcACwqzmMvBUAYDyfGCclwIDtao58npaIoQKPA6aIHELCkIH3B63g+vnhEVc316HrY5DIqBZ02w66bQf+Yolu2wnu82TivHKwAnz21nkbAPD+9QkA+H57Cq0VldD1ROYU5doftBIrYaoWTF57ZObHiozKfLKgjKhznkQ8wMCZ2e56HW1wmQdE8PF8YkQUaDZc+DOTBF8Pp1gPp9KzQGVA8VyJELAvzmIBsvUKsvVKqj7CZ08S8GcfAID7S0dL/pG3gl3Nwa7mUCtaW6oK+B6irILbl04icPZBXtpyafP7z9pS28HfU5Zhs+FKn4t76i+WApEdifF8YsCLqmKqgHm2oqysXGXlyJMICHv7a8IDZvBiubSJDCFUd2R9gc9eJBF3Mmaoxfs9jL7Mm63ZcAOl4pqTVjOqFa0tD86rohpI2HbwHZNSVmrC3YMwiThwEThJJCpDRkKWrWjCNEFWQaR2vfBASpGRRbmQhz9bke+Yuox1gJP0CDPJGc72znXs4H6rMyJPyXIhHypHZr64BmUkbR6y6SfNkCpVQMxYrAYmbZq5UEsBngDLjlqnM5onWpgWRBY/UQ4+49eWLOUAAAAASUVORK5CYII=',
    'sthink3': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAACF0lEQVR42u1Wv2vCQBh9CaFbHexQKEIdRDpk6X/gWCR0cJJS6Naxk4h0cOhQgjh17FYoxclBglOH/AddHCQ4SHF2sJsIdrAXPy+Xu1xih0JvSXI/8t69e9/3HfDfNFu1aK/p88+DG7rgAOBUcvD8BQBgOB0Zv0qAATuVnHA8KxFDBR4HLCKShoQhA+/1G+H369Mzru9ud773QcJUTWg3XbSbLoLZHO2mG/ZTMnFeSa0A3f3h+Q0A4PToGAAweu/szOWV0PWE+Rvh2us3EithqSZ8fbwId76vZqrMJ2siI+rkk4gH6GC5tMJDp6UNLvMADz6cjoyIAs7FCQAIwZeDMZaDsTQXqAzI55WIB4LJZ6w1Di7PMtcRuntpFDxeuVrye/4CTiUHp5JDtWivRVFAa4gyCu7fWonA2Q+ptOXS6ufNXouOg/bFEqjXumFMs/ckZxrM5hyRDYnhdGTAj6piRj1ghYvLpRXqtS7CHwgSTlxKpiT4Uk6/TdGCrYTbH8jKMiNBdy8jkSkVU7PVa93weFRKJC5G1aK9pgoEEwuyOwEzIcuetGKKjlZpws2gupDwwEla4jCkDOnZ8Yt1wFNXQz582HHwZKSRUMgjmCyEa6w0Jky7RhTKSgLsYur5C3RdJ+xvtDxhliwX8jvhyMwXV6CMpMVDdvvJckmVKsDvmA9HJm2We6GWApQA251ons7VPNHErCCy9g1xzTAqnZ05oAAAAABJRU5ErkJggg==',
    'hat_sthink1': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAApklEQVR42u3TMQrCQBSE4X9hj2CRSuxsrMRKhPR7DpE9hedYxHOkF8QqWNmks0yRO8QiCBIxronp5qsfO/MerCGSmy1qgN024XAsAcjuN8NAJjY8hBSAa16wXM0B8P40uISN2foZ3hZCivfUQ65h+wS3SzTX6Ffkbfi8bsI/qVzCJCs7H91c4kvY9tbTfffWVV58nXE/XMO8ho/hHz9FRERERERkVA/juzdjYcSFUQAAAABJRU5ErkJggg==',
    'hat_sthink2': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAApklEQVR42u3TMQrCQBSE4X9hj2CRSuxsrMRKhPR7DpE9hedYxHOkF8QqWNmks0yRO8QiCBIxronp5qsfO/MerCGSmy1qgN024XAsAcjuN8NAJjY8hBSAa16wXM0B8P40uISN2foZ3hZCivfUQ65h+wS3SzTX6Ffkbfi8bsI/qVzCJCs7H91c4kvY9tbTfffWVV58nXE/XMO8ho/hHz9FRERERERkVA/juzdjYcSFUQAAAABJRU5ErkJggg==',
    'hat_sthink3': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAApklEQVR42u3TMQrCQBSE4X9hj2CRSuxsrMRKhPR7DpE9hedYxHOkF8QqWNmks0yRO8QiCBIxronp5qsfO/MerCGSmy1qgN024XAsAcjuN8NAJjY8hBSAa16wXM0B8P40uISN2foZ3hZCivfUQ65h+wS3SzTX6Ffkbfi8bsI/qVzCJCs7H91c4kvY9tbTfffWVV58nXE/XMO8ho/hHz9FRERERERkVA/juzdjYcSFUQAAAABJRU5ErkJggg==',
    'dots1': 'iVBORw0KGgoAAAANSUhEUgAAABAAAAAGCAYAAADKfB7nAAAAL0lEQVR42mNgGGjAyMDAwOCloPMfJrDtwRVGUgxggjFWntlIlgvgBoSb+A9MGAAA0gEHBplV5yoAAAAASUVORK5CYII=',
    'dots2': 'iVBORw0KGgoAAAANSUhEUgAAABAAAAAGCAYAAADKfB7nAAAANElEQVR42mNgGGjAyMDAwOCloPMfJrDtwRWcYtgAE4yx8sxGDElsYjgNCDfxx5DEJkZ1AAAS/Q4GL1J/RgAAAABJRU5ErkJggg==',
    'dots3': 'iVBORw0KGgoAAAANSUhEUgAAABAAAAAGCAYAAADKfB7nAAAAM0lEQVR42mNgGGjAyMDAwOCloPMfJrDtwRWSxJhgAivPbMQwnRgxuAHhJv4YiokVowgAAMfbFQYTMBB9AAAAAElFTkSuQmCC',
    'hat_hold_open': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAApklEQVR42u3TMQrCQBSE4X9hj2CRSuxsrMRKhPR7DpE9hedYxHOkF8QqWNmks0yRO8QiCBIxronp5qsfO/MerCGSmy1qgN024XAsAcjuN8NAJjY8hBSAa16wXM0B8P40uISN2foZ3hZCivfUQ65h+wS3SzTX6Ffkbfi8bsI/qVzCJCs7H91c4kvY9tbTfffWVV58nXE/XMO8ho/hHz9FRERERERkVA/juzdjYcSFUQAAAABJRU5ErkJggg==',
    'hat_hold_chew1': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAApklEQVR42u3TMQrCQBSE4X9hj2CRSuxsrMRKhPR7DpE9hedYxHOkF8QqWNmks0yRO8QiCBIxronp5qsfO/MerCGSmy1qgN024XAsAcjuN8NAJjY8hBSAa16wXM0B8P40uISN2foZ3hZCivfUQ65h+wS3SzTX6Ffkbfi8bsI/qVzCJCs7H91c4kvY9tbTfffWVV58nXE/XMO8ho/hHz9FRERERERkVA/juzdjYcSFUQAAAABJRU5ErkJggg==',
    'hat_hold_look': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAApklEQVR42u3TMQrCQBSE4X9hj2CRSuxsrMRKhPR7DpE9hedYxHOkF8QqWNmks0yRO8QiCBIxronp5qsfO/MerCGSmy1qgN024XAsAcjuN8NAJjY8hBSAa16wXM0B8P40uISN2foZ3hZCivfUQ65h+wS3SzTX6Ffkbfi8bsI/qVzCJCs7H91c4kvY9tbTfffWVV58nXE/XMO8ho/hHz9FRERERERkVA/juzdjYcSFUQAAAABJRU5ErkJggg==',
    'hat_hold_chew2': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAApklEQVR42mNgIBF4Kej8Z6AiYCHV4rQUCQaGOQz/GRgYGLY9uMJIqQMYibV8xgx7BgYGBoZzZ24yGJmoMzAwMDBkZByk2BEsxPgaZjk6mDHDniEjg7LQYCHHYnRHQEKDPIdgKD5ihT+RvfGSYBDZ9gKvoTbHiHcEC7qv5erw+/rNmZsE1XiREBqMtMhayIAaOWUUjIJRMApGwSgYBaNgFIyCUTC8AQB22zh4ClIX/QAAAABJRU5ErkJggg==',
    'banana0': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAA0ElEQVR42mNgGAWjYBSMglHAwMCQF6DxPy9A4/9A2M2EzPFS0PnvpaBDV4ewMDAwMNy5wMLAwMDAsGadDAMDAwNDSBDD/20PrjDSNQRglnNKuQxMOvBS0Pn/7ZzH/2/nPP7/f9FDt6hgwiWxZp0MAz0cgdUB35/toVtUMOGTpEcowB2w7cEVxpCgJ3QPBSZCCmgdCkwMAwxQHIAeDQOeCOmRDjAcgC0UaJkOBlcawBYK35/toX1tiA/AHEKr2pGRUEMFxp604QbjyEkDo4CeAABsWkxv/A8iqgAAAABJRU5ErkJggg==',
    'banana0b': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAzklEQVR42mNgGAWjYBSMglEwGEBegMb/vACN/wNhNxMyx0tB57+Xgg5dHcLCwMDAcOcCCwMDAwPDmnUyDAwMDAwhQQz/tz24wkjXEIBZzinlMjDpwEtB5/+3cx7/v53z+P//RQ/dooIJl8SadTIM9HAEVgd8f7aHblHBhE+SHqEAd8C2B1cYQ4Ke0D0UmAgpoHUoMDEMMEBxAHo0DHgipEc6wHAAtlCgZToYXGkAWyh8f7aH9rUhPgBzCK1qR0ZCDRUYe9KGG4wjJw2MKAAA5qNMbxd33GwAAAAASUVORK5CYII=',
    'banana1': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAA80lEQVR42mNgGAWjYBSMglEwwIARXcBLQec/Mn/bgyuMdHOAl4LO/w1n+lAUBJgU0dQhTIQUoDuI5g548eASXdMA00AnwlEHjDqABV0gI2TBwLjES0Hn/7dzHv9h9P8XPf+/nfOAi6GXkFSNAi8Fnf9r1skwMDAwMKxZJ8MQEvQEriAk6AlDU8UfhqaKPwy0cAQTsuUwC9esk2H4/mwPA6eUC8OadTIMdR2QmKKFI1ASYUjQE4ZtD64wIocAXWpDmK9gFQ5yqHBKuTB8f7YHHi3UrpSYsFW79AwFRny5QsXgD5w/acMN+lbHtG6IDJqScBQAAAA5ZItaOazNAAAAAElFTkSuQmCC',
    'banana1b': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAA80lEQVR42mNgGAWjYBSMglEw0gEjuoCXgs5/ZP62B1cY6eYALwWd/xvO9KEoCDApoqlDmAgpQHcQzR3w4sEluqYBpoFOhKMOGHUAC7pARsiCgXGJl4LO/2/nPP7D6P8vev5/O+cBF0MvIakaBV4KOv/XrJNhYGBgYFizToYhJOgJXEFI0BOGpoo/DE0Vfxho4QgmZMthFq5ZJ8Pw/dkeBk4pF4Y162QY6jogMUULR6AkwpCgJwzbHlxhRA4ButSGMF/BKhzkUOGUcmH4/mwPPFqoXSkxYat26RkKjPhyhYrBHzh/0oYb9K2Oad0QGTQl4YADAFOyZIvBcIlHAAAAAElFTkSuQmCC',
    'banana2': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAA9UlEQVR42mNgGAWjYBSMglEwCkY6YEQX8FLQ+Y/M3/bgCiPdXOOloPP/0Zme/7/e7EKh0R1FTcCELiChoIeVppsDXjy4RNc0wDTQiXDAHcCCLpARsmBgXOKloPP/2zmP/zD6/4ue/9/OecDFaJUTmGCWr1knw8DAwMCwZp0MQ0jQE7iCkKAnDE0VfxiaKv4w0MIRTMiWwyxcs06G4fuzPQycUi4Ma9bJMNR1QGKKFo5ASYQhQU8Ytj24wogcAnQpimG+ghW7yKHCKeXC8P3ZHni0ULtoZsJW5tMzFBjx5QoVgz9w/qQNNxjpWhDRqxYc8JJwFAAAIwtwv+7FnkYAAAAASUVORK5CYII=',
    'banana2b': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAA90lEQVR42mNgGAWjYBSMglEwCkbBAANGdAEvBZ3/yPxtD64w0s01Xgo6/x+d6fn/680uFBrdUdQETOgCEgp6WGm6OeDFg0t0TQNMA50IB9wBLOgCGSELBsYlXgo6/7+d8/gPo/+/6Pn/7ZwHXIxWOYEJZvmadTIMDAwMDGvWyTCEBD2BKwgJesLQVPGHoaniDwMtHMGEbDnMwjXrZBi+P9vDwCnlwrBmnQxDXQckpmjhCJREGBL0hGHbgyuMyCFAl6IY5itYsYscKpxSLgzfn+2BRwu1i2YmbGU+PUOBEV+uUDH4A+dP2nCDka4FEb1qwQEvCQccAABP9nC/njlIhQAAAABJRU5ErkJggg==',
    'banana3': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAA6klEQVR42mNgGAWjYBSMglEwCkbBKBhgwIgu4KWg8x+Zv+3BFUa6ucZLQef/ozM9/3+92YVCozuKmoAJl4SEgh4KTSvAgk0wwKSI/onBS0Hn/7dzHv9h9P8XPf+/nfOAi9EqGphglq9ZJ8PAwMDAsGadDENI0BO4gpCgJwxNFX8Ymir+MNDCEUzIlsMsXLNOhuH7sz0MnFIuDGvWyTDUdUBiihaOQEmEIUFPGLY9uMKIHAJ0KQdgvoLleeRQ4ZRyYfj+bA88WqhdLjBhK3DoGQqM+HKFisEfOH/ShhuMdC2I6FUEM41WhwMNAEecbVORpSoOAAAAAElFTkSuQmCC',
    'banana3b': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAA6UlEQVR42mNgGAWjYBSMglEwCkbBKBjpgBFdwEtB5z8yf9uDK4x0c42Xgs7/R2d6/v96swuFRncUNQETLgkJBT0UmlaABZtggEkR/RODl4LO/2/nPP7D6P8vev5/O+cBF6NVNDDBLF+zToaBgYGBYc06GYaQoCdwBSFBTxiaKv4wNFX8YaCFI5iQLYdZuGadDMP3Z3sYOKVcGNask2Go64DEFC0cgZIIQ4KeMGx7cIUROQToUg7AfAXL88ihwinlwvD92R54tFC7XGDCVuDQMxQY8eUKFYM/cP6kDTcY6VoQ0asIZhrxtSEALhFtU/xsI0wAAAAASUVORK5CYII=',
    'banana4': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAzElEQVR42mNgGAWjYBSMglEwCkbBKBgFIx0wInO8FHT+41K47cEVRpq6xEtB5/+3cx7/YfT/Fz3/v53zgIvhcxwlgAlm+Zp1MgwMDAwMa9bJMIQEPYErCAl6wtBU8YehqeIPAy0cwYRsOczCNetkGL4/28PAKeXCsGadDENdBwsDAwMDTRzBhMwJCXrCsO3BFUbkEKBLIoT5CpbQkEOFU8qF4fuzPfBooXZiZMKWyukZCoz4coWKwR84f9KGG4w0ywUDku8JOWAU0AsAAJwmV3iyvCaLAAAAAElFTkSuQmCC',
    'banana4b': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAzElEQVR42mNgGAWjYBSMglEwCkbBKBgFo2CAASMyx0tB5z8uhdseXGGkqUu8FHT+fzvn8R9G/3/R8//bOQ+4GD7HUQKYYJavWSfDwMDAwLBmnQxDSNATuIKQoCcMTRV/GJoq/jDQwhFMyJbDLFyzTobh+7M9DJxSLgxr1skw1HWwMDAwMNDEEUzInJCgJwzbHlxhRA4BuiRCmK9gCQ05VDilXBi+P9sDjxZqJ0YmbKmcnqHAiC9XqBj8gfMnbbjBSLNcMCD5npADRgwAAIabV3g0jBbRAAAAAElFTkSuQmCC',
    'banana_whole': 'iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAAwklEQVR42mNgIBMwMjAwMOQFaPxnYGBguHOBhYGBgYFh24MrjIQ0siBz1qyTYWBgYGAICWL4T4xmBgYGBgYvBZ3/3855/P//ouf/t3Me/70UdP7jU88EY2x7cIUxJOgJw/dnexg4pVwIWsSETfD7sz0MW08kMOCzFUUjzFZkP+PSzITLRJiTYZrRDWDEFVCwEOaUcmH4/mwPNLSfwKMKq43ITkYOLGSn43QqLs14nYrubOTAqmh6QJxGdENUDP4wUAQAHPBWrIzkNTAAAAAASUVORK5CYII=',
    'peel': 'iVBORw0KGgoAAAANSUhEUgAAAA4AAAAKCAYAAACE2W/HAAAAaElEQVR42mNgGLTAS0HnP8kKvBR0/n875/EfWY4JXcGadTKETUfXCAPImmGGoYszott27dQDnLZomSkwhAQ9Ydj24AojCzZJfGDNOhmGkCCG/4zYAgTmNHQQEvQEzmYkJei3PbgCVw8AnYYtXNc802oAAAAASUVORK5CYII=',
    'sparkle': 'iVBORw0KGgoAAAANSUhEUgAAAAcAAAAHCAYAAADEUlfTAAAAJUlEQVR42mNgQAL/P6z6j8xnYiAb/P+w6j/MOGQa3QrCphDtIABlgBktFXJQCQAAAABJRU5ErkJggg==',
}

_log_seen = {}
_bell_ready = threading.Event()
_instance_lock = None


def log_error():
    try:
        tb = traceback.format_exc()
        lines = tb.strip().splitlines()
        sig = '\n'.join(lines[-3:])
        now = time.monotonic()
        last = _log_seen.get(sig)
        if last is not None and now - last < LOG_REPEAT_GAP:
            return
        _log_seen[sig] = now
        if os.path.exists(LOG) and os.path.getsize(LOG) > LOG_LIMIT:
            os.replace(LOG, LOG + '.old')
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(datetime.datetime.now().strftime('\n[%Y-%m-%d %H:%M:%S]\n'))
            f.write(tb)
    except Exception:
        pass


def acquire_single_instance():
    try:
        k32 = ctypes.WinDLL('kernel32', use_last_error=True)
        k32.CreateMutexW.restype = wintypes.HANDLE
        k32.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
        handle = k32.CreateMutexW(None, False, MUTEX_NAME)
        if ctypes.get_last_error() == 183:
            return None
        return handle or True
    except Exception:
        return True


try:
    class MONITORINFO(ctypes.Structure):
        _fields_ = [('cbSize', wintypes.DWORD), ('rcMonitor', wintypes.RECT),
                    ('rcWork', wintypes.RECT), ('dwFlags', wintypes.DWORD)]
except Exception:
    MONITORINFO = None


def primary_work_area(root):
    try:
        r = wintypes.RECT()
        if ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(r), 0):
            return r.left, r.top, r.right, r.bottom
    except Exception:
        pass
    return 0, 0, root.winfo_screenwidth(), root.winfo_screenheight() - 48


def monitor_work_area(root, x, y, nearest=True):
    try:
        u32 = ctypes.windll.user32
        u32.MonitorFromPoint.restype = ctypes.c_void_p
        u32.MonitorFromPoint.argtypes = [wintypes.POINT, wintypes.DWORD]
        u32.GetMonitorInfoW.argtypes = [ctypes.c_void_p, ctypes.POINTER(MONITORINFO)]
        handle = u32.MonitorFromPoint(wintypes.POINT(int(x), int(y)), 2 if nearest else 0)
        if not handle:
            return None
        info = MONITORINFO()
        info.cbSize = ctypes.sizeof(MONITORINFO)
        if u32.GetMonitorInfoW(handle, ctypes.byref(info)):
            r = info.rcWork
            return r.left, r.top, r.right, r.bottom
    except Exception:
        pass
    return primary_work_area(root)


def bell_ok(path):
    try:
        with wave.open(path, 'rb') as w:
            return w.getnframes() > 0
    except Exception:
        return False


def make_bell(path):
    rate, dur = 44100, 1.4
    frames = bytearray()
    for i in range(int(rate * dur)):
        t = i / rate
        v = 0.0
        for start, f0 in ((0.0, 1318.5), (0.32, 1046.5)):
            if t >= start:
                tt = t - start
                env = math.exp(-tt * 4.2) * min(1.0, tt * 400)
                v += env * (math.sin(2 * math.pi * f0 * tt) * 0.6
                            + math.sin(2 * math.pi * f0 * 2.76 * tt) * 0.25 * math.exp(-tt * 6)
                            + math.sin(2 * math.pi * f0 * 5.40 * tt) * 0.12 * math.exp(-tt * 9))
        frames += struct.pack('<h', int(max(-1, min(1, v * 0.55)) * 32767))
    tmp = path + '.tmp'
    with wave.open(tmp, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(frames))
    os.replace(tmp, path)


def prepare_bell():
    try:
        if not bell_ok(BELL_WAV):
            make_bell(BELL_WAV)
        if bell_ok(BELL_WAV):
            _bell_ready.set()
    except Exception:
        log_error()


def beep():
    try:
        import winsound
    except ImportError:
        return
    if _bell_ready.is_set():
        try:
            winsound.PlaySound(BELL_WAV, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
            return
        except Exception:
            pass
    try:
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    except Exception:
        pass


def parse_time(s):
    s = s.strip().replace('：', ':')
    if ':' in s:
        h, _, m = s.partition(':')
    elif s.isdigit() and len(s) in (3, 4):
        h, m = s[:-2], s[-2:]
    elif s.isdigit() and len(s) <= 2:
        h, m = s, '0'
    else:
        return None
    try:
        h, m = int(h), int(m)
    except ValueError:
        return None
    if 0 <= h <= 23 and 0 <= m <= 59:
        return f'{h:02d}:{m:02d}'
    return None


def valid_date(s):
    try:
        datetime.date.fromisoformat(s)
        return True
    except (TypeError, ValueError):
        return False


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def days_text(days):
    days = sorted(days)
    if len(days) == 7:
        return '每天'
    if days == [0, 1, 2, 3, 4]:
        return '平日'
    if days == [5, 6]:
        return '週末'
    if not days:
        return '只響一次'
    return '週' + '、'.join(WEEK[d] for d in days)


def when_text(a):
    dates = a.get('dates') or []
    if not dates:
        return days_text(a['days'])
    today = datetime.date.today().isoformat()
    fut = sorted(x for x in dates if x >= today)
    if not fut:
        return '日期都過了'

    def fmt(x):
        dd = datetime.date.fromisoformat(x)
        return f'{dd.month}/{dd.day}（{WEEK[dd.weekday()]}）'
    if len(fut) <= 3:
        return '、'.join(fmt(x) for x in fut)
    return '、'.join(fmt(x) for x in fut[:2]) + f' 等 {len(fut)} 天'


def hour_in_range(hour, start, end):
    if start <= end:
        return start <= hour <= end
    return hour >= start or hour <= end


def fmt_left(sec):
    return f'{sec // 60:02d}:{sec % 60:02d}'


def rounded(c, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return c.create_polygon(pts, smooth=True, **kw)


def clean_alarm(a):
    if not isinstance(a, dict):
        return None
    tm = parse_time(str(a.get('time', '')))
    if not tm:
        return None
    days = a.get('days') if isinstance(a.get('days'), list) else []
    days = sorted({d for d in days if is_int(d) and 0 <= d <= 6})
    dates = a.get('dates') if isinstance(a.get('dates'), list) else []
    dates = sorted({d for d in dates if isinstance(d, str) and valid_date(d)})
    label = a.get('label')
    label = label.strip()[:LABEL_MAX] if isinstance(label, str) else ''
    return {'time': tm, 'label': label, 'on': bool(a.get('on', True)), 'days': days, 'dates': dates}


def clean_config(data):
    cfg = copy.deepcopy(DEFAULT_CFG)
    if not isinstance(data, dict):
        return cfg
    if isinstance(data.get('hat'), bool):
        cfg['hat'] = data['hat']
    if is_int(data.get('size')) and data['size'] in SIZE_VALUES:
        cfg['size'] = data['size']
    home = data.get('home')
    if (isinstance(home, (list, tuple)) and len(home) == 2
            and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in home)):
        cfg['home'] = [int(home[0]), int(home[1])]
    alarms = data.get('alarms')
    if isinstance(alarms, list):
        cleaned = [x for x in (clean_alarm(a) for a in alarms) if x]
        cfg['alarms'] = sorted(cleaned, key=lambda x: x['time'])
    h = data.get('hourly')
    if isinstance(h, dict):
        cfg['hourly'] = {
            'on': bool(h.get('on', False)),
            'from': h['from'] if is_int(h.get('from')) and 0 <= h['from'] <= 23 else 9,
            'to': h['to'] if is_int(h.get('to')) and 0 <= h['to'] <= 23 else 22,
        }
    return cfg


def load_config():
    if not os.path.exists(SETTINGS):
        return copy.deepcopy(DEFAULT_CFG), None
    try:
        with open(SETTINGS, encoding='utf-8') as f:
            data = json.load(f)
        return clean_config(data), None
    except Exception:
        log_error()
    backup = SETTINGS + datetime.datetime.now().strftime('.%Y%m%d%H%M%S.bak')
    try:
        shutil.copy2(SETTINGS, backup)
        return copy.deepcopy(DEFAULT_CFG), f'設定檔讀不到，已備份成 {os.path.basename(backup)}'
    except Exception:
        log_error()
        return copy.deepcopy(DEFAULT_CFG), '設定檔讀不到，也無法備份'


def save_config(cfg):
    tmp = SETTINGS + '.tmp'
    try:
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=1)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, SETTINGS)
        return True
    except Exception:
        log_error()
        return False


class Scheduler:
    def __init__(self, now):
        self.last = now.replace(second=0, microsecond=0) - datetime.timedelta(minutes=1)

    @staticmethod
    def due(a, dt):
        if not a.get('on') or a['time'] != dt.strftime('%H:%M'):
            return False
        if a['dates']:
            return dt.strftime('%Y-%m-%d') in a['dates']
        if a['days']:
            return dt.weekday() in a['days']
        return True

    @staticmethod
    def retire(a, dt):
        today = dt.strftime('%Y-%m-%d')
        if a['dates']:
            if not any(d > today for d in a['dates']):
                a['on'] = False
                return True
        elif not a['days']:
            a['on'] = False
            return True
        return False

    def poll(self, alarms, now):
        now = now.replace(second=0, microsecond=0)
        if now == self.last:
            return None
        if now < self.last:
            self.last = now
            return [], False, False
        steps = int((now - self.last).total_seconds() // 60)
        first = max(1, steps - MAX_CATCHUP_MIN + 1)
        fired, changed = [], False
        for k in range(first, steps + 1):
            dt = self.last + datetime.timedelta(minutes=k)
            for a in alarms:
                if self.due(a, dt):
                    fired.append((dt, a))
                    changed = self.retire(a, dt) or changed
        self.last = now
        return fired, changed, True


class Panel:
    def __init__(self, pet):
        self.pet = pet
        self.win = None
        self.canvas = None
        self.editing = None
        self.draft = None
        self.timer_text = None
        self.confirm_del = None
        self.confirm_job = None

    @property
    def is_open(self):
        return self.win is not None

    def u(self, n):
        return self.pet.u(n)

    def font(self, size, weight='normal'):
        return self.pet.font(size, weight)

    def toggle(self):
        if self.win:
            self.close()
        else:
            self.open()

    def open(self):
        p = self.pet
        p.touch()
        if p.state == 'sleep':
            p.set_state('shock')
        w = tk.Toplevel(p.root)
        w.overrideredirect(True)
        w.attributes('-topmost', True)
        w.config(bg=KEY)
        try:
            w.wm_attributes('-transparentcolor', KEY)
        except tk.TclError:
            pass
        w.bind('<Escape>', lambda e: self.close())
        self.win = w
        self.canvas = tk.Canvas(w, bg=KEY, highlightthickness=0, bd=0)
        self.canvas.pack()
        self.build()

    def close(self):
        if self.win:
            try:
                self.win.destroy()
            except tk.TclError:
                pass
        self.win = None
        self.canvas = None
        self.editing = None
        self.draft = None
        self.timer_text = None
        self.confirm_del = None

    def refresh(self):
        if self.win:
            self.build()

    def place(self):
        if not self.win:
            return
        p = self.pet
        self.win.update_idletasks()
        W, H = self.win.winfo_reqwidth(), self.win.winfo_reqheight()
        l, t, r, b = p.pet_area()
        x = int(p.x + PX * p.S - W - self.u(8))
        if x < l + 8:
            x = int(p.x + (PX + PET + 2) * p.S + self.u(8))
        y = int(p.y + BH * p.S - H)
        self.win.geometry(f'+{max(l + 8, min(x, r - W - 8))}+{max(t + 8, min(y, b - H - 8))}')

    def tick(self):
        p = self.pet
        if self.win and p.deadline is not None and self.timer_text and p.frame % 5 == 0:
            try:
                self.timer_text.config(text=fmt_left(p.time_left()))
            except tk.TclError:
                pass

    def label(self, parent, text, size=10, color=C_TEXT, weight='normal', bg=C_BG, **kw):
        return tk.Label(parent, text=text, font=self.font(size, weight), fg=color, bg=bg, **kw)

    def button(self, parent, text, cmd, bg=C_CARD2, fg=C_TEXT, hover=C_LINE, size=10, padx=12, pady=6, weight='normal'):
        b = tk.Label(parent, text=text, font=self.font(size, weight), fg=fg, bg=bg,
                     padx=self.u(padx), pady=self.u(pady), cursor='hand2')
        b.bind('<Enter>', lambda e: b.config(bg=hover))
        b.bind('<Leave>', lambda e: b.config(bg=bg))
        b.bind('<Button-1>', lambda e: cmd())
        return b

    def switch(self, parent, on, cmd, bg=C_CARD):
        w, h = self.u(40), self.u(22)
        c = tk.Canvas(parent, width=w, height=h, bg=bg, highlightthickness=0, cursor='hand2')
        rounded(c, 1, 1, w - 1, h - 1, h // 2, fill=C_GOLD if on else C_OFF, outline='')
        k = h - self.u(6)
        x = w - k - self.u(3) if on else self.u(3)
        c.create_oval(x, self.u(3), x + k, self.u(3) + k, fill=C_BG if on else C_MUTED, outline='')
        c.bind('<Button-1>', lambda e: cmd())
        return c

    def card(self, parent, title, right=None):
        outer = tk.Frame(parent, bg=C_BG)
        outer.pack(fill='x', pady=(self.u(10), 0))
        head = tk.Frame(outer, bg=C_BG)
        head.pack(fill='x', pady=(0, self.u(5)))
        self.label(head, title, 9, C_MUTED, 'bold').pack(side='left')
        if right:
            right(head)
        body = tk.Frame(outer, bg=C_CARD, padx=self.u(12), pady=self.u(10))
        body.pack(fill='x')
        return body

    def build(self):
        p = self.pet
        for w in self.canvas.winfo_children():
            w.destroy()
        self.canvas.delete('all')
        pad = self.u(16)
        root = tk.Frame(self.canvas, bg=C_BG, padx=pad, pady=pad)

        head = tk.Frame(root, bg=C_BG)
        head.pack(fill='x')
        icon = tk.Canvas(head, width=p.icon.width(), height=p.icon.height(), bg=C_BG, highlightthickness=0)
        icon.create_image(0, 0, image=p.icon, anchor='nw')
        if p.cfg['hat']:
            icon.create_image(0, 0, image=p.icon_hat, anchor='nw')
        icon.pack(side='left')
        tt = tk.Frame(head, bg=C_BG)
        tt.pack(side='left', padx=self.u(10))
        self.label(tt, '小猴設定', 14, C_TEXT, 'bold').pack(anchor='w')
        self.label(tt, '右鍵點小猴可以開關這個面板', 8, C_MUTED).pack(anchor='w')
        self.button(head, '✕', self.close, bg=C_BG, fg=C_MUTED, hover=C_CARD,
                    size=11, padx=8, pady=2).pack(side='right', anchor='n')

        self.timer_card(root)
        self.alarm_card(root)
        if self.editing is None:
            self.hourly_card(root)
            self.look_card(root)
            self.footer(root)
        self.finish(root)

    def finish(self, root):
        root.update_idletasks()
        W, H = root.winfo_reqwidth(), root.winfo_reqheight()
        self.canvas.config(width=W, height=H)
        rounded(self.canvas, 0, 0, W, H, self.u(18), fill=C_BG, outline='')
        self.canvas.create_window(0, 0, window=root, anchor='nw', width=W, height=H)
        self.place()

    def timer_card(self, root):
        p = self.pet
        body = self.card(root, '計 時')
        row = tk.Frame(body, bg=C_CARD)
        row.pack(fill='x')
        if p.deadline is not None:
            self.label(row, p.timer_label, 10, C_MUTED, bg=C_CARD).pack(side='left')
            self.timer_text = self.label(row, fmt_left(p.time_left()), 20, C_GOLD, 'bold', bg=C_CARD)
            self.timer_text.pack(side='left', padx=self.u(10))
            self.button(row, '取消', p.cancel_timer, bg=C_CARD2, fg=C_RED,
                        size=9, padx=10, pady=4).pack(side='right')
            return
        self.timer_text = None
        self.button(row, '番茄鐘 25 分', lambda: p.start_timer(25 * 60, '番茄鐘'),
                    bg=C_GOLD, fg=C_BG, hover=C_GOLD_HI, weight='bold').pack(side='left')
        self.button(row, '休息 5 分', lambda: p.start_timer(5 * 60, '休息')).pack(side='left', padx=self.u(8))
        row2 = tk.Frame(body, bg=C_CARD)
        row2.pack(fill='x', pady=(self.u(8), 0))
        self.label(row2, '自訂', 10, C_MUTED, bg=C_CARD).pack(side='left')
        e = tk.Entry(row2, width=4, font=self.font(11), bg=C_CARD2, fg=C_TEXT, insertbackground=C_GOLD,
                     relief='flat', justify='center', highlightthickness=1,
                     highlightbackground=C_LINE, highlightcolor=C_GOLD)
        e.insert(0, '15')
        e.pack(side='left', padx=self.u(8), ipady=self.u(3))
        self.label(row2, '分鐘', 10, C_MUTED, bg=C_CARD).pack(side='left')

        def go_custom():
            try:
                n = int(e.get().strip())
            except ValueError:
                n = 0
            if 1 <= n <= 600:
                p.start_timer(n * 60, f'{n} 分鐘')
            else:
                e.config(highlightbackground=C_RED)
        e.bind('<Return>', lambda ev: go_custom())
        self.button(row2, '開始', go_custom, size=9, padx=10, pady=4).pack(side='left', padx=self.u(8))
        self.button(row2, '試響', lambda: p.start_timer(3, '測試'), bg=C_CARD, fg=C_MUTED,
                    hover=C_CARD2, size=9, padx=8, pady=4).pack(side='right')

    def alarm_card(self, root):
        p = self.pet
        editing = self.editing is not None

        def add(h):
            self.button(h, '＋ 新增', self.new_alarm, bg=C_BG, fg=C_GOLD, hover=C_CARD,
                        size=9, padx=6, pady=1).pack(side='right')
        body = self.card(root, '鬧 鐘', right=None if editing else add)
        alarms = p.cfg['alarms']
        if not alarms and not editing:
            self.label(body, '還沒有鬧鐘，按右上角「＋ 新增」', 9, C_MUTED, bg=C_CARD).pack(anchor='w')
        for i, a in enumerate(alarms):
            if self.editing == i:
                self.alarm_editor(body)
                continue
            row = tk.Frame(body, bg=C_CARD)
            row.pack(fill='x', pady=self.u(3))
            col = C_TEXT if a['on'] else C_MUTED
            t = self.label(row, a['time'], 17, C_GOLD if a['on'] else C_MUTED, 'bold', bg=C_CARD)
            t.pack(side='left')
            info = tk.Frame(row, bg=C_CARD)
            info.pack(side='left', padx=self.u(10))
            l1 = self.label(info, a['label'] or '鬧鐘', 10, col, bg=C_CARD)
            l1.pack(anchor='w')
            l2 = self.label(info, when_text(a), 8, C_MUTED, bg=C_CARD)
            l2.pack(anchor='w')
            if editing:
                continue
            for w in (t, info, l1, l2):
                w.config(cursor='hand2')
                w.bind('<Button-1>', lambda e, i=i: self.edit_alarm(i))
            confirm = self.confirm_del == i
            self.button(row, '刪除？' if confirm else '✕', lambda i=i: self.ask_delete(i),
                        bg=C_CARD2 if confirm else C_CARD, fg=C_RED if confirm else C_MUTED,
                        hover=C_CARD2, size=9, padx=6, pady=2).pack(side='right')
            self.switch(row, a['on'], lambda i=i: self.toggle_alarm(i)).pack(side='right', padx=self.u(6))
        if self.editing == len(alarms):
            self.alarm_editor(body)

    def hourly_card(self, root):
        p = self.pet
        h = p.cfg['hourly']
        body = self.card(root, '整 點 報 時')
        row = tk.Frame(body, bg=C_CARD)
        row.pack(fill='x')
        self.label(row, '每到整點，小猴搖鈴提醒', 10, C_TEXT if h['on'] else C_MUTED, bg=C_CARD).pack(side='left')
        self.switch(row, h['on'], self.toggle_hourly).pack(side='right')
        self.button(row, '試聽', lambda: p.ring(f'{datetime.datetime.now().hour} 點整（試聽）', ack=False),
                    bg=C_CARD, fg=C_MUTED, hover=C_CARD2, size=8, padx=6, pady=1).pack(side='right', padx=self.u(6))
        if not h['on']:
            return
        row = tk.Frame(body, bg=C_CARD)
        row.pack(fill='x', pady=(self.u(8), 0))
        self.label(row, '從', 10, C_MUTED, bg=C_CARD).pack(side='left')
        self.stepper(row, 'from').pack(side='left', padx=self.u(6))
        self.label(row, '點，到', 10, C_MUTED, bg=C_CARD).pack(side='left')
        self.stepper(row, 'to').pack(side='left', padx=self.u(6))
        tail = '點（跨夜）' if h['from'] > h['to'] else '點'
        self.label(row, tail, 10, C_MUTED, bg=C_CARD).pack(side='left')

    def look_card(self, root):
        p = self.pet
        body = self.card(root, '外 觀')
        row = tk.Frame(body, bg=C_CARD)
        row.pack(fill='x')
        self.label(row, '戴斗笠', 10, C_TEXT, bg=C_CARD).pack(side='left')
        self.switch(row, p.cfg['hat'], self.toggle_hat).pack(side='right')
        row = tk.Frame(body, bg=C_CARD)
        row.pack(fill='x', pady=(self.u(10), 0))
        self.label(row, '大小', 10, C_TEXT, bg=C_CARD).pack(side='left')
        seg = tk.Frame(row, bg=C_CARD2, padx=self.u(2), pady=self.u(2))
        seg.pack(side='right')
        for name, v in SIZES:
            on = p.cfg['size'] == v
            self.button(seg, name, lambda v=v: p.change_size(v), bg=C_GOLD if on else C_CARD2,
                        fg=C_BG if on else C_TEXT, hover=C_GOLD_HI if on else C_LINE,
                        size=9, padx=8, pady=3, weight='bold' if on else 'normal').pack(side='left')

    def footer(self, root):
        p = self.pet
        foot = tk.Frame(root, bg=C_BG)
        foot.pack(fill='x', pady=(self.u(14), 0))
        self.button(foot, '吃香蕉', p.start_run, size=9, padx=10, pady=5).pack(side='left')
        self.button(foot, '回到右下角', p.reset_home, size=9, padx=10, pady=5).pack(side='left', padx=self.u(8))
        self.button(foot, '讓小猴休息', p.quit, bg=C_BG, fg=C_RED, hover=C_CARD,
                    size=9, padx=8, pady=5).pack(side='right')

    def stepper(self, parent, key):
        p = self.pet
        f = tk.Frame(parent, bg=C_CARD2)

        def step(d):
            h = p.cfg['hourly']
            h[key] = (h[key] + d) % 24
            p.save()
            self.refresh()
        self.button(f, '−', lambda: step(-1), size=9, padx=6, pady=1).pack(side='left')
        self.label(f, f"{p.cfg['hourly'][key]:02d}", 10, C_GOLD, 'bold', bg=C_CARD2, width=3).pack(side='left')
        self.button(f, '＋', lambda: step(1), size=9, padx=6, pady=1).pack(side='left')
        return f

    def alarm_editor(self, body):
        p = self.pet
        d = self.draft
        box = tk.Frame(body, bg=C_CARD2, padx=self.u(10), pady=self.u(10))
        box.pack(fill='x', pady=self.u(4))

        row = tk.Frame(box, bg=C_CARD2)
        row.pack(fill='x')
        ent = dict(font=self.font(16, 'bold'), bg=C_BG, fg=C_GOLD, insertbackground=C_GOLD, relief='flat',
                   justify='center', highlightthickness=1, highlightbackground=C_LINE, highlightcolor=C_GOLD)
        te = tk.Entry(row, width=6, **ent)
        te.insert(0, d['time'])
        te.pack(side='left', ipady=self.u(2))
        ent.update(font=self.font(10), fg=C_TEXT, justify='left')
        le = tk.Entry(row, width=12, **ent)
        le.pack(side='left', padx=self.u(8), ipady=self.u(5), fill='x', expand=True)
        placeholder = '名稱（例如 上課）'
        if d['label']:
            le.insert(0, d['label'])
        else:
            le.insert(0, placeholder)
            le.config(fg=C_MUTED)

        def clear(e):
            if le.get() == placeholder:
                le.delete(0, 'end')
                le.config(fg=C_TEXT)
        le.bind('<FocusIn>', clear)

        def keep(e=None):
            d['time'] = te.get()
            v = le.get().strip()
            d['label'] = '' if v == placeholder else v[:LABEL_MAX]
        te.bind('<KeyRelease>', keep)
        le.bind('<KeyRelease>', keep)

        seg = tk.Frame(box, bg=C_BG, padx=self.u(2), pady=self.u(2))
        seg.pack(anchor='w', pady=(self.u(10), 0))
        for name, m in (('每週重複', 'week'), ('指定日期', 'date')):
            on = d['mode'] == m

            def setm(m=m):
                keep()
                d['mode'] = m
                self.refresh()
            self.button(seg, name, setm, bg=C_GOLD if on else C_BG, fg=C_BG if on else C_MUTED,
                        hover=C_GOLD_HI if on else C_CARD, size=9, padx=10, pady=3,
                        weight='bold' if on else 'normal').pack(side='left')

        if d['mode'] == 'week':
            self.week_picker(box)
        else:
            self.month_picker(box)

        msg = self.label(box, '', 8, C_RED, bg=C_CARD2)
        msg.pack(anchor='w')

        def ok():
            keep()
            tm = parse_time(d['time'])
            if not tm:
                msg.config(text='時間格式不對，請輸入像 07:30 這樣')
                te.config(highlightbackground=C_RED)
                return
            today = datetime.date.today().isoformat()
            dates = sorted(x for x in d['dates'] if x >= today) if d['mode'] == 'date' else []
            if d['mode'] == 'date' and not dates:
                msg.config(text='請在月曆上至少點選一天')
                return
            new = {'time': tm, 'label': d['label'][:LABEL_MAX], 'on': True,
                   'days': sorted(d['days']) if d['mode'] == 'week' else [], 'dates': dates}
            alarms = p.cfg['alarms']
            if self.editing < len(alarms):
                alarms[self.editing] = new
            else:
                alarms.append(new)
            alarms.sort(key=lambda x: x['time'])
            self.editing = None
            self.draft = None
            p.save()
            self.refresh()

        def cancel():
            self.editing = None
            self.draft = None
            self.refresh()
        btns = tk.Frame(box, bg=C_CARD2)
        btns.pack(fill='x', pady=(self.u(4), 0))
        self.button(btns, '儲存', ok, bg=C_GOLD, fg=C_BG, hover=C_GOLD_HI, size=9,
                    padx=14, pady=4, weight='bold').pack(side='right')
        self.button(btns, '取消', cancel, bg=C_CARD2, fg=C_MUTED, hover=C_LINE, size=9,
                    padx=10, pady=4).pack(side='right', padx=self.u(6))
        te.bind('<Return>', lambda e: ok())
        le.bind('<Return>', lambda e: ok())
        if d.pop('focus', False):
            def focus():
                try:
                    te.focus_force()
                    te.select_range(0, 'end')
                except tk.TclError:
                    pass
            p.root.after(50, focus)

    def week_picker(self, box):
        days = self.draft['days']
        drow = tk.Frame(box, bg=C_CARD2)
        drow.pack(fill='x', pady=(self.u(10), 0))
        chips = []

        def paint():
            for i, ch in enumerate(chips):
                on = i in days
                ch.config(bg=C_PINK if on else C_BG, fg=C_BG if on else C_MUTED)

        def flip(i):
            if i in days:
                days.remove(i)
            else:
                days.append(i)
            paint()
        for i in range(7):
            ch = tk.Label(drow, text=WEEK[i], font=self.font(9, 'bold'), width=2, pady=self.u(3), cursor='hand2')
            ch.bind('<Button-1>', lambda e, i=i: flip(i))
            ch.pack(side='left', padx=(0, self.u(4)))
            chips.append(ch)
        paint()
        quick = tk.Frame(box, bg=C_CARD2)
        quick.pack(fill='x', pady=(self.u(6), 0))
        for name, ds in (('平日', [0, 1, 2, 3, 4]), ('週末', [5, 6]), ('每天', list(range(7)))):
            def setd(ds=ds):
                days[:] = ds
                paint()
            self.button(quick, name, setd, bg=C_CARD2, fg=C_MUTED, hover=C_LINE,
                        size=8, padx=6, pady=1).pack(side='left')
        self.label(box, '星期都不選 = 只響一次', 8, C_MUTED, bg=C_CARD2).pack(anchor='w', pady=(self.u(4), 0))

    def month_picker(self, box):
        d = self.draft
        y, m = d['month']
        today = datetime.date.today()
        cal = tk.Frame(box, bg=C_BG, padx=self.u(8), pady=self.u(8))
        cal.pack(fill='x', pady=(self.u(10), 0))
        head = tk.Frame(cal, bg=C_BG)
        head.pack(fill='x')

        def shift(n):
            mm = y * 12 + (m - 1) + n
            d['month'] = (mm // 12, mm % 12 + 1)
            self.refresh()
        can_back = (y, m) > (today.year, today.month)
        self.button(head, '‹', lambda: shift(-1) if can_back else None, bg=C_BG,
                    fg=C_TEXT if can_back else C_OFF, hover=C_CARD if can_back else C_BG,
                    size=11, padx=8, pady=0).pack(side='left')
        self.label(head, f'{y} 年 {m} 月', 10, C_TEXT, 'bold', bg=C_BG).pack(side='left', expand=True)
        self.button(head, '›', lambda: shift(1), bg=C_BG, fg=C_TEXT, hover=C_CARD,
                    size=11, padx=8, pady=0).pack(side='right')

        grid = tk.Frame(cal, bg=C_BG)
        grid.pack(pady=(self.u(6), 0))
        for i, w in enumerate(WEEK):
            self.label(grid, w, 8, C_MUTED if i < 5 else C_PINK, bg=C_BG, width=3).grid(
                row=0, column=i, pady=(0, self.u(2)))
        cells = {}

        def sel_text():
            fut = sorted(x for x in d['dates'] if x >= today.isoformat())
            return f'已選 {len(fut)} 天' if fut else '點日期來選擇（可以選好幾天）'

        def paint(ds):
            c = cells[ds]
            day = datetime.date.fromisoformat(ds)
            if day < today:
                c.config(bg=C_BG, fg=C_OFF, cursor='')
            elif ds in d['dates']:
                c.config(bg=C_PINK, fg=C_BG)
            elif day == today:
                c.config(bg=C_CARD2, fg=C_GOLD)
            else:
                c.config(bg=C_BG, fg=C_TEXT)

        def flip(ds):
            if datetime.date.fromisoformat(ds) < today:
                return
            if ds in d['dates']:
                d['dates'].remove(ds)
            else:
                d['dates'].append(ds)
            paint(ds)
            count.config(text=sel_text())
        for r, week in enumerate(calendar.monthcalendar(y, m), start=1):
            for col, n in enumerate(week):
                if not n:
                    continue
                ds = f'{y:04d}-{m:02d}-{n:02d}'
                c = tk.Label(grid, text=str(n), font=self.font(9, 'bold'), width=3, pady=self.u(3), cursor='hand2')
                c.grid(row=r, column=col, padx=self.u(1), pady=self.u(1))
                c.bind('<Button-1>', lambda e, ds=ds: flip(ds))
                cells[ds] = c
                paint(ds)
        bot = tk.Frame(cal, bg=C_BG)
        bot.pack(fill='x', pady=(self.u(6), 0))
        count = self.label(bot, sel_text(), 8, C_MUTED, bg=C_BG)
        count.pack(side='left')

        def clear_all():
            d['dates'].clear()
            self.refresh()
        self.button(bot, '清除', clear_all, bg=C_BG, fg=C_MUTED, hover=C_CARD,
                    size=8, padx=6, pady=1).pack(side='right')

    def new_alarm(self):
        if self.editing is not None:
            return
        t = datetime.date.today()
        self.confirm_del = None
        self.draft = {'time': '08:00', 'label': '', 'days': [0, 1, 2, 3, 4], 'dates': [],
                      'mode': 'week', 'month': (t.year, t.month), 'focus': True}
        self.editing = len(self.pet.cfg['alarms'])
        self.refresh()

    def edit_alarm(self, i):
        if self.editing is not None:
            return
        a = self.pet.cfg['alarms'][i]
        t = datetime.date.today()
        dates = list(a['dates'])
        fut = sorted(x for x in dates if x >= t.isoformat())
        first = datetime.date.fromisoformat(fut[0]) if fut else t
        self.confirm_del = None
        self.draft = {'time': a['time'], 'label': a['label'], 'days': list(a['days']),
                      'dates': dates, 'mode': 'date' if dates else 'week',
                      'month': (first.year, first.month), 'focus': True}
        self.editing = i
        self.refresh()

    def ask_delete(self, i):
        p = self.pet
        if self.confirm_job:
            p.root.after_cancel(self.confirm_job)
            self.confirm_job = None
        if self.confirm_del == i:
            self.confirm_del = None
            del p.cfg['alarms'][i]
            p.save()
            self.refresh()
            return
        self.confirm_del = i
        self.refresh()
        self.confirm_job = p.root.after(DELETE_CONFIRM_MS, self.expire_delete)

    def expire_delete(self):
        self.confirm_job = None
        if self.confirm_del is not None:
            self.confirm_del = None
            self.refresh()

    def toggle_alarm(self, i):
        a = self.pet.cfg['alarms'][i]
        a['on'] = not a['on']
        self.confirm_del = None
        self.pet.save()
        self.refresh()

    def toggle_hourly(self):
        h = self.pet.cfg['hourly']
        h['on'] = not h['on']
        self.pet.save()
        self.refresh()

    def toggle_hat(self):
        self.pet.cfg['hat'] = not self.pet.cfg['hat']
        self.pet.save()
        self.refresh()


class MonkeyPet:
    def __init__(self):
        self.cfg, load_msg = load_config()

        self.root = tk.Tk()
        self.root.title('小猴')
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.config(bg=KEY)
        try:
            self.root.wm_attributes('-transparentcolor', KEY)
        except tk.TclError:
            pass
        self.dpi = self.root.winfo_fpixels('1i') / 96.0
        fams = set(tkfont.families(self.root))
        self.fam = next((f for f in ('Microsoft JhengHei UI', 'Microsoft JhengHei', 'PingFang TC',
                                     'Noto Sans CJK TC', 'Noto Sans TC') if f in fams), 'TkDefaultFont')
        self.canvas = tk.Canvas(self.root, bg=KEY, highlightthickness=0, bd=0)
        self.canvas.pack()
        icon_zoom = max(2, self.u(2))
        self.icon = tk.PhotoImage(data=SPRITES['happy']).zoom(icon_zoom)
        self.icon_hat = tk.PhotoImage(data=SPRITES['hat_happy']).zoom(icon_zoom)
        self.bell_icon = tk.PhotoImage(data=SPRITES['bell0'])

        self.state = 'idle'
        self.t = 0
        self.frame = 0
        self.last_touch = time.monotonic()
        self.deadline = None
        self.timer_label = ''
        self.hover = False
        self.blink_left = 0
        self.press = None
        self.dragging = False
        self.needs_ack = True
        self.clicks = 0
        self.click_job = None
        self.toast = None
        self.toast_size = (0, 0)
        self.peel = None
        self.last_ops = None
        self.save_failed = False
        self.x = self.y = 0
        self.scheduler = Scheduler(datetime.datetime.now())
        self.panel = Panel(self)
        self.apply_size()

        c = self.canvas
        c.bind('<ButtonPress-1>', self.on_press)
        c.bind('<B1-Motion>', self.on_drag)
        c.bind('<ButtonRelease-1>', self.on_release)
        c.bind('<Button-3>', lambda e: self.panel.toggle())
        c.bind('<Enter>', lambda e: self.set_hover(True))
        c.bind('<Leave>', lambda e: self.set_hover(False))

        self.go_home()
        if load_msg:
            self.root.after(800, lambda: self.notify(load_msg))
        self.loop()

    def u(self, n):
        return int(round(n * self.dpi))

    def font(self, size, weight='normal'):
        return (self.fam, size, weight)

    def apply_size(self):
        self.S = max(2, round(self.cfg['size'] * self.dpi))
        cache = {}
        self.img = {}
        for k, v in SPRITES.items():
            if v not in cache:
                cache[v] = tk.PhotoImage(data=v).zoom(self.S)
            self.img[k] = cache[v]
        self.canvas.config(width=BW * self.S, height=BH * self.S)
        self.last_ops = None

    def pet_center(self, x=None, y=None):
        x = self.x if x is None else x
        y = self.y if y is None else y
        return x + (PX + PET / 2) * self.S, y + (PY + PET / 2) * self.S

    def pet_area(self):
        return monitor_work_area(self.root, *self.pet_center())

    def clamp(self, x, y):
        S = self.S
        l, t, r, b = monitor_work_area(self.root, *self.pet_center(x, y))
        x = min(max(x, l - PX * S), r - (PX + PET) * S)
        y = min(max(y, t - PY * S), b - BH * S + 2 * S)
        return x, y

    def default_home(self):
        l, t, r, b = primary_work_area(self.root)
        return r - (PX + PET + 2) * self.S, b - BH * self.S + 2 * self.S

    def go_home(self):
        home = self.cfg['home']
        if home and monitor_work_area(self.root, *self.pet_center(*home), nearest=False) is None:
            self.cfg['home'] = None
            self.save()
            home = None
        if home:
            self.x, self.y = self.clamp(*home)
        else:
            self.x, self.y = self.default_home()
        self.move()

    def move(self):
        self.root.geometry(f'+{int(self.x)}+{int(self.y)}')

    def save(self):
        if save_config(self.cfg):
            self.save_failed = False
        elif not self.save_failed:
            self.save_failed = True
            self.notify('設定存檔失敗，詳情請看 .monkeypet.log')

    def time_left(self):
        if self.deadline is None:
            return 0
        return max(0, int(self.deadline - time.monotonic()))

    def start_timer(self, seconds, label):
        self.deadline = time.monotonic() + seconds
        self.timer_label = label
        self.touch()
        self.set_state('happy')
        self.panel.refresh()

    def cancel_timer(self):
        self.deadline = None
        self.panel.refresh()

    def check_clock(self):
        now = datetime.datetime.now()
        result = self.scheduler.poll(self.cfg['alarms'], now)
        if result is None:
            return
        fired, changed, fresh = result
        if changed:
            self.save()
            self.panel.refresh()
        if fired:
            dt, a = fired[-1]
            text = f"{a['time']}  {a['label'] or '鬧鐘'}"
            if dt < now.replace(second=0, microsecond=0):
                text += '（錯過了）'
            if len(fired) > 1:
                text += f'，另有 {len(fired) - 1} 個'
            self.ring(text, ack=True)
            return
        h = self.cfg['hourly']
        if fresh and h['on'] and now.minute == 0 and hour_in_range(now.hour, h['from'], h['to']):
            self.ring(f'{now.hour} 點整', ack=False)

    def ring(self, text, ack=True):
        if self.state == 'alarm' and self.needs_ack and not ack:
            return
        self.peel = None
        self.needs_ack = ack
        self.set_state('alarm')
        beep()
        self.show_toast(text, ack)

    def notify(self, text):
        if self.state == 'alarm' and self.needs_ack:
            return
        self.show_toast(text, False)

    def dismiss_alarm(self):
        self.close_toast()
        self.set_state('calm')

    def touch(self):
        self.last_touch = time.monotonic()

    def set_hover(self, v):
        self.hover = v

    def on_press(self, e):
        self.press = (e.x_root, e.y_root, self.x, self.y)
        self.dragging = False

    def on_drag(self, e):
        if not self.press or self.state in SHOW:
            return
        dx, dy = e.x_root - self.press[0], e.y_root - self.press[1]
        if abs(dx) + abs(dy) > DRAG_THRESHOLD:
            self.dragging = True
        if self.dragging:
            self.x, self.y = self.press[2] + dx, self.press[3] + dy
            self.move()
            if self.state != 'alarm':
                self.set_state('shock')
            self.panel.place()
            self.place_toast()

    def on_release(self, e):
        self.touch()
        acking = self.state == 'alarm' and self.needs_ack
        if self.dragging:
            self.x, self.y = self.clamp(self.x, self.y)
            self.move()
            self.cfg['home'] = [int(self.x), int(self.y)]
            self.save()
            if self.state != 'alarm':
                self.set_state('happy')
            self.panel.place()
            self.place_toast()
        elif acking:
            self.dismiss_alarm()
        elif self.state == 'sleep':
            self.set_state('wake')
        elif self.state in CLICKABLE:
            self.count_click()
        if not self.dragging and not acking:
            self.close_toast()
        self.press = None
        self.dragging = False

    def count_click(self):
        self.clicks += 1
        if self.click_job:
            self.root.after_cancel(self.click_job)
        self.click_job = self.root.after(CLICK_GAP_MS, self.resolve_clicks)

    def resolve_clicks(self):
        n, self.clicks, self.click_job = self.clicks, 0, None
        if self.state not in CLICKABLE:
            return
        if n >= 3:
            self.set_state('think')
        elif n == 2:
            self.start_run()
        else:
            self.set_state('happy')

    def set_state(self, s):
        self.state = s
        self.t = 0

    def start_run(self):
        if self.state in SHOW:
            return
        self.touch()
        self.peel = None
        self.set_state('drop')

    def loop(self):
        for step in (self.check_clock, self.update, self.draw, self.panel.tick):
            try:
                step()
            except Exception:
                log_error()
        self.root.after(TICK_MS, self.loop)

    def update(self):
        self.t += 1
        self.frame += 1
        s, t = self.state, self.t

        if (self.deadline is not None and time.monotonic() >= self.deadline
                and s != 'alarm' and s not in SHOW):
            self.deadline = None
            if self.timer_label == '番茄鐘':
                msg = '番茄鐘結束，休息一下吧！'
            else:
                msg = f'{self.timer_label}時間到！'
            self.ring(msg, ack=True)
            self.panel.refresh()
            return

        if s == 'idle':
            if self.blink_left > 0:
                self.blink_left -= 1
            elif random.random() < BLINK_CHANCE:
                self.blink_left = BLINK_TICKS
            if (time.monotonic() - self.last_touch > SLEEP_AFTER and self.deadline is None
                    and not self.panel.is_open):
                self.set_state('sleep')
        elif s in ('happy', 'think', 'wake'):
            if t > DUR[s]:
                self.set_state('idle')
        elif s == 'shock':
            if t > DUR['shock'] and not self.dragging:
                self.set_state('happy')
        elif s == 'alarm':
            if self.needs_ack:
                if t % ALARM_BEEP_EVERY == 0 and t <= ALARM_BEEP_FOR:
                    beep()
                if t > ALARM_TIMEOUT:
                    self.close_toast()
                    self.set_state('idle')
            elif t > DUR['chime']:
                self.set_state('happy')
        elif s == 'calm':
            if t > DUR['calm']:
                self.set_state('idle')
                self.start_run()
        elif s == 'drop':
            if t >= DUR['drop']:
                self.set_state('peel')
        elif s == 'peel':
            if t >= DUR['peel']:
                self.set_state('eat')
        elif s == 'eat':
            if t >= DUR['eat']:
                self.peel = list(PEEL_START)
                self.set_state('toss')
        elif s == 'toss':
            p = self.peel
            if p and p[1] < PEEL_FLOOR:
                p[0] += p[2]
                p[1] += p[3]
                p[3] += PEEL_GRAVITY
            if t >= DUR['toss']:
                self.peel = None
                self.set_state('happy')

    def think_frame(self, prefix, t):
        if THINK_PAUSE[0] <= t < THINK_PAUSE[1]:
            return prefix + '3'
        return prefix + ('2' if (t // 4) % 2 else '1')

    def sprite_name(self):
        s, t = self.state, self.t
        if s == 'idle':
            if self.blink_left > 0:
                return 'blink'
            return 'idle1' if (self.frame // 8) % 2 == 0 else 'idle2'
        if s == 'sleep':
            return 'sleep1' if (self.frame // 10) % 2 == 0 else 'sleep2'
        if s in ('shock', 'alarm'):
            return 'shock'
        if s == 'happy':
            return 'happy' if t % 4 < 2 else 'idle1'
        if s == 'calm':
            return 'blink'
        if s == 'drop':
            return 'shock' if t < FALL else 'hold_look'
        if s == 'peel':
            return 'hold_look'
        if s == 'eat':
            k = t % CHEW
            if k < BITE_OPEN:
                return 'hold_open'
            return 'hold_chew1' if (k // 2) % 2 == 0 else 'hold_chew2'
        if s == 'toss':
            return 'happy'
        if s == 'wake':
            if t < 4:
                return 'blink'
            return self.think_frame('sthink', t)
        if s == 'think':
            return self.think_frame('think', t)
        return 'idle1'

    def render_ops(self):
        ops = []

        def img(k, x, y):
            ops.append(('img', k, x, y))
        name = self.sprite_name()
        img(name, PX, PY)
        if self.cfg['hat'] and 'hat_' + name in self.img:
            img('hat_' + name, PX, PY)
        self.banana_ops(img, name)
        if self.state == 'alarm':
            img('bell1' if (self.t // 2) % 2 == 0 else 'bell2', PX + 2, PY - 28)
            lines = [(-1, 9, 2, 7), (-2, 15, 2, 15), (-1, 21, 2, 23),
                     (28, 7, 31, 9), (28, 15, 32, 15), (28, 23, 31, 21)]
            for i, (x1, y1, x2, y2) in enumerate(lines):
                if (self.t + i) % 3:
                    ops.append(('line', PX + x1, y1, PX + x2, y2))
        if self.state == 'sleep':
            off = (self.frame // 6) % 3
            img('zz', PX + 24, PY - 8 - off * 2)
        if (self.hover and self.deadline is not None and not self.panel.is_open
                and self.state in ('idle', 'happy', 'shock')):
            ops.append(('text', PX + 16, PY - 6, fmt_left(self.time_left())))
        return ops

    def banana_ops(self, img, name):
        s, t = self.state, self.t
        bob = 'b' if name == 'hold_chew2' else ''
        hands = 'hands1' if bob else 'hands'
        if s == 'drop':
            if t < FALL:
                img('banana_whole', PX, -14 + (PY + 10 + 14) * (t / FALL) ** 2)
            else:
                img('banana0', PX, PY)
                img('hands', PX, PY)
        elif s == 'peel':
            img('banana0' if t < 6 else 'banana1', PX, PY)
            img('hands', PX, PY)
            if 5 <= t <= 9:
                img('sparkle', PX - 1 + (t % 2), PY + 8)
        elif s == 'eat':
            bite = min(t // CHEW, 2)
            stage = bite + 1 if t % CHEW < BITE_OPEN else bite + 2
            img(f'banana{stage}{bob}', PX, PY)
            img(hands, PX, PY)
        elif s == 'toss' and self.peel:
            if t < 18 or t % 2:
                img('peel', self.peel[0], self.peel[1])
        if s in ('think', 'wake') and t >= DOTS_FROM:
            img(f'dots{min(3, 1 + (t - DOTS_FROM) // 4)}', PX + (18 if s == 'think' else 16), PY - 8)
        if s == 'toss' and 4 <= t <= 16:
            img('sparkle', PX + 22 + (t // 3) % 2 * 3, PY - 4 - (t // 3) % 3)

    def draw(self):
        ops = self.render_ops()
        if ops == self.last_ops:
            return
        self.last_ops = ops
        c, S = self.canvas, self.S
        c.delete('all')
        for op in ops:
            kind = op[0]
            if kind == 'img':
                c.create_image(op[2] * S, op[3] * S, image=self.img[op[1]], anchor='nw')
            elif kind == 'line':
                c.create_line(op[1] * S, op[2] * S, op[3] * S, op[4] * S, fill=C_SHAKE, width=S)
            else:
                c.create_text(op[1] * S, op[2] * S, text=op[3], fill=C_TIMER,
                              font=self.font(max(10, 2 * S), 'bold'))

    def show_toast(self, text, ack):
        self.close_toast()
        w = tk.Toplevel(self.root)
        w.overrideredirect(True)
        w.attributes('-topmost', True)
        w.config(bg=KEY)
        try:
            w.wm_attributes('-transparentcolor', KEY)
        except tk.TclError:
            pass
        f = self.font(12, 'bold')
        tw = tkfont.Font(family=self.fam, size=12, weight='bold').measure(text)
        if ack:
            tw += tkfont.Font(family=self.fam, size=8).measure('點小猴') + self.u(14)
        W, H, r = tw + self.u(56), self.u(44), self.u(14)
        lw = max(1, self.u(1.5))
        c = tk.Canvas(w, width=W, height=H + self.u(10), bg=KEY, highlightthickness=0)
        c.pack()
        rounded(c, 1, 1, W - 1, H, r, fill=C_BG, outline=C_GOLD, width=lw)
        tx = W - self.u(40)
        c.create_polygon(tx, H - 1, tx + self.u(12), H - 1, tx + self.u(16), H + self.u(9), fill=C_BG, outline='')
        c.create_line(tx, H - 1, tx + self.u(16), H + self.u(9), tx + self.u(12), H - 1, fill=C_GOLD, width=lw)
        c.create_image(self.u(12), H // 2, image=self.bell_icon, anchor='w')
        c.create_text(self.u(42), H // 2, text=text, font=f, anchor='w', fill=C_TEXT)
        if ack:
            c.create_text(W - self.u(14), H // 2, text='點小猴', font=self.font(8), anchor='e', fill=C_MUTED)

        def clicked(e):
            if self.state == 'alarm' and self.needs_ack:
                self.dismiss_alarm()
            else:
                self.close_toast()
        c.bind('<Button-1>', clicked)
        self.toast = w
        self.toast_size = (W, H)
        self.place_toast()
        if not ack:
            self.root.after(CHIME_TOAST_MS, lambda: self.close_toast(w))

    def place_toast(self):
        if not self.toast:
            return
        W, H = self.toast_size
        l, t, r, b = self.pet_area()
        px = int(self.x + (PX + 22) * self.S - W + self.u(30))
        py = int(self.y + (PY - 30) * self.S - H - self.u(10))
        try:
            self.toast.geometry(f'+{max(l + 8, min(px, r - W - 8))}+{max(t + 8, py)}')
        except tk.TclError:
            pass

    def close_toast(self, which=None):
        if self.toast and (which is None or which is self.toast):
            try:
                self.toast.destroy()
            except tk.TclError:
                pass
            self.toast = None

    def change_size(self, v):
        if v == self.cfg['size'] or v not in SIZE_VALUES:
            return
        cx = self.x + (PX + PET / 2) * self.S
        by = self.y + (PY + PET) * self.S
        self.cfg['size'] = v
        self.apply_size()
        if self.cfg['home']:
            self.x, self.y = self.clamp(cx - (PX + PET / 2) * self.S, by - (PY + PET) * self.S)
            self.cfg['home'] = [int(self.x), int(self.y)]
            self.move()
        else:
            self.go_home()
        self.save()
        self.panel.refresh()
        self.place_toast()

    def reset_home(self):
        self.cfg['home'] = None
        self.save()
        self.go_home()
        self.panel.refresh()
        self.place_toast()

    def quit(self):
        self.save()
        self.panel.close()
        self.close_toast()
        self.root.destroy()


def main():
    global _instance_lock
    _instance_lock = acquire_single_instance()
    if _instance_lock is None:
        sys.exit(0)
    threading.Thread(target=prepare_bell, daemon=True).start()
    MonkeyPet().root.mainloop()


if __name__ == '__main__':
    main()
