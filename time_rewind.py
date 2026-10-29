
import tkinter as tk
import math
import winsound
from pathlib import Path

from pynput import keyboard
from queue import Queue

import ctypes

# ウィンドウを作成
root = tk.Tk()
root.title("時を戻そう！")
root.geometry("500x500")

# 透明にする色を指定
TRANSPARENT_COLOR = "#010101"

root.configure(bg=TRANSPARENT_COLOR)

# 最前面表示
root.attributes("-topmost", True)

# ウィンドウ枠をなくす
root.overrideredirect(True)

# 指定色を透明にする（Windows用）
root.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)

# 起動時は非表示
root.withdraw()

# 画面全体のサイズを取得
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# ウィンドウを画面全体に広げる
window_width = screen_width
window_height = screen_height

root.geometry(f"{window_width}x{window_height}+0+0")

# 画面全体を描画領域にする
canvas = tk.Canvas(
    root,
    width=screen_width,
    height=screen_height,
    bg=TRANSPARENT_COLOR,
    highlightthickness=0
)
canvas.pack()

# 時計の中心座標
cx = screen_width // 2
cy = screen_height // 2
angle = 0

# キー入力イベントを受け渡す
event_queue = Queue()

# アニメーションの実行状態
is_animating = False

# アニメーション予約の管理（今回追加）
clock_after_id = None
message_after_id = None

# 擬音演出の管理
impact_font_size = 12
impact_after_id = None

# 衝撃波アニメーションの管理
shockwave_radius = 10
shockwave_after_id = None

# 画面全体を覆うために必要な衝撃波の半径
shockwave_max_radius = math.hypot(
    screen_width / 2,
    screen_height / 2
)

# 衝撃波を約0.8秒で画面全体に広げる
shockwave_interval = 25
shockwave_duration = 800

# アニメーションの実行回数
shockwave_steps = shockwave_duration // shockwave_interval

# 1回あたりの半径の増加量
shockwave_speed = (
    shockwave_max_radius - 10
) / shockwave_steps

# Ctrl+Zの押下状態
pressed_ctrl = False
pressed_z = False

# Ctrl+Shift+Qの押下状態
pressed_shift = False
pressed_q = False

# 時計の外枠
clock_frame = canvas.create_oval(
    cx - 120, cy - 120,
    cx + 120, cy + 120,
    outline="#163A70",
    width=7
)

# 時計の目盛り
for i in range(12):
    tick_angle = math.radians(i * 30 - 90)

    x1 = cx + 100 * math.cos(tick_angle)
    y1 = cy + 100 * math.sin(tick_angle)

    x2 = cx + 110 * math.cos(tick_angle)
    y2 = cy + 110 * math.sin(tick_angle)

    canvas.create_line(
        x1, y1, x2, y2,
        fill="#163A70",
        width=4,
        tags="clock_tick"
    )

# 長針
canvas.create_line(
    cx, cy, cx, cy - 90,
    fill="#D62828",
    width=7,
    tags="minute_hand"
)

# 短針
canvas.create_line(
    cx, cy, cx, cy - 60,
    fill="#111827",
    width=9,
    tags="hour_hand"
)

# 時計の中心
clock_center = canvas.create_oval(
    cx - 7, cy - 7,
    cx + 7, cy + 7,
    fill="#111827",
    outline=""
)

# メッセージをCanvasに描画
message_text = canvas.create_text(
    cx, cy + 170,
    text="時を戻そう！",
    font=("Yu Gothic UI", 12, "bold"),
    fill="#111827",
    tags="message"
)

# 漫画風の擬音をCanvasに追加
impact_text = canvas.create_text(
    cx, cy,
    text="ズキューン！",
    font=("Yu Gothic UI", 12, "bold"),
    fill="#D62828",
    state="hidden",
    tags="impact"
)

# 衝撃波用の円を作成
shockwave = canvas.create_oval(
    cx - 10, cy - 10,
    cx + 10, cy + 10,
    outline="#D62828",
    fill="#000000",
    width=4,
    state="hidden",
    tags="shockwave"
)

# 衝撃波をCanvas内の最背面に移動
canvas.tag_lower(shockwave)

