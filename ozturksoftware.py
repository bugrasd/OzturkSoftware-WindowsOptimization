import sys
import os
import shutil
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, 
    QCheckBox, QMessageBox, QHBoxLayout, QToolButton, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt6.QtGui import QPainter, QPen, QColor, QCursor

def execute_reg_command(command, show_error=False):
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True, encoding='cp857')
    except subprocess.CalledProcessError as e:
        error_msg = f"Kayıt defteri hatası: {e.stderr.strip()}"
        if show_error:
            QMessageBox.critical(None, "Hata", error_msg)
        else:
            print(error_msg)
    except Exception as e:
        if show_error:
            QMessageBox.critical(None, "Beklenmedik Hata", f"Hata: {e}")
        else:
            print(f"Beklenmedik hata: {e}")

def optimize_display():
    cmds = [
        'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v AppsUseLightTheme /t REG_DWORD /d 0 /f',
        'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v SystemUsesLightTheme /t REG_DWORD /d 0 /f',
        'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Lock Screen" /v LockScreenImage /t REG_SZ /d "" /f', 
        'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" /v DisableLogonBackgroundImage /t REG_DWORD /d 1 /f'
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
    try:
        result = subprocess.run(f'reg import "{reg_file_path}"', shell=True, check=True, capture_output=True, text=True, encoding='cp857')
        if result.stderr:
            QMessageBox.warning(None, "Uyarı/Hata", f"Registry tweak işlemi tamamlandı, ancak bazı uyarılar/hatalar oluşmuş olabilir:\n{result.stderr.strip()}")
    except subprocess.CalledProcessError as e:
        QMessageBox.critical(None, "Hata", f"Registry tweak uygulanamadı:\n{e.stderr.strip()}")
    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Beklenmedik hata: {e}")

def clean_temp_files():
    folders = [
        os.environ.get('TEMP'),
        os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp'),
        os.path.join(os.path.expanduser('~'), 'AppData\\Roaming\\Microsoft\\Windows\\Recent')
    ]
    for folder in folders:
        if folder and os.path.exists(folder):
            for item in os.listdir(folder):
                path = os.path.join(folder, item)
                try:
                    if os.path.isfile(path) or os.path.islink(path):
                        os.unlink(path)
                    elif os.path.isdir(path):
                        shutil.rmtree(path, ignore_errors=True)
                except Exception:
                    pass

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
        
        self.status_label = QLabel("Uygulama başlatılıyor...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: white; font-size: 14px; padding-top: 10px;")
        layout.addWidget(self.status_label)
        
        self.setWindowOpacity(0)
        self.anim_opacity = QPropertyAnimation(self, b'windowOpacity')
        self.anim_opacity.setDuration(600)
        self.anim_opacity.setStartValue(0)
        self.anim_opacity.setEndValue(1)
        self.anim_opacity.start()
        
        QTimer.singleShot(1000, self.open_main)

    def open_main(self):
        self.main = MainApp()
        self.main.show()
        self.close()

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Öztürk Software - Optimization Application')
        self.setFixedSize(700, 650)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.oldPos = self.pos()
        
        bg_color = '#1e1e1e' 
        fg_color = 'white'   
        header_color = '#252525'
        title_color = '#81d4fa'
        btn_border = '#444'
        info_btn_color = '#81d4fa'
        
        self.main_widget = QWidget(self)
        self.main_widget.setObjectName("mainWidget")
        self.main_widget.setGeometry(0, 0, 700, 650)
        self.main_widget.setStyleSheet(f"#mainWidget {{background-color: {bg_color}; color: {fg_color}; border-radius: 20px;}}")

        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(0, 0, 0, 15)
        layout.setSpacing(5)

        self.header = QWidget()
        self.header.setFixedHeight(35)
        self.header.setStyleSheet(f'background-color: {header_color}; border-top-left-radius: 20px; border-top-right-radius: 20px;')
        
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
        
        layout.addWidget(self.header)

        self.title = QLabel('Öztürk Software - Optimization Application')
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet(f'font-size: 24px; font-weight: bold; padding: 10px; color: {title_color};')
        layout.addWidget(self.title)

        self.checks = []
        self.options = [
            ('Görüntü Ayarlarını Optimize Et (Koyu Tema)', 'Sistem genelinde koyu temayı etkinleştirir, kilit/oturum açma arkaplanlarını kaldırır.', optimize_display),
            ('Animasyonları Kapat', 'Windows animasyonlarını ve görsel efektleri kapatarak performansı artırır. (MinAnimate=0)', lambda: execute_reg_command('reg add "HKCU\\Control Panel\\Desktop\\WindowMetrics" /v MinAnimate /t REG_SZ /d 0 /f')),
            ('Masaüstü İpuçlarını Kapat', 'Masaüstü ipuçlarını kapatarak sistem tepkisini hızlandırır. (ShowInfoTip=0)', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v ShowInfoTip /t REG_DWORD /d 0 /f')),
            ('Görev Çubuğu Şeffaflığını Kapat', 'Görev çubuğu transparanlığını kapatarak performansı artırır. (EnableTransparency=0)', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v EnableTransparency /t REG_DWORD /d 0 /f')),
            
            ('Başlat Menüsü Önerilerini Kapat', 'Başlat menüsünde önerileri ve reklamları devre dışı bırakır. (SystemPaneSuggestionsEnabled=0)', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" /v SystemPaneSuggestionsEnabled /t REG_DWORD /d 0 /f')),
            ('Görev Çubuğu Küçük İkonlar', 'Görev çubuğunu daha kompakt hale getirir. (TaskbarSmallIcons=1)', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v TaskbarSmallIcons /t REG_DWORD /d 1 /f')),
            ('Hızlı Başlat Menüsü', 'Başlat menüsünde son kullanılan/eklenen uygulamaları gösterme. (Start_TrackProgs=0)', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v Start_TrackProgs /t REG_DWORD /d 0 /f')),
            ('Görev Çubuğu Otomatik Gizle', 'Görev çubuğunu oyun/uygulama sırasında otomatik gizler. (Binary Ayar)', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\StuckRects3" /v Settings /t REG_BINARY /d 0300000003000000 /f')),
            ('Hızlı Başlat Klasörünü Temizle', 'Başlat menüsü başlangıç klasörünü gereksiz ikonlardan temizler.', lambda: subprocess.run('DEL /F /S /Q "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\*"', shell=True)),

            ('Telemetri ve Veri Toplamayı Kapat', 'Microsoft veri toplama ve telemetri özelliklerini kapatır.', optimize_privacy),
            ('Odaklanma Modunu Aç (Yalnızca Öncelikli Bildirimler)', 'Bildirimleri minimuma indirerek oyun/uygulama performansını artırır. (FocusAssistLevel=2)', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\FocusAssist" /v FocusAssistLevel /t REG_DWORD /d 2 /f')),
            ('Reklam Kimliği Kapat', 'Uygulamaların reklam kimliğini kullanmasını engeller. (Enabled=0)', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo" /v Enabled /t REG_DWORD /d 0 /f')),
            ('Uygulama Arka Planını Kapat', 'Arka planda çalışan uygulamaları kapatarak RAM tasarrufu sağlar. (GlobalUserDisabled=1)', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications" /v GlobalUserDisabled /t REG_DWORD /d 1 /f')),
            ('Konum Servisini Kapat', 'Konum tabanlı hizmetleri kapatarak gizliliği artırır. (Status=0)', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Location" /v Status /t REG_DWORD /d 0 /f')),

            ('Güç Modunu Nihai Performansa Al', 'Tüm CPU çekirdeklerini maksimum performans için açar.', optimize_power),
            ('Hızlı Başlatmayı Kapat', 'Hiberboot özelliğini kapatarak bazı hataları/gecikmeleri önler. (HiberbootEnabled=0)', lambda: execute_reg_command('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power" /v HiberbootEnabled /t REG_DWORD /d 0 /f')),
            ('Görsel Efektleri Minimuma Al', 'Performans için tüm görsel efektleri kapatır. (VisualFXSetting=2)', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f')),
            ('SSD için TRIM Aç', 'SSD performansını korumak için TRIM komutunu etkinleştirir.', lambda: subprocess.run('fsutil behavior set DisableDeleteNotify 0', shell=True)),
            
            ('Sistem Tepkisi ve Latency Optimizasyonu', 'Sistem duyarlılığını 0\'a çeker (saf oyun modu) ve Win32 öncelik ayrımını optimize eder.', lambda: execute_reg_command('reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v SystemResponsiveness /t REG_DWORD /d 0 /f') and execute_reg_command('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl" /v Win32PrioritySeparation /t REG_DWORD /d 26 /f')),
            ('Hizmet Kapanma Süresini Hızlandır', 'Windows hizmetlerinin kapanma bekleme süresini 2 saniyeye (2000ms) düşürür.', lambda: execute_reg_command('reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control" /v WaitToKillServiceTimeout /t REG_SZ /d 2000 /f')),
            
            ('Registry İyileştirmesi Uygula', 'Sistem performansını artırmak için harici kayıt defteri tweakleri uygular.', optimize_registry),
            
            ('Geçici Dosyaları Temizle', 'Windows ve uygulamaların oluşturduğu gereksiz dosyaları temizler.', clean_temp_files),
            ('Prefetch Dosyalarını Temizle', 'Sadece Prefetch klasörünü temizler.', lambda: subprocess.run('DEL /F /S /Q %systemroot%\\Prefetch\\*', shell=True)),
            ('Geri Dönüşüm Kutusunu Boşalt', 'Disk alanını artırır. (PowerShell komutu)', lambda: execute_reg_command('powershell.exe -NoProfile -Command "Clear-RecycleBin -Force"')),
            ('DNS Önbelleğini Temizle', 'İnternet bağlantısı ve hız sorunlarını azaltır.', lambda: subprocess.run('ipconfig /flushdns', shell=True)),
            ('Windows Update Geçmişini Temizle', 'Güncelleme önbelleğini temizler ve hata olasılığını azaltır.', lambda: subprocess.run('net stop wuauserv & DEL /F /S /Q %windir%\\SoftwareDistribution\\* & net start wuauserv', shell=True)),
            ('Log Dosyalarını Temizle', 'Sistem log dosyalarını temizler.', lambda: subprocess.run('DEL /F /S /Q %systemroot%\\System32\\winevt\\Logs\\*', shell=True)),

            ('Ağ Kısıtlamasını Kaldır (Low Latency)', 'Windows\'un multimedya görevleri için uyguladığı ağ kısıtlamasını (throttling) kaldırır.', lambda: execute_reg_command('reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v NetworkThrottlingIndex /t REG_DWORD /d ffffffff /f')),
            ('TCP Hız Optimizasyonu (Nagle Kapat)', 'Nagle algoritmasını devre dışı bırakıp TCP onay frekansını artırarak ping ve latency azaltır.', lambda: execute_reg_command('reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces\\{NIC-ID}" /v TcpAckFrequency /t REG_DWORD /d 1 /f') and execute_reg_command('reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces\\{NIC-ID}" /v TCPNoDelay /t REG_DWORD /d 1 /f') and execute_reg_command('reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces\\{NIC-ID}" /v TcpDelAckTicks /t REG_DWORD /d 0 /f')),
            ('Windows Firewall Kurallarını Sıfırla', 'Gereksiz firewall kurallarını kapatır/sıfırlar.', lambda: execute_reg_command('netsh advfirewall reset')),
            ('Arka Plan Ağ Hizmetlerini Kapat (WLAN AutoConfig)', 'Oyun sırasında internet hızını potansiyel olarak artırır. (Servisi durdurur)', lambda: subprocess.run('net stop "WLAN AutoConfig"', shell=True)),
            
            ('Oyun Modunu Aç', 'Windows oyun modunu etkinleştirir. (AllowAutoGameMode=1)', lambda: execute_reg_command('reg add "HKCU\\Software\\Microsoft\\GameBar" /v AllowAutoGameMode /t REG_DWORD /d 1 /f')),
            ('GameDVR/Arkaplan Kaydını Tamamen Kapat', 'Oyun kaydı, yayın ve performans azaltıcı GameDVR özelliklerini kapatır.', lambda: execute_reg_command('reg add "HKCU\\System\\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 0 /f') and execute_reg_command('reg add "HKCU\\System\\GameConfigStore" /v GameDVR_FSEBehaviourMode /t REG_DWORD /d 2 /f') and execute_reg_command('reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\GameDVR" /v AppCaptureEnabled /t REG_DWORD /d 0 /f')),
            ('GPU Scheduling Optimize Et', 'Yeni nesil GPU planlamayı etkinleştirir. (HwSchMode=2)', lambda: execute_reg_command('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers" /v HwSchMode /t REG_DWORD /d 2 /f')),
            ('Tanı Hizmetlerini Kapat', 'Oyun sırasında gereksiz hizmetleri kapatarak performansı artırır. (DiagTrack)', lambda: subprocess.run('powershell.exe -NoProfile -Command "Stop-Service -Name \\"DiagTrack\\" -Force"', shell=True)),
        ]
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none; background-color: transparent;")
        layout.addWidget(scroll_area)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll_area.setWidget(scroll_content)
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(5)

        checkbox_style = f'QCheckBox {{font-size:14px; padding:8px; color: {fg_color};}} QCheckBox::indicator {{width:20px; height:20px;}}'
        apply_button_style = "QPushButton {background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #81d4fa, stop:1 #29b6f6); color:black; padding:12px; border-radius:10px; font-weight:bold; border: none;} QPushButton:hover{background:qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #29b6f6, stop:1 #81d4fa);}"
        info_btn_style = f'QToolButton {{ color: {info_btn_color}; background-color: transparent; border: none; font-size: 16px; }}'

        self.select_all_checkbox = QCheckBox("TÜMÜNÜ SEÇ / SEÇİMİ KALDIR")
        self.select_all_checkbox.setStyleSheet(f'QCheckBox {{font-size:16px; font-weight: bold; padding:10px; color: {title_color};}} QCheckBox::indicator {{width:20px; height:20px;}}')
        self.select_all_checkbox.stateChanged.connect(self.toggle_all_checkboxes)
        scroll_layout.addWidget(self.select_all_checkbox)
        
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background-color: {btn_border};")
        scroll_layout.addWidget(separator)

        for name, info_text, _ in self.options:
            hbox = QHBoxLayout()
            hbox.setContentsMargins(20, 0, 20, 0)
            cb = QCheckBox(name)
            cb.setStyleSheet(checkbox_style)
            self.checks.append(cb)
            hbox.addWidget(cb)
            
            info_btn = QToolButton()
            info_btn.setText('ℹ️')
            info_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            info_btn.setToolTip(info_text)
            info_btn.setStyleSheet(info_btn_style)
            info_btn.clicked.connect(lambda _, t=info_text: QMessageBox.information(self, 'Bilgi', t))
            
            hbox.addWidget(info_btn)
            hbox.addStretch()
            scroll_layout.addLayout(hbox)

        layout.addStretch()
        
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 10, 20, 10)
        
        self.apply_button = QPushButton('Seçilen Özellikleri Uygula')
        self.apply_button.clicked.connect(self.apply_selected)
        self.apply_button.setStyleSheet(apply_button_style)
        button_layout.addWidget(self.apply_button)
        
        layout.addLayout(button_layout)

    def toggle_all_checkboxes(self, state):
        is_checked = state == Qt.CheckState.Checked.value
        for cb in self.checks:
            cb.setChecked(is_checked)

    def apply_selected(self):
        selected_funcs = []
        for i, cb in enumerate(self.checks):
            if cb.isChecked():
                selected_funcs.append(self.options[i][2])
        
        if not selected_funcs:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen uygulamak için en az bir özellik seçin!')
            return

        reply = QMessageBox.question(
            self, 'Onay', 
            'Seçilen optimizasyonlar uygulanacak. Bu ayarlar geri alınamaz. Onaylıyor musunuz?', 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for func in selected_funcs:
                func()
            QMessageBox.information(self, 'Başarılı', 'Seçilen optimizasyon işlemleri tamamlandı! Değişikliklerin çoğu için sistemi yeniden başlatmanız gerekebilir.')
            for cb in self.checks:
                cb.setChecked(False)
            self.select_all_checkbox.setChecked(False)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    loader = Loader()
    loader.show()
    sys.exit(app.exec())
