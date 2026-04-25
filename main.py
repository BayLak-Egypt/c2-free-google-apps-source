import socket
import threading
import time
import json
import requests
import base64
import zlib
from concurrent.futures import ThreadPoolExecutor
import customtkinter as ctk
import config  # تأكد أن config.URL يحتوي على رابط الـ Script

class BayLakC2Bridge(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("C2 APPS SCRIPT SERVER - PRO EDITION")
        self.geometry("650x850")
        ctk.set_appearance_mode("dark")
        
        self.running = False
        # تحسين الجلسة لدعم عدد اتصالات أكبر وسرعة استجابة أعلى
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=200, 
            pool_maxsize=200, 
            max_retries=1 # تقليل الإعادة لسرعة الاستجابة
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # استخدام Executor لمنع انهيار البرنامج عند ضغط البيانات
        self.executor = ThreadPoolExecutor(max_workers=50)

        # --- UI Setup ---
        self.setup_ui()

    def setup_ui(self):
        self.header_label = ctk.CTkLabel(self, text="C2 BRIDGE PRO", font=("Orbitron", 28, "bold"), text_color="#00ffcc")
        self.header_label.pack(pady=(30, 10))
        
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(pady=10, padx=40, fill="x")

        self.entry_group = self.create_input("Group/Room Name", config.DEFAULT_GROUP)
        self.entry_ip = self.create_input("Target Host (IP)", config.DEFAULT_IP)
        self.entry_port = self.create_input("Target Port", config.DEFAULT_PORT)

        self.btn_host = ctk.CTkButton(self, text="RUN AS HOST", command=self.run_host, fg_color="#1b5e20", height=45)
        self.btn_host.pack(pady=10, padx=60, fill="x")
        
        self.btn_join = ctk.CTkButton(self, text="RUN AS JOINER", command=self.run_join, fg_color="#0d47a1", height=45)
        self.btn_join.pack(pady=10, padx=60, fill="x")

        self.btn_stop = ctk.CTkButton(self, text="SHUTDOWN SERVER", command=self.stop, fg_color="#b71c1c", height=45)
        self.btn_stop.pack(pady=10, padx=60, fill="x")

        self.log_box = ctk.CTkTextbox(self, width=580, height=300, font=("Consolas", 12), fg_color="#111")
        self.log_box.pack(pady=20, padx=20)

    def create_input(self, placeholder, default_val):
        entry = ctk.CTkEntry(self.container, placeholder_text=placeholder, height=40)
        entry.insert(0, default_val)
        entry.pack(pady=5, fill="x")
        return entry

    def log(self, msg):
        # استخدام try لتجنب أخطاء الواجهة أثناء الإغلاق
        try:
            self.log_box.insert("end", f"» {time.strftime('%H:%M:%S')} | {msg}\n")
            self.log_box.see("end")
        except: pass

    def compress_data(self, data_bytes):
        """ضغط البيانات لتقليل حجم الطلب وسرعة الإرسال"""
        return base64.b64encode(zlib.compress(data_bytes)).decode()

    def decompress_data(self, b64_string):
        """فك ضغط البيانات المستلمة"""
        try:
            return zlib.decompress(base64.b64decode(b64_string))
        except:
            return None

    def safe_request(self, data):
        """إرسال الطلب مع معالجة التحويل التلقائي (Redirect)"""
        try:
            # استخدام مهلة قصيرة (Timeout) لضمان عدم تعليق البرنامج
            r = self.session.post(config.URL, json=data, timeout=8, allow_redirects=True)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            return None
        return None

    def stop(self):
        self.running = False
        self.log("System offline.")

    # --- HOST LOGIC ---
    def run_host(self):
        self.running = True
        self.log("Host Engine started (Optimized)...")
        threading.Thread(target=self.host_loop, daemon=True).start()

    def host_loop(self):
        group = self.entry_group.get()
        target_ip = self.entry_ip.get()
        target_port = int(self.entry_port.get())
        
        while self.running:
            # طلب البيانات القادمة من الـ Joiner
            res = self.safe_request({"role": "HOST", "group": group, "payload": ""})
            if res and res.get("data"):
                raw_payload = self.decompress_data(res.get("data"))
                if raw_payload:
                    # معالجة الاتصال بالهدف في خيط منفصل لزيادة السرعة
                    self.executor.submit(self.relay_to_target, raw_payload, group, target_ip, target_port)
            
            # تقليل وقت الانتظار جداً لزيادة التجاوب
            time.sleep(0.05)

    def relay_to_target(self, payload, group, ip, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                s.connect((ip, port))
                s.sendall(payload)
                reply = s.recv(1024 * 64) # 64KB Buffer
                if reply:
                    # إعادة الرد مضغوطاً
                    compressed_reply = self.compress_data(reply)
                    self.safe_request({"role": "HOST", "group": group, "payload": compressed_reply})
                    self.log(f"Relayed: {len(reply)} bytes")
        except: pass

    # --- JOINER LOGIC ---
    def run_join(self):
        self.running = True
        threading.Thread(target=self.join_listener, daemon=True).start()

    def join_listener(self):
        group = self.entry_group.get()
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind(('127.0.0.1', 0))
            server.listen(128)
            port = server.getsockname()[1]
            self.log(f"Joiner listening on Port: {port}")
        except Exception as e:
            self.log(f"Bind Error: {e}"); return

        while self.running:
            try:
                conn, addr = server.accept()
                self.executor.submit(self.process_client, conn, addr, group)
            except: continue

    def process_client(self, conn, addr, group):
        try:
            with conn:
                conn.settimeout(5)
                buffer = conn.recv(1024 * 64)
                if buffer:
                    payload = self.compress_data(buffer)
                    res = self.safe_request({"role": "JOINER", "group": group, "payload": payload})
                    if res and res.get("data"):
                        reply_data = self.decompress_data(res.get("data"))
                        if reply_data:
                            conn.sendall(reply_data)
                            self.log(f"Success: {addr[1]} | {len(reply_data)} bytes")
        except Exception as e:
            pass

if __name__ == "__main__":
    app = BayLakC2Bridge()
    app.mainloop()
