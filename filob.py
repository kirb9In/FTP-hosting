import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from android.storage import primary_external_storage_path
import threading

class FTPServerApp(App):
    def build(self):
        self.server = None
        self.ftp_username = "admin"
        self.ftp_password = "12345"
        self.selected_folders = []
        
        # Автоматически создаем папку по умолчанию
        default_folder = os.path.join(primary_external_storage_path(), "FTPServer")
        os.makedirs(default_folder, exist_ok=True)
        self.selected_folders.append(default_folder)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.status_label = Label(text="FTP-сервер готов к запуску")
        
        self.username_input = TextInput(hint_text="Логин", text=self.ftp_username)
        self.password_input = TextInput(hint_text="Пароль", text=self.ftp_password, password=True)
        
        btn_choose = Button(text="Выбрать папки")
        btn_choose.bind(on_press=self.show_folder_chooser)
        
        self.btn_toggle = Button(text="Запустить FTP-сервер")
        self.btn_toggle.bind(on_press=self.toggle_server)
        
        layout.add_widget(self.status_label)
        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(btn_choose)
        layout.add_widget(self.btn_toggle)
        
        return layout
    
    def show_folder_chooser(self, instance):
        content = BoxLayout(orientation='vertical')
        file_chooser = FileChooserListView(
            dirselect=True,
            multiselect=True,
            path=primary_external_storage_path()
        )
        content.add_widget(file_chooser)
        
        popup = Popup(title="Выберите папки (удерживайте для множественного выбора)", 
                     content=content, 
                     size_hint=(0.9, 0.9))
        
        def select_folders(btn):
            if file_chooser.selection:
                self.selected_folders = file_chooser.selection
                self.status_label.text = f"Выбрано папок: {len(self.selected_folders)}"
            popup.dismiss()
        
        btn_select = Button(text="Подтвердить", size_hint=(1, 0.1))
        btn_select.bind(on_press=select_folders)
        content.add_widget(btn_select)
        
        popup.open()
    
    def toggle_server(self, instance):
        if self.server:
            self.stop_server()
        else:
            self.start_server()
    
    def start_server(self):
        if not self.selected_folders:
            self.status_label.text = "Ошибка: не выбрано ни одной папки!"
            return
            
        self.ftp_username = self.username_input.text.strip() or "admin"
        self.ftp_password = self.password_input.text.strip() or "12345"
        
        try:
            authorizer = DummyAuthorizer()
            
            # Создаем главного пользователя с доступом ко всем папкам
            authorizer.add_user(
                username=self.ftp_username,
                password=self.ftp_password,
                homedir=self.selected_folders[0],  # Первая папка как домашняя
                perm="elradfmw"
            )
            
            # Для остальных папок создаем символические ссылки в домашней папке
            home_dir = self.selected_folders[0]
            for i, folder in enumerate(self.selected_folders[1:]):
                link_name = os.path.join(home_dir, f"folder_{i}")
                if not os.path.exists(link_name):
                    os.symlink(folder, link_name)
            
            handler = FTPHandler
            handler.authorizer = authorizer
            
            self.server = FTPServer(("0.0.0.0", 2221), handler)
            self.status_label.text = (
                f"FTP-сервер запущен\n"
                f"Доступно папок: {len(self.selected_folders)}\n"
                f"IP: {self.get_local_ip()}:2221\n"
                f"Логин: {self.ftp_username}\n"
                f"Пароль: {self.ftp_password}"
            )
            self.btn_toggle.text = "Остановить сервер"
            
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            
        except Exception as e:
            self.status_label.text = f"Ошибка: {str(e)}"
            if "already exists" in str(e):
                self.status_label.text += "\nЗакройте сервер и попробуйте снова"
    
    def stop_server(self):
        if self.server:
            self.server.close_all()
            self.server = None
            # Удаляем временные ссылки
            home_dir = self.selected_folders[0] if self.selected_folders else ""
            if home_dir:
                for item in os.listdir(home_dir):
                    if item.startswith("folder_"):
                        os.remove(os.path.join(home_dir, item))
            self.status_label.text = "FTP-сервер остановлен"
            self.btn_toggle.text = "Запустить FTP-сервер"
    
    def get_local_ip(self):
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

if __name__ == "__main__":
    FTPServerApp().run()