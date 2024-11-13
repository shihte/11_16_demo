import customtkinter as ctk
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import csv
import os
import webbrowser
import threading
import time
import logging
import sys
import traceback
import signal
import requests
from werkzeug.serving import make_server

# 設置日誌
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LwopanServer:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_routes()
        self.server = None
        self.server_thread = None
        self.is_running = False
        
    def get_resource_path(self, relative_path):
        try:
            if hasattr(sys, '_MEIPASS'):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.abspath(os.path.dirname(__file__))
            full_path = os.path.join(base_path, relative_path)
            return full_path
        except Exception as e:
            logger.error(f"Error getting resource path: {e}")
            return os.path.abspath(relative_path)

    def validate_id(self, id_str):
        try:
            id_num = int(id_str)
            return 1 <= id_num <= 184
        except ValueError:
            return False

    def opencsv(self, ID):
        try:
            file_path = os.path.join('happyread', f"Book_{ID}.csv")
            with open(file_path, "r", newline="", encoding="utf-8") as open_XID_csv:
                csv_reader = csv.reader(open_XID_csv)
                first_column = [row[0] for row in csv_reader]
                return first_column[1:]
        except Exception as e:
            logger.error(f"Error opening CSV: {e}")
            return []

    def search_in_book_all(self, question_numbers):
        results = []
        file_path = os.path.join('happyread', "book_all.csv")
        try:
            with open(file_path, "r", newline="", encoding="utf-8") as book_answer:
                csv_reader = list(csv.reader(book_answer))
                for number in question_numbers:
                    found = False
                    for row in csv_reader:
                        if row and row[0] == number:
                            answer = row[6] if row[6] else "未新增解答"
                            if answer != "未新增解答":
                                results.append({"question": row[1], "answer": answer})
                            found = True
                            break
                    if not found:
                        results.append({"question": f"題號 {number}", 
                                      "answer": "找不到相關題目，請檢查是否有錯字"})
        except Exception as e:
            logger.error(f"Error searching book_all: {e}")
            return [{"question": "錯誤", "answer": "找不到相關題目，請檢查是否有錯字"}]
        return results

    def search(self, text):
        results = []
        file_path = os.path.join('happyread', "book_all.csv")
        try:
            with open(file_path, "r", newline="", encoding="utf-8") as book_answer:
                csv_reader = list(csv.reader(book_answer))
                if text.isdigit():
                    found = False
                    for row in csv_reader:
                        if row and row[0] == text:
                            answer = row[6] if row[6] else "未新增解答"
                            if answer != "未新增解答":
                                results.append({"question": row[1], "answer": answer})
                            else:
                                results.append({"question": text, 
                                              "answer": "找不到相關題目，請檢查是否有錯字"})
                            found = True
                            break
                    if not found:
                        results.append({"question": text, 
                                      "answer": "找不到相關題目，請檢查是否有錯字"})
                else:
                    for row in csv_reader:
                        if row and text.lower() in row[1].lower():
                            answer = row[6] if row[6] else "未新增解答"
                            if answer != "未新增解答":
                                results.append({"question": row[1], "answer": answer})
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return [{"question": text, "answer": "找不到相關題目，請檢查是否有錯字"}]

        if not results:
            results.append({"question": text, "answer": "找不到相關題目，請檢查是否有錯字"})
        return results

    def process_input(self, Q):
        if Q.startswith("https://happyread.kh.edu.tw/"):
            if "id=" in Q:
                id_start = Q.index("id=") + 3
                id_value = Q[id_start:].split("&")[0]
                if self.validate_id(id_value):
                    question_numbers = self.opencsv(id_value)
                    if question_numbers:
                        results = self.search_in_book_all(question_numbers)
                        if not results or all(result["answer"] == "未新增解答" 
                                           for result in results):
                            return [{"question": Q, 
                                   "answer": "找不到相關題目，請檢查是否有錯字"}]
                        return results
            return [{"question": Q, "answer": "找不到相關題目，請檢查是否有錯字"}]
        else:
            return self.search(Q)

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return send_from_directory('.', 'index.html')

        @self.app.route('/script.js')
        def serve_script():
            return send_from_directory('.', 'script.js')

        @self.app.route('/search', methods=['POST'])
        def search_route():
            data = request.json
            question = data['question']
            results = self.process_input(question)
            return jsonify({'result': results})

        @self.app.route('/lwopan_logo.png')
        def serve_logo():
            return send_from_directory('.', 'lwopan_logo.png')

        @self.app.route('/404')
        def not_found():
            return send_from_directory('.', '404.html')

        @self.app.route('/how_to_codeing')
        def how_to_coding():
            return send_from_directory('.', 'how_to_codeing.html')

        @self.app.route('/<path:path>')
        def catch_all(path):
            if os.path.exists(path):
                return send_from_directory('.', path)
            else:
                return send_from_directory('.', '404.html'), 404

    def run_server_thread(self, host, port):
        self.server = make_server(host, port, self.app)
        self.is_running = True
        self.server.serve_forever()

    def start_server(self, host='127.0.0.1', port=5000):
        if not self.is_running:
            self.server_thread = threading.Thread(
                target=self.run_server_thread,
                args=(host, port)
            )
            self.server_thread.daemon = True
            self.server_thread.start()
            time.sleep(1)  # 等待伺服器啟動
            logger.info(f"Server started at http://{host}:{port}")
            return True
        return False

    def stop_server(self):
        if self.is_running and self.server:
            self.is_running = False
            self.server.shutdown()
            self.server = None
            if self.server_thread:
                self.server_thread.join(timeout=1)
            logger.info("Server stopped")
            return True
        return False