def rewind_clock():
    global angle, clock_after_id

    # アニメーション停止中なら処理しない
    if not is_animating:
        return

    # 角度を減らして逆回転
    angle -= 10

    # 長針の先端座標
    minute_angle = math.radians(angle - 90)

    mx = cx + 90 * math.cos(minute_angle)
    my = cy + 90 * math.sin(minute_angle)

    # 長針を移動
    canvas.coords(
        "minute_hand",
        cx, cy, mx, my
    )

    # 短針の先端座標
    hour_angle = math.radians(angle / 12 - 90)

    hx = cx + 60 * math.cos(hour_angle)
    hy = cy + 60 * math.sin(hour_angle)

    # 短針を移動
    canvas.coords(
        "hour_hand",
        cx, cy, hx, hy
    )

    # 30ミリ秒後に再実行
    if is_animating:
        clock_after_id = root.after(30, rewind_clock)

# 文字サイズを管理
font_size = 12

def animate_message():
    global font_size, message_after_id

    if not is_animating:
        return

    if font_size < 32:
        font_size += 2

        canvas.itemconfig(
            message_text,
            font=("Yu Gothic UI", font_size, "bold")
        )

        message_after_id = root.after(50, animate_message)

def animate_impact():
    global impact_font_size, impact_after_id

    if not is_animating:
        return

    # 文字を表示
    canvas.itemconfig(impact_text, state="normal")

    # 文字を拡大
    impact_font_size += 4

    canvas.itemconfig(
        impact_text,
        font=("Yu Gothic UI", impact_font_size, "bold")
    )

    if impact_font_size < 48:
        # 40ミリ秒後に再び拡大
        impact_after_id = root.after(40, animate_impact)
    else:
        # 最大サイズで400ミリ秒維持してから消す
        impact_after_id = root.after(400, hide_impact)


def hide_impact():
    global impact_after_id

    canvas.itemconfig(impact_text, state="hidden")
    impact_after_id = None

# 音声ファイルの場所
sound_path = Path(__file__).resolve().parent / "rewind.wav"

def animate_shockwave():
    global shockwave_radius, shockwave_after_id

    # 演出停止中なら何もしない
    if not is_animating:
        return

    # 衝撃波を表示
    canvas.itemconfig(shockwave, state="normal")

    # 画面サイズに合わせた速度で半径を大きくする
    shockwave_radius += shockwave_speed

    # 黒い衝撃波が時計の外枠付近まで広がったら白くする
    if shockwave_radius >= 120:
        canvas.itemconfig(clock_frame, outline="#FFFFFF")
        canvas.itemconfig("minute_hand", fill="#FF5555")
        canvas.itemconfig("hour_hand", fill="#FFFFFF")
        canvas.itemconfig("clock_tick", fill="#FFFFFF")
        canvas.itemconfig(clock_center, fill="#FFFFFF")

    # 衝撃波が文字の位置まで広がったら白くする
    if shockwave_radius >= 190:
        canvas.itemconfig(message_text, fill="#FFFFFF")

    # 円の座標を更新
    canvas.coords(
        shockwave,
        cx - shockwave_radius,
        cy - shockwave_radius,
        cx + shockwave_radius,
        cy + shockwave_radius
    )

    # 画面全体を覆うまで拡大を続ける
    if shockwave_radius < shockwave_max_radius:
        shockwave_after_id = root.after(25, animate_shockwave)
    else:
        shockwave_after_id = None

def play_voice():
    if sound_path.exists():
        winsound.PlaySound(
            str(sound_path),
            winsound.SND_FILENAME | winsound.SND_ASYNC
        )
    else:
        print("音声ファイルが見つかりません:", sound_path)

def enable_click_through():
    user32 = ctypes.windll.user32

    GWL_EXSTYLE = -20
    WS_EX_TRANSPARENT = 0x00000020

    # Windows APIの引数と戻り値を設定
    user32.GetParent.argtypes = [ctypes.c_void_p]
    user32.GetParent.restype = ctypes.c_void_p

    # Tkinterの最上位ウィンドウを取得
    hwnd = user32.GetParent(root.winfo_id())

    # Windows APIの引数と戻り値を設定
    user32.GetWindowLongPtrW.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int
    ]
    user32.GetWindowLongPtrW.restype = ctypes.c_ssize_t

    user32.SetWindowLongPtrW.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int,
        ctypes.c_ssize_t
    ]
    user32.SetWindowLongPtrW.restype = ctypes.c_ssize_t

    # 現在の設定を取得
    style = user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)

    # クリック透過だけを追加
    user32.SetWindowLongPtrW(
        hwnd,
        GWL_EXSTYLE,
        style | WS_EX_TRANSPARENT
    )

