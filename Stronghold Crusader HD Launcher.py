###=============================================================###
# Программа: Stronghold Crusader HD Launcher (SCHDL)
# Версия: 1.0.0 (Stable)
# © AntonS2000 (MA Foundation) 2025
# Дата последней компиляции: 11.08.2025
# Лицензия: MA Foundation Original License
# Язык: Python 3.13
# Библиотеки: PyQt6, psutil, json, subprocess, pathlib
# Требования: Stronghold Crusader HD v1.3, DXWnd, AutoHotkey v2.0.0
# Описание: Лаунчер для игры Stronghold Crusader HD (Portable)
#           с возможностью запуска DXWnd и патча AutoHotkey.
#           Позволяет как-либо управлять процессами игры и её
#           вспомогательными утилитами – запускать и завершать их.
#           Графический интерфейс построен с помощью библиотеки
#           PyQt6, поддерживает смену тем и контроль всплывающих
#           информационных сообщений.
###=============================================================###

import sys
import json
import subprocess
import psutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLabel, QSpacerItem,
    QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt, QProcess, QCoreApplication
from PyQt6.QtGui import QPalette, QColor, QIcon

# === Настройки ===
APP_NAME = "Stronghold Crusader HD Launcher"
SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "theme": "light",
    "messages": "disabled",
    "last_run": "✅ Всё вместе",
    "last_close": "🚀 Лаунчер + 💊Патч"
}
ICON_FILE = "gameicon.ico"  # относительный путь к иконке
# Определяем базовую директорию (где находится Stronghold Crusader HD Launcher.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Пути к исполняемым файлам (относительно корня игры)
DXWND_EXE = BASE_DIR / "DXWnd" / "dxwnd.exe"         # Лаунчер DXWnd
PATCH_EXE = BASE_DIR / "HKPatch" / "HKPatch.exe"     # Патч AutoHotkey v2.0.0

def load_theme():
    return load_settings().get("theme", "light")

def save_theme(theme):
    save_setting("theme", theme)

def load_settings():
    settings_path = Path(SETTINGS_FILE)
    if settings_path.exists():
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⛔ Ошибка чтения settings.json: {e}")
    else:
        # Автосоздание при первом запуске
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_SETTINGS, f, ensure_ascii=False, indent=2)
    return DEFAULT_SETTINGS.copy()

def save_setting(key, value):
    settings = load_settings()
    settings[key] = value
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

SETTINGS = load_settings()

def apply_theme(app, theme):
    if theme == "dark":
        app.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        app.setPalette(palette)
    else:
        app.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 100, 200))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 100, 200))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        app.setPalette(palette)


def restart_app():
    QCoreApplication.quit()
    subprocess.Popen([sys.executable] + sys.argv)
    sys.exit()

def show_message(title, text, icon=QMessageBox.Icon.Information):
    if load_settings().get("messages", "enabled") == "enabled":
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(icon)
        msg.setWindowIcon(QIcon(str(Path(__file__).parent / ICON_FILE))) # Устанавливаем иконку SCHDL
        # msg.setWindowIcon(QIcon(str(Path(ICON_FILE)))) # Устанавливаем иконку SCHDL
        msg.exec()
        
class MainLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setFixedSize(450, 300)  # фиксированный размер окна
        self.setWindowIcon(self.load_icon())
        self.init_ui()

    def load_icon(self):
        icon_path = Path(ICON_FILE)  # относительный путь к иконке
        if not icon_path.is_absolute():
            icon_path = Path(__file__).parent / icon_path  # ищем в папке SCHDL
        if icon_path.exists():
            return QIcon(str(icon_path))
        return QIcon()  # пустая иконка
        
    def toggle_messages(self):
        current = load_settings().get("messages", "enabled")
        new_value = "disabled" if current == "enabled" else "enabled"
        save_setting("messages", new_value)
        self.msg_btn.setText("❌ Всплывающие сообщения" if new_value == "enabled" else "✅ Всплывающие сообщения")

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Заголовок с иконкой (по центру)
        header_container = QHBoxLayout()
        header_container.addStretch()  # растягиваем слева

        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)  # расстояние между иконкой и текстом
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Иконка
        icon_label = QLabel()
        icon_path = Path(__file__).parent / ICON_FILE
        if icon_path.exists():
            from PyQt6.QtGui import QPixmap
            pixmap = QPixmap(str(icon_path))
            if not pixmap.isNull():
                pixmap = pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(pixmap)
            else:
                icon_label.setText("🎮")
                icon_label.setStyleSheet("font-size: 32px;")
        else:
            icon_label.setText("🎮")
            icon_label.setStyleSheet("font-size: 32px;")

        # Текст
        title = QLabel("Stronghold Crusader HD Launcher")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Добавляем в внутренний layout
        header_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Вставляем внутренний layout в контейнер
        header_container.addLayout(header_layout)
        header_container.addStretch()  # растягиваем справа

        layout.addSpacing(10)  # отступ сверху
        layout.addLayout(header_container)

        # Строка: кнопка темы + кнопка всплывающих окон
        theme_row = QHBoxLayout()

        # Кнопка смены темы
        current_theme = load_theme()
        self.theme_btn = QPushButton("☀️ Светлая тема" if current_theme == "dark" else "🌑 Тёмная тема")
        self.theme_btn.setToolTip("Изменяет тему программы")
        self.theme_btn.clicked.connect(self.toggle_theme)

        # Кнопка всплывающих окон
        msg_state = load_settings().get("messages", "enabled")
        self.msg_btn = QPushButton("❌ Всплывающие сообщения" if msg_state == "enabled" else "✅ Всплывающие сообщения")
        self.msg_btn.setToolTip("Включает/отключает информационные сообщения")
        self.msg_btn.clicked.connect(self.toggle_messages)

        theme_row.addWidget(self.theme_btn)
        theme_row.addWidget(self.msg_btn)

        layout.addLayout(theme_row)
        layout.addSpacing(15)
        
        # Выпадающий список: что запустить
        self.combo_run = QComboBox()
        self.combo_run.addItems([
            "🚀 Лаунчер DXWnd",
            "💊 Патч WASD",
            "✅ Всё вместе"
        ])

        # Восстанавливаем последний выбор
        last_run = load_settings().get("last_run", "🚀 Лаунчер DXWnd")
        index = self.combo_run.findText(last_run)
        if index >= 0:
            self.combo_run.setCurrentIndex(index)

        layout.addWidget(QLabel("🙂 Что запустить будем?"))
        layout.addWidget(self.combo_run)

        # Кнопка "Запустить"
        self.btn_run = QPushButton("▶️ Запустить")
        self.btn_run.setToolTip("Запускает выбранные из верхнего списка программы")
        self.btn_run.clicked.connect(self.run_selected)
        layout.addWidget(self.btn_run)
        layout.addSpacing(15)

        # Третья строка: выпадающий список
        self.combo_close = QComboBox()
        self.combo_close.addItems([
            "🚀 Лаунчер DXWnd",
            "💊 Патч WASD",
            "🚀 Лаунчер + 💊Патч",
            "➡️ Только SCHDL",
            "✅ Все процессы"
        ])

        # Восстанавливаем последний выбор
        last_close = load_settings().get("last_close", "🚀 Лаункер DXWnd")
        index = self.combo_close.findText(last_close)
        if index >= 0:
            self.combo_close.setCurrentIndex(index)

        layout.addSpacing(5)
        layout.addWidget(QLabel("💁‍♂️ Выберите процессы для завершения:"))
        layout.addWidget(self.combo_close)

        # Четвёртая строка: кнопка "Закрыть"
        self.btn_close = QPushButton("⚠️ Завершить выбранные процессы")
        self.btn_close.setToolTip("Завершает выбранные из верхнего списка процессы")
        self.btn_close.clicked.connect(self.close_selected)
        layout.addWidget(self.btn_close)

        # Подключаем обновление текста кнопки при изменении выбора
        self.combo_close.currentTextChanged.connect(self.update_close_button_text)
        self.update_close_button_text()  # Установить начальный текст

        # Сохраняем при изменении выбора
        self.combo_run.currentTextChanged.connect(self.save_last_run)
        self.combo_close.currentTextChanged.connect(self.save_last_close)

        # Отступ вниз
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(layout)

    def update_close_button_text(self):
        text = self.combo_close.currentText()
        if text in ["🚀 Лаунчер DXWnd", "💊 Патч WASD", "➡️ Только SCHDL"]:
            self.btn_close.setText("⚠️ Закрыть выбранный процесс")
        else:
            self.btn_close.setText("⚠️ Закрыть выбранные процессы")

    def save_last_run(self, text):
        save_setting("last_run", text)

    def save_last_close(self, text):
        save_setting("last_close", text)

    def toggle_theme(self):
        current_theme = load_theme()
        new_theme = "light" if current_theme == "dark" else "dark"
        save_theme(new_theme)
        restart_app()

    @staticmethod
    def is_process_running(process_name):
        """Проверяет, запущен ли процесс по имени исполняемого файла"""
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() == process_name.lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def is_running(self, key):
        exe_map = {
            "dxwnd": "dxwnd.exe",
            "patch": "HKPatch.exe"
        }
        if key in exe_map:
            return self.is_process_running(exe_map[key])
        return False

    def start_dxwnd(self):
        if self.is_process_running("dxwnd.exe"):
            show_message("Уже запущен", "👌 Лаунчер DXWnd уже запущен!", QMessageBox.Icon.Information)
            return
        if not DXWND_EXE.exists():
            show_message("Ошибка", f"🚫 Файл не найден:\n{DXWND_EXE}", QMessageBox.Icon.Critical)
            return
        # Запускаем отдельно — не будет привязан к SCHDL
        if QProcess.startDetached(str(DXWND_EXE)):
            show_message("Запущен", f"🚀 Лаунчер DXWnd запущен:\n{DXWND_EXE}", QMessageBox.Icon.Information)
        else:
            show_message("Ошибка", f"❌ Не удалось запустить DXWnd:\n{DXWND_EXE}", QMessageBox.Icon.Critical)
        
    def start_patch(self):
        if self.is_process_running("HKPatch.exe"):
            show_message("Уже запущен", "👌 Патч AutoHotkey v2.0.0 уже запущен!", QMessageBox.Icon.Information)
            return
        if not PATCH_EXE.exists():
            show_message("Ошибка", f"🚫 Файл не найден:\n{PATCH_EXE}", QMessageBox.Icon.Critical)
            return
        # Запускаем отдельно — не будет привязан к SCHDL
        if QProcess.startDetached(str(PATCH_EXE)):
            show_message("Запущен", f"🚀 Патч запущен:\n{PATCH_EXE}", QMessageBox.Icon.Information)
        else:
            show_message("Ошибка", f"❌ Не удалось запустить патч:\n{PATCH_EXE}", QMessageBox.Icon.Critical)

    def run_all(self):
        launched = []
        if not self.is_running("dxwnd") and DXWND_EXE.exists():
            self.start_dxwnd()
            launched.append("Лаунчер DXWnd")
        elif self.is_running("dxwnd"):
            launched.append("Лаунчер DXWnd (уже запущен)")
        elif not DXWND_EXE.exists():
            show_message("Ошибка", f"😨 Лаунчер DXWnd не найден:\n{DXWND_EXE}", QMessageBox.Icon.Warning)

        if not self.is_running("patch") and PATCH_EXE.exists():
            self.start_patch()
            launched.append("Патч AutoHotkey v2.0.0")
        elif self.is_running("patch"):
            launched.append("Патч AutoHotkey v2.0.0 (уже запущен)")
        elif not PATCH_EXE.exists():
            show_message("Ошибка", f"😨 Патч не найден:\n{PATCH_EXE}", QMessageBox.Icon.Warning)

        if launched:
            show_message("Запущено", "👉 Результат запуска:\n" + "\n".join(f"• {item}" for item in launched), QMessageBox.Icon.Information)
        else:
            show_message("Информация", "🤷‍♂️ Нечего запускать.", QMessageBox.Icon.Information)

    def on_process_error(self, name, error):
        print(f"🚫 Ошибка {name}: {error}")
        # Можно показать предупреждение, но не обязательно

    def run_selected(self):
        selection = self.combo_run.currentText()

        if selection == "🚀 Лаунчер DXWnd":
            self.start_dxwnd()
        elif selection == "💊 Патч WASD":
            self.start_patch()
        elif selection == "✅ Всё вместе":
            self.run_all()

    def close_selected(self):
        selection = self.combo_close.currentText()
        closed = []

        def terminate_by_name(process_name, friendly_name):
            found = False
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() == process_name.lower():
                        proc.terminate()
                        try:
                            proc.wait(timeout=3)  # ждём 3 секунды
                            closed.append(friendly_name)
                        except psutil.TimeoutExpired:
                            proc.kill()
                            closed.append(f"{friendly_name} (принудительно)")
                        found = True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            if not found:
                pass  # можно добавить в будущем в лог, но не обязательно

        if selection == "🚀 Лаунчер DXWnd":
            terminate_by_name("dxwnd.exe", "Лаунчер DXWnd")
        elif selection == "💊 Патч WASD":
            terminate_by_name("HKPatch.exe", "Патч AutoHotkey v2.0.0")
        elif selection == "🚀 Лаунчер + 💊Патч":
            terminate_by_name("dxwnd.exe", "Лаунчер DXWnd")
            terminate_by_name("HKPatch.exe", "Патч AutoHotkey v2.0.0")
        elif selection == "➡️ Только SCHDL":
            reply = QMessageBox.question(
                self, "Подтверждение",
                "⚠️ Закрыть SCHDL?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            ) if load_settings().get("messages", "enabled") == "enabled" else QMessageBox.StandardButton.Yes
            if reply == QMessageBox.StandardButton.Yes:
                self.close()
        elif selection == "✅ Все процессы":
            terminate_by_name("dxwnd.exe", "Лаунчер DXWnd")
            terminate_by_name("HKPatch.exe", "Патч AutoHotkey v2.0.0")
            reply = QMessageBox.question(
                self, "Подтверждение",
                "⚠️ Закрыть и SCHDL?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            ) if load_settings().get("messages", "enabled") == "enabled" else QMessageBox.StandardButton.Yes
            if reply == QMessageBox.StandardButton.Yes:
                self.close()

        if closed:
            show_message("Завершение", "✅ Были закрыты:\n" + "\n".join(f"• {item}" for item in closed), QMessageBox.Icon.Information)
        elif selection not in ["➡️ Только SCHDL", "✅ Всё вместе"]:
            show_message("Информация", "🤷‍♂️ Нет активных процессов для закрытия.", QMessageBox.Icon.Information)

def closeEvent(self, event):
    event.accept()          # SCHDL закрывается — но не трогает другие процессы

def main():
    app = QApplication(sys.argv)

    # Применяем тему
    theme = load_theme()
    apply_theme(app, theme)

    window = MainLauncher()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()