class ServerGUI:
    def __init__(self):
        self.server = LwopanServer()
        self.setup_gui()
        
    def setup_gui(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("lwopan Server Controller")
        self.root.geometry("400x600")
        
        title_frame = ctk.CTkFrame(self.root, corner_radius=0)
        title_frame.pack(fill="x", padx=20, pady=(20,10))
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="lwopan 伺服器控制台",
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=20)

        self.status_label = ctk.CTkLabel(
            title_frame,
            text="伺服器狀態: 已停止",
            font=("Arial", 14)
        )
        self.status_label.pack(pady=10)
        
        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.start_button = ctk.CTkButton(
            button_frame,
            text="啟動伺服器",
            command=self.start_server,
            font=("Arial", 14),
            height=40
        )
        self.start_button.pack(pady=20, padx=40, fill="x")
        
        self.open_button = ctk.CTkButton(
            button_frame,
            text="開啟網頁",
            command=self.open_browser,
            font=("Arial", 14),
            height=40,
            state="disabled"
        )
        self.open_button.pack(pady=20, padx=40, fill="x")
        
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="停止伺服器",
            command=self.stop_server,
            font=("Arial", 14),
            height=40,
            state="disabled"
        )
        self.stop_button.pack(pady=20, padx=40, fill="x")
        
        self.exit_button = ctk.CTkButton(
            button_frame,
            text="退出程式",
            command=self.exit_application,
            font=("Arial", 14),
            height=40,
            fg_color="#FF5252",
            hover_color="#FF1A1A"
        )
        self.exit_button.pack(pady=20, padx=40, fill="x")

        copyright_label = ctk.CTkLabel(
            self.root,
            text="© 2024 lwopan. All rights reserved.",
            font=("Arial", 12),
            text_color="gray"
        )
        copyright_label.pack(pady=10)

        # 設置關閉窗口的處理
        self.root.protocol("WM_DELETE_WINDOW", self.exit_application)

    def start_server(self):
        if self.server.start_server():
            self.status_label.configure(text="伺服器狀態: 運行中")
            self.start_button.configure(state="disabled")
            self.open_button.configure(state="normal")
            self.stop_button.configure(state="normal")
            logger.info("Server started successfully")

    def stop_server(self):
        if self.server.stop_server():
            self.status_label.configure(text="伺服器狀態: 已停止")
            self.start_button.configure(state="normal")
            self.open_button.configure(state="disabled")
            self.stop_button.configure(state="disabled")
            logger.info("Server stopped successfully")

    def open_browser(self):
        webbrowser.open('http://127.0.0.1:5000')
        logger.info("Browser opened")

    def exit_application(self):
        if self.server.is_running:
            self.stop_server()
        self.root.quit()
        self.root.destroy()
        os._exit(0)  # 強制結束所有線程

    def run(self):
        self.root.mainloop()

def main():
    try:
        app = ServerGUI()
        app.run()
    except Exception as e:
        # 保存錯誤信息到文件
        with open('error_log.txt', 'w') as f:
            f.write(f"Error: {str(e)}\n")
            f.write(traceback.format_exc())
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # 保存錯誤信息到文件
        with open('error_log.txt', 'w') as f:
            f.write(f"Critical Error: {str(e)}\n")
            f.write(traceback.format_exc())
        sys.exit()