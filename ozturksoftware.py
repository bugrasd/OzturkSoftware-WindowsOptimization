import sys, os, shutil, subprocess, ctypes
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QCheckBox, QMessageBox, QHBoxLayout, QToolButton, QScrollArea
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt6.QtGui import QPainter, QPen, QColor, QCursor

DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
BACKUP_FILE = os.path.join(DESKTOP_PATH, "ozturk_software_backup.reg")

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

def create_backup(keys_to_backup):
    try:
        if os.path.exists(BACKUP_FILE): os.remove(BACKUP_FILE)
        with open(BACKUP_FILE, "w") as backup_file:
            for key in keys_to_backup:
                subprocess.run(f'reg export "{key}" "{BACKUP_FILE}" /y', shell=True, capture_output=True)
        return True
    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Yedekleme oluşturulamadı: {e}")
        return False

def restore_from_backup():
    if os.path.exists(BACKUP_FILE):
        try:
            result = subprocess.run(f'reg import "{BACKUP_FILE}"', shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                QMessageBox.information(None, "Başarılı", "Ayarlar başarıyla geri yüklendi!")
                os.remove(BACKUP_FILE)
            else:
                QMessageBox.critical(None, "Hata", f"Ayarlar geri yüklenemedi.\nHata: {result.stderr}")
        except Exception as e:
            QMessageBox.critical(None, "Hata", f"Geri yükleme sırasında bir hata oluştu: {e}")
    else:
        QMessageBox.warning(None, "Bilgi", "Geri yüklenecek bir yedek dosyası bulunamadı.")

def execute_reg_command(command):
    try: subprocess.run(command, shell=True, check=True, capture_output=True)
    except subprocess.CalledProcessError as e: print(f"Kayıt defteri hatası: {e.stderr.decode('cp857', errors='ignore')}")

def optimize_display():
    cmds = [
        'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v AppsUseLightTheme /t REG_DWORD /d 0 /f',
        'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v SystemUsesLightTheme /t REG_DWORD /d 0 /f',
        'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Lock Screen" /v LockScreenImage /t REG_SZ /d "" /f', 
        'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" /v DisableLogonBackgroundImage /t REG_DWORD /d 1 /f'
    ]
    for cmd in cmds: execute_reg_command(cmd)

def optimize_windows_features():
    cmds = [
        'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v Start_ShowRecentlyAddedApps /t REG_DWORD /d 0 /f',
        'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" /v SubscribedContent-338388Enabled /t REG_DWORD /d 0 /f',
        'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v Start_TrackProgs /t REG_DWORD /d 0 /f',
        'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v TaskbarSmallIcons /t REG_DWORD /d 1 /f'
    ]
    for cmd in cmds: execute_reg_command(cmd)

def optimize_privacy():
    cmds = [
        'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\FocusAssist" /v FocusAssistLevel /t REG_DWORD /d 0 /f',
        'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo" /v Enabled /t REG_DWORD /d 0 /f',
        'reg add "HKCU\\Software\\Microsoft\\Input\\TIPC" /v Enabled /t REG_DWORD /d 0 /f',
        'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f',
        'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" /v PublishUserActivities /t REG_DWORD /d 0 /f'
    ]
    for cmd in cmds: execute_reg_command(cmd)

def optimize_power():
    subprocess.run('powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61', shell=True, capture_output=True)
    subprocess.run('powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c', shell=True, capture_output=True)

def optimize_registry():
    reg_file_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "ozturksoftware.reg")
    if not os.path.exists(reg_file_path):
        QMessageBox.critical(None, "Dosya Bulunamadı", "'ozturksoftware.reg' dosyası bulunamadı!")
        return
    try: subprocess.run(f'reg import "{reg_file_path}"', shell=True, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e: QMessageBox.critical(None, "Hata", f"Registry tweak uygulanamadı:\n{e.stderr}")
    except Exception as e: QMessageBox.critical(None, "Hata", f"Beklenmedik hata: {e}")

def clean_temp_files():
    folders = [
        os.environ.get('TEMP'),
        os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp'),
        os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Prefetch'),
        os.path.join(os.path.expanduser('~'), 'AppData\\Roaming\\Microsoft\\Windows\\Recent')
    ]
    for folder in folders:
        if folder and os.path.exists(folder):
            for item in os.listdir(folder):
                path = os.path.join(folder, item)
                try:
                    if os.path.isfile(path) or os.path.islink(path): os.unlink(path)
                    elif os.path.isdir(path): shutil.rmtree(path)
                except: pass

class CircularLoader(QWidget):
    def __init__(self, diameter=120):
        super().__init__()
        self.diameter = diameter
        self.setFixedSize(diameter, diameter)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_angle)
        self.timer.start(16)

    def update_angle(self):
        self.angle = (self.angle + 6) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(8, 8, -8, -8)
        painter.setPen(QPen(QColor(50, 50, 50), 10))
        painter.drawEllipse(rect)
        pen_fg = QPen(QColor(79, 195, 247), 10)
        pen_fg.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_fg)
        painter.drawArc(rect, self.angle * 16, 120 * 16)