def on_press(key):
    global pressed_ctrl, pressed_z
    global pressed_shift, pressed_q

    # Ctrlキー
    if key in (
        keyboard.Key.ctrl,
        keyboard.Key.ctrl_l,
        keyboard.Key.ctrl_r
    ):
        pressed_ctrl = True

    # Shiftキー
    if key in (
        keyboard.Key.shift,
        keyboard.Key.shift_l,
        keyboard.Key.shift_r
    ):
        pressed_shift = True

    # 文字キー
    char = getattr(key, "char", None)

    if char:
        char = char.lower()

        # Ctrl+Zを検知
        if char in ("z", "\x1a"):
            if pressed_ctrl and not pressed_z:
                event_queue.put("rewind")

            pressed_z = True

        # Qキーを検知
        if char in ("q", "\x11"):
            if pressed_ctrl and pressed_shift and not pressed_q:
                event_queue.put("quit")

            pressed_q = True


def on_release(key):
    global pressed_ctrl, pressed_z
    global pressed_shift, pressed_q

    if key in (
        keyboard.Key.ctrl,
        keyboard.Key.ctrl_l,
        keyboard.Key.ctrl_r
    ):
        pressed_ctrl = False

    if key in (
        keyboard.Key.shift,
        keyboard.Key.shift_l,
        keyboard.Key.shift_r
    ):
        pressed_shift = False

    char = getattr(key, "char", None)

    if char:
        char = char.lower()

        if char in ("z", "\x1a"):
            pressed_z = False

        if char in ("q", "\x11"):
            pressed_q = False

def stop_rewind():
    global is_animating
    global clock_after_id, message_after_id
    global impact_after_id
    global shockwave_after_id

    is_animating = False

    if clock_after_id is not None:
        root.after_cancel(clock_after_id)
        clock_after_id = None

    if message_after_id is not None:
        root.after_cancel(message_after_id)
        message_after_id = None

    # 擬音アニメーションの予約を取り消す
    if impact_after_id is not None:
        root.after_cancel(impact_after_id)
        impact_after_id = None

    # 擬音を非表示に戻す
    canvas.itemconfig(impact_text, state="hidden")

    # 衝撃波の予約を取り消す
    if shockwave_after_id is not None:
        root.after_cancel(shockwave_after_id)
        shockwave_after_id = None

    # 衝撃波を非表示に戻す
    canvas.itemconfig(shockwave, state="hidden")

    # 時計の色を元に戻す
    canvas.itemconfig(clock_frame, outline="#163A70")
    canvas.itemconfig("minute_hand", fill="#D62828")
    canvas.itemconfig("hour_hand", fill="#111827")
    canvas.itemconfig("clock_tick", fill="#163A70")
    canvas.itemconfig(clock_center, fill="#111827")
    canvas.itemconfig(message_text, fill="#111827")

    root.withdraw()

def start_rewind():
    global is_animating, angle, font_size
    global impact_font_size
    global shockwave_radius

    # 演出中は再実行しない
    if is_animating:
        return

    is_animating = True
    angle = 0
    font_size = 12

    # 擬音の文字サイズを初期化
    impact_font_size = 12

    # 衝撃波の半径を初期化
    shockwave_radius = 10

    # 衝撃波を初期位置に戻す
    canvas.coords(
        shockwave,
        cx - 10, cy - 10,
        cx + 10, cy + 10
    )

    # 時計を画面に表示
    root.deiconify()
    root.lift()

    root.update_idletasks()
    enable_click_through()

    # 文字サイズを初期化
    canvas.itemconfig(
        message_text,
        font=("Yu Gothic UI", font_size, "bold")
    )

    # 演出開始（原因調査用）
    rewind_clock()
    animate_message()
    animate_impact()
    root.after(200, animate_shockwave)
    play_voice()

    # 1.5秒後に演出終了
    root.after(1500, stop_rewind)

def quit_app():
    # 音声停止
    winsound.PlaySound(None, 0)
    
    # キーボード監視を停止
    listener.stop()

    # Tkinterを終了
    root.destroy()

def check_events():
    while not event_queue.empty():
        event = event_queue.get_nowait()

        if event == "quit":
            quit_app()
            return

        elif event == "rewind":
            start_rewind()

    root.after(30, check_events)

# キーボード監視を開始
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release
)
listener.start()

# キーイベントを定期確認
check_events()

root.mainloop()
