import sys
import logging
from PyQt6.QtWidgets import (
     QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
     QPushButton, QLabel, QLineEdit, QFileDialog, QTextEdit, 
     QProgressBar, QCheckBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from sync_engine import synchronize_events, SyncResult
from ics_generator import generate_ics_file

# Configuración de logging para que se integre con la GUI
class GuiLogger(logging.Handler):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit

    def emit(self, record):
        msg = self.format(record)
        self.text_edit.append(msg)

class SyncWorker(QThread):
    """Hilo para ejecutar la sincronización sin bloquear la UI."""
    finished = pyqtSignal(SyncResult)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, params=None, api_key=None):
        super().__init__()
        self.params = params
        self.api_key = api_key

    def run(self):
        try:
            self.progress.emit("Iniciando sincronización con OSAA API...")
            result = synchronize_events(self.params, self.api_key)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class OSAAApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OSAA Sync to iCalendar")
        self.setMinimumSize(600, 450)
        
        self.setup_ui()
        self.setup_logging()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # --- Sección de Configuración ---
        config_group = QVBoxLayout()
        
        # Ruta del archivo ICS
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Seleccione la ruta donde guardar el archivo .ics...")
        self.btn_browse = QPushButton("Buscar...")
        self.btn_browse.clicked.connect(self.browse_file)
        path_layout.addWidget(QLabel("Archivo ICS:"))
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.btn_browse)
        
        # Filtros (Simulados por ahora según prompt)
        filter_layout = QHBoxLayout()
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filtro de deporte o equipo (opcional)...")
        filter_layout.addWidget(QLabel("Filtro API:"))
        filter_layout.addWidget(self.filter_input)

        config_group.addLayout(path_layout)
        config_group.addLayout(filter_layout)
        layout.addLayout(config_group)

        # --- Botones de Acción ---
        actions_layout = QHBoxLayout()
        self.btn_sync = QPushButton("Sincronizar Ahora")
        self.btn_sync.clicked.connect(self.start_sync)
        
        self.btn_export = QPushButton("Exportar .ics")
        self.btn_export.clicked.connect(self.export_ics)
        
        self.auto_sync_cb = QCheckBox("Auto-Sincronización (fondo)")
        
        actions_layout.addWidget(self.btn_sync)
        actions_layout.addWidget(self.btn_export)
        actions_layout.addWidget(self.auto_sync_cb)
        layout.addLayout(actions_layout)

        # --- API Key Field ---
        key_layout = QHBoxLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Ingrese su API Key de OSAA (si tiene una)...")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        key_layout.addWidget(QLabel("API Key:"))
        key_layout.addWidget(self.api_key_input)
        layout.addLayout(key_layout)

        # --- Área de Logs ---
        layout.addWidget(QLabel("Progreso y Logs:"))
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("background-color: #1e1e1e; color: #dcdcdc; font-family: Consolas, monospace;")
        layout.addWidget(self.log_area)

        # --- Barra de Progreso ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

    def setup_logging(self):
        # Redirigir logs de Python a la QTextEdit de la GUI
        handler = GuiLogger(self.log_area)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)

    def browse_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Calendario", "", "iCalendar Files (*.ics)"
        )
        if file_path:
            self.path_input.setText(file_path)

    def start_sync(self):
        self.btn_sync.setEnabled(False)
        self.progress_bar.setRange(0, 0) # Modo indeterminado (animación de carga)
        
        # Obtener parámetros del filtro y la API Key
        params = {}
        if self.filter_input.text():
            params['q'] = self.filter_input.text()
        
        api_key = self.api_key_input.text()

        self.worker = SyncWorker(params, api_key)
        self.worker.progress.connect(lambda msg: self.log_area.append(f"ℹ️ {msg}"))
        self.worker.finished.connect(self.on_sync_finished)
        self.worker.error.connect(self.on_sync_error)
        self.worker.start()

    def on_sync_finished(self, result: SyncResult):
        self.btn_sync.setEnabled(True)
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)
        self.log_area.append(f"✅ <b>Sincronización completada:</b> {result}")

    def on_sync_error(self, error_msg: str):
        self.btn_sync.setEnabled(True)
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)
        self.log_area.append(f"❌ <b>Error:</b> {error_msg}")

    def export_ics(self):
        path = self.path_input.text()
        if not path:
            self.log_area.append("⚠️ Por favor, seleccione una ruta para guardar el archivo .ics")
            return
        
        self.log_area.append(f"Exportando calendario a {path}...")
        if generate_ics_file(path):
            self.log_area.append("✅ Archivo .ics exportado exitosamente.")
        else:
            self.log_area.append("❌ Error al exportar el archivo .ics")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OSAAApp()
    window.show()
    sys.exit(app.exec())
