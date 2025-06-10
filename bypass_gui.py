import tkinter as tk
from tkinter import messagebox
import subprocess
import time
import requests
from PIL import Image
import io
import base64

def start_bypass():
    api_key = entry_api.get()
    try:
        main_box = list(map(int, entry_main_box.get().split(',')))
        piece_box = list(map(int, entry_piece_box.get().split(',')))
        if len(main_box) != 4 or len(piece_box) != 4:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "รูปแบบ Crop box ไม่ถูกต้อง ให้ใส่ x1,y1,x2,y2")
        return

    try:
        devices = subprocess.check_output(["adb", "devices"]).decode()
        if "device" not in devices.split("\n")[1]:
            messagebox.showerror("ADB Error", "ไม่พบอุปกรณ์ ADB")
            return

        subprocess.run(["adb", "shell", "exec-out", "screencap -p"], shell=True, check=True, stdout=open("screen.png", "wb"))
        img = Image.open("screen.png")
        main_image = img.crop(tuple(main_box))
        piece_image = img.crop(tuple(piece_box))
        main_b64 = base64.b64encode(main_image.tobytes()).decode()
        piece_b64 = base64.b64encode(piece_image.tobytes()).decode()

        data = {
            "puzzleImageB64": main_b64,
            "pieceImageB64": piece_b64
        }
        response = requests.post(f"https://www.sadcaptcha.com/api/v1/puzzle?licenseKey={api_key}", json=data)
        response.raise_for_status()
        data = response.json()
        ratio = data.get("slideXProportion") or data.get("ratio")
        offset = ratio * (main_box[2] - main_box[0])

        subprocess.run(["adb", "shell", "input", "swipe 100 500 {0} 500 1000".format(int(100+offset))], shell=True)
        messagebox.showinfo("สำเร็จ", f"เลื่อนสำเร็จ: {offset:.2f} px")

    except Exception as e:
        messagebox.showerror("Error", str(e))

def image_to_bytes(image):
    with io.BytesIO() as output:
        image.save(output, format="PNG")
        return output.getvalue()

root = tk.Tk()
root.title("🔓 Slider CAPTCHA Bypass")
root.geometry("420x320")

tk.Label(root, text="🔑 API Key:").pack()
entry_api = tk.Entry(root, width=60)
entry_api.pack()

tk.Label(root, text="📷 ตำแหน่งภาพหลัก (x1,y1,x2,y2):").pack()
entry_main_box = tk.Entry(root, width=60)
entry_main_box.insert(0, "100,800,900,1600")
entry_main_box.pack()

tk.Label(root, text="🧩 ตำแหน่งชิ้นส่วน (x1,y1,x2,y2):").pack()
entry_piece_box = tk.Entry(root, width=60)
entry_piece_box.insert(0, "900,800,1200,1100")
entry_piece_box.pack()

tk.Button(root, text="🚀 เริ่ม Bypass", command=start_bypass, bg="green", fg="white", height=2).pack(pady=20)

root.mainloop()