class Loader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Öztürk Software - Yükleniyor')
        self.setFixedSize(400, 250)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("#mainWidget {background-color: #121212; border-radius: 20px;}")
        self.main_widget = QWidget(self)
        self.main_widget.setObjectName("mainWidget")
        self.main_widget.setGeometry(0, 0, 400, 250)
        layout = QVBoxLayout(self.main_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loader = CircularLoader(120)
        layout.addWidget(self.loader, alignment=Qt.AlignmentFlag.AlignCenter)
        self.status_label = QLabel("Uygulama güncellemesi kontrol ediliyor...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: white; font-size: 14px; padding-top: 10px;")
        layout.addWidget(self.status_label)
        self.setWindowOpacity(0)
        self.anim_opacity = QPropertyAnimation(self, b'windowOpacity')
        self.anim_opacity.setDuration(600)
        self.anim_opacity.setStartValue(0)
        self.anim_opacity.setEndValue(1)
        self.anim_opacity.start()
        QTimer.singleShot(2000, lambda: self.status_label.setText("Uygulama başlatılıyor..."))
        QTimer.singleShot(5000, self.open_main)

    def open_main(self):
        self.main = MainApp()
        self.main.show()
        self.close()

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Öztürk Software - FPS Optimize')
        self.setFixedSize(700, 650)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.oldPos = self.pos()
        self.dark_mode = True
        self.main_widget = QWidget(self)
        self.main_widget.setObjectName("mainWidget")
        self.main_widget.setGeometry(0, 0, 700, 650)
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(0, 0, 0, 15)
        layout.setSpacing(5)

        self.header = QWidget()
        self.header.setFixedHeight(35)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(10, 0, 10, 0)
        header_layout.setSpacing(10)
        self.close_btn = QPushButton('')
        self.close_btn.setFixedSize(15, 15)
        self.close_btn.setStyleSheet('background-color: #ff5f57; border-radius: 7px; border: none;')
        self.close_btn.clicked.connect(self.close)
        self.min_btn = QPushButton('')
        self.min_btn.setFixedSize(15, 15)
        self.min_btn.setStyleSheet('background-color: #ffbd2e; border-radius: 7px; border: none;')
        self.min_btn.clicked.connect(self.showMinimized)
        header_layout.addWidget(self.close_btn)
        header_layout.addWidget(self.min_btn)
        header_layout.addStretch()
        self.theme_btn = QPushButton('🌙')
        self.theme_btn.setFixedSize(40, 20)
        self.theme_btn.clicked.connect(lambda: self.toggle_theme())
        header_layout.addWidget(self.theme_btn)
        layout.addWidget(self.header)

        self.title = QLabel('Öztürk Software FPS Optimize')
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet('font-size: 24px; font-weight: bold; padding: 10px;')
        layout.addWidget(self.title)

        self.checks = []
        self.options = [
    ('Görüntü Ayarlarını Optimize Et', 'Sistem genelinde koyu temayı etkinleştirir, arkaplan ayarlarını optimize eder.', optimize_display, ['HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize', 'HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System']),
    ('Animasyonları Kapat', 'Windows animasyonlarını ve görsel efektleri kapatarak performansı artırır.', lambda: execute_reg_command('reg add "HKCU\\Control Panel\\Desktop\\WindowMetrics" /v MinAnimate /t REG_SZ /d 0 /f'), ['HKCU\\Control Panel\\Desktop']),
    ('Masaüstü İpuçlarını Kapat', 'Masaüstü ipuçlarını kapatarak sistem tepkisini hızlandırır.', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v ShowInfoTip /t REG_DWORD /d 0 /f'), ['HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced']),
    ('Görev Çubuğu Şeffaflığını Kapat', 'Görev çubuğu transparanlığını kapatarak performansı artırır.', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v EnableTransparency /t REG_DWORD /d 0 /f'), ['HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize']),
    ('Başlat Menüsü Arkaplanını Basitleştir', 'Başlat menüsünü daha sade ve hızlı hale getirir.', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v Start_ShowClassicMode /t REG_DWORD /d 1 /f'), ['HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced']),
    
    ('Başlat Menüsü Önerilerini Kapat', 'Başlat menüsünde önerileri ve reklamları devre dışı bırakır.', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" /v SystemPaneSuggestionsEnabled /t REG_DWORD /d 0 /f'), ['HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager']),
    ('Görev Çubuğu Küçük İkonlar', 'Görev çubuğunu daha kompakt hale getirir.', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v TaskbarSmallIcons /t REG_DWORD /d 1 /f'), ['HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced']),
    ('Hızlı Başlat Menüsü', 'Başlat menüsünde son kullanılan uygulamaları gösterme.', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v Start_TrackProgs /t REG_DWORD /d 0 /f'), ['HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced']),
    ('Görev Çubuğu Otomatik Gizle', 'Görev çubuğunu oyun veya uygulama sırasında otomatik gizler.', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\StuckRects3" /v Settings /t REG_BINARY /d 0300000003000000 /f'), ['HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\StuckRects3']),
    ('Hızlı Başlat Klasörünü Temizle', 'Başlat menüsünü gereksiz ikonlardan temizler.', lambda: execute_reg_command('del /q/f/s "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\*"'), []),

    ('Telemetri ve Veri Toplamayı Kapat', 'Microsoft veri toplama ve telemetri özelliklerini kapatır.', optimize_privacy, ['HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection']),
    ('Odaklanma Modunu Aç', 'Bildirimleri kapatarak oyun ve uygulama performansını artırır.', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\FocusAssist" /v FocusAssistLevel /t REG_DWORD /d 2 /f'), ['HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\FocusAssist']),
    ('Reklam Kimliği Kapat', 'Uygulamaların reklam kimliğini kullanmasını engeller.', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo" /v Enabled /t REG_DWORD /d 0 /f'), ['HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo']),
    ('Uygulama Arka Planını Kapat', 'Arka planda çalışan uygulamaları kapatarak RAM tasarrufu sağlar.', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications" /v GlobalUserDisabled /t REG_DWORD /d 1 /f'), ['HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications']),
    ('Konum Servisini Kapat', 'Konum tabanlı hizmetleri kapatarak gizliliği artırır.', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Location" /v Status /t REG_DWORD /d 0 /f'), ['HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Location']),

    ('Güç Modunu Nihai Performansa Al', 'Tüm CPU çekirdeklerini maksimum performans için açar.', optimize_power, []),
    ('Hızlı Başlatmayı Kapat', 'Windows hızlı başlat özelliğini kapatarak bazı hataları ve gecikmeleri önler.', lambda: execute_reg_command('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power" /v HiberbootEnabled /t REG_DWORD /d 0 /f'), ['HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power']),
    ('Görsel Efektleri Minimuma Al', 'Performans için tüm görsel efektleri kapatır.', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f'), ['HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects']),
    ('SSD için TRIM Aç', 'SSD performansını korumak için TRIM komutunu etkinleştirir.', lambda: subprocess.run('fsutil behavior set DisableDeleteNotify 0', shell=True), []),
    
    ('Registry İyileştirmesi', 'Sistem performansını artırmak için kayıt defteri tweakleri uygular.', optimize_registry, ['HKLM\\SYSTEM\\CurrentControlSet\\Control', 'HKCU\\Control Panel\\Desktop']),

    ('Geçici Dosyaları Temizle', 'Windows ve uygulamaların oluşturduğu gereksiz dosyaları temizler.', clean_temp_files, []),
    ('Prefetch Dosyalarını Temizle', 'Başlangıç performansını artırmak için prefetch klasörünü temizler.', lambda: execute_reg_command('del /q/f/s %systemroot%\\Prefetch\\*'), []),
    ('Geri Dönüşüm Kutusunu Boşalt', 'Disk alanını artırır.', lambda: execute_reg_command('powershell.exe -NoProfile -Command "Clear-RecycleBin -Force"'), []),
    ('DNS Önbelleğini Temizle', 'İnternet bağlantısı ve hız sorunlarını azaltır.', lambda: subprocess.run('ipconfig /flushdns', shell=True), []),
    ('Windows Update Geçmişini Temizle', 'Güncelleme önbelleğini temizler ve hata olasılığını azaltır.', lambda: execute_reg_command('net stop wuauserv && del /q /f /s %windir%\\SoftwareDistribution\\* && net start wuauserv'), []),
    ('Log Dosyalarını Temizle', 'Sistem log dosyalarını temizler.', lambda: execute_reg_command('del /q/f/s %systemroot%\\System32\\winevt\\Logs\\*'), []),

    ('TCP/IP Ayarlarını Optimize Et', 'Ağ gecikmelerini azaltır.', lambda: execute_reg_command('netsh int tcp set global autotuninglevel=normal'), []),
    ('Windows Firewall Kurallarını Sadeleştir', 'Gereksiz firewall kurallarını kapatır.', lambda: execute_reg_command('netsh advfirewall reset'), []),
    ('Arka Plan Ağ Hizmetlerini Kapat', 'Oyun sırasında internet hızını artırır.', lambda: execute_reg_command('net stop "WLAN AutoConfig"'), []),
    
    ('Oyun Modunu Aç', 'Windows oyun modunu etkinleştirir.', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\GameBar" /v AllowAutoGameMode /t REG_DWORD /d 1 /f'), ['HKCU\\Software\\Microsoft\\GameBar']),
    ('Arka Plan Hizmetlerini Kapat', 'Oyun sırasında gereksiz hizmetleri kapatarak performansı artırır.', lambda: execute_reg_command('powershell.exe -NoProfile -Command "Stop-Service -Name \"DiagTrack\" -Force"'), []),
    ('GameDVR Kapat', 'Oyun kaydı ve performans azaltıcı özellikleri kapatır.', lambda: execute_reg_command('reg add "HKCU\\System\\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 0 /f'), ['HKCU\\System\\GameConfigStore']),
    ('GPU Scheduling Optimize Et', 'Yeni nesil GPU planlamayı etkinleştirir.', lambda: execute_reg_command('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers" /v HwSchMode /t REG_DWORD /d 2 /f'), ['HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers']),
        ]
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")
        layout.addWidget(scroll_area)

        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(5)

        for name, info_text, _, _ in self.options:
            hbox = QHBoxLayout()
            hbox.setContentsMargins(20, 0, 20, 0)
            cb = QCheckBox(name)
            self.checks.append(cb)
            hbox.addWidget(cb)
            info_btn = QToolButton()
            info_btn.setText('ℹ️')
            info_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            info_btn.setToolTip(info_text)
            info_btn.clicked.connect(lambda _, t=info_text: QMessageBox.information(self, 'Bilgi', t))
            hbox.addWidget(info_btn)
            hbox.addStretch()
            scroll_layout.addLayout(hbox)

        layout.addStretch()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 10, 20, 10)
        self.restore_button = QPushButton('Ayarları Geri Al')
        self.restore_button.clicked.connect(restore_from_backup)
        button_layout.addWidget(self.restore_button, 1)
        self.apply_button = QPushButton('Seçilen Özellikleri Uygula')
        self.apply_button.clicked.connect(self.apply_selected)
        button_layout.addWidget(self.apply_button, 2)
        layout.addLayout(button_layout)
        self.toggle_theme(init=True)

    def apply_selected(self):
        selected_funcs = []
        keys_to_backup = set()
        for i, cb in enumerate(self.checks):
            if cb.isChecked():
                selected_funcs.append(self.options[i][2])
                keys_to_backup.update(self.options[i][3])
        if not selected_funcs:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen uygulamak için en az bir özellik seçin!')
            return
        reply = QMessageBox.question(self, 'Onay', 'Seçilen optimizasyonlar uygulanacak. Devam etmeden önce mevcut ayarlarınız yedeklenecektir. Onaylıyor musunuz?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if create_backup(list(keys_to_backup)):
                for func in selected_funcs: func()
                QMessageBox.information(self, 'Başarılı', 'Seçilen optimizasyon işlemleri tamamlandı!')
            else:
                QMessageBox.critical(self, 'Hata', 'Ayarlar yedeklenemediği için işlem iptal edildi.')

    def toggle_theme(self, init=False):
        if not init: self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.main_widget.setStyleSheet("#mainWidget {background-color: #f0f0f0; color: black; border-radius: 20px;}")
            self.header.setStyleSheet('background-color: #e0e0e0; border-top-left-radius: 20px; border-top-right-radius: 20px;')
            checkbox_style = 'QCheckBox {font-size:14px; padding:8px; color: black;} QCheckBox::indicator {width:20px; height:20px;}'
            button_style = "QPushButton {background-color: #ccc; color: black; padding: 12px; border-radius: 10px; font-weight: bold; border: 1px solid #bbb;} QPushButton:hover {background-color: #bbb;}"
            apply_button_style = "QPushButton {background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #81d4fa, stop:1 #29b6f6); color:black; padding:12px; border-radius:10px; font-weight:bold; border: none;} QPushButton:hover{background:qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #29b6f6, stop:1 #81d4fa);}"
            info_btn_style = 'QToolButton { color: black; background-color: transparent; border: none; font-size: 16px; }'
            self.theme_btn.setText('☀️')
            self.theme_btn.setStyleSheet('background-color:#ddd; border-radius:10px; color: black; border:none;')
            self.title.setStyleSheet('font-size: 24px; font-weight: bold; padding: 10px; color: black;')
        else:
            self.main_widget.setStyleSheet("#mainWidget {background-color: #f0f0f0; color: black; border-radius: 20px;}")
            self.header.setStyleSheet('background-color: #e0e0e0; border-top-left-radius: 20px; border-top-right-radius: 20px;')
            checkbox_style = 'QCheckBox {font-size:14px; padding:8px; color: black;} QCheckBox::indicator {width:20px; height:20px;}'
            button_style = "QPushButton {background-color: #ccc; color: black; padding: 12px; border-radius: 10px; font-weight: bold; border: 1px solid #bbb;} QPushButton:hover {background-color: #bbb;}"
            apply_button_style = "QPushButton {background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #81d4fa, stop:1 #29b6f6); color:black; padding:12px; border-radius:10px; font-weight:bold; border: none;} QPushButton:hover{background:qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #29b6f6, stop:1 #81d4fa);}"
            info_btn_style = 'QToolButton { color: black; background-color: transparent; border: none; font-size: 16px; }'
            self.theme_btn.setText('☀️')
            self.theme_btn.setStyleSheet('background-color:#ddd; border-radius:10px; color: black; border:none;')
            self.title.setStyleSheet('font-size: 24px; font-weight: bold; padding: 10px; color: black;')
        for cb in self.checks: cb.setStyleSheet(checkbox_style)
        for btn in self.findChildren(QToolButton): btn.setStyleSheet(info_btn_style)
        self.restore_button.setStyleSheet(button_style)
        self.apply_button.setStyleSheet(apply_button_style)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton: self.oldPos = event.globalPosition().toPoint()
    def mouseMoveEvent(self, event):
        delta = event.globalPosition().toPoint() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    loader = Loader()
    loader.show()
    sys.exit(app.exec())