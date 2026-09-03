import sys
import logging
from PyQt6.QtWidgets import QApplication
from database import init_db
from gui import OSAAApp

def main():
    """
    Punto de entrada principal de la aplicación OSAA Sync to iCalendar.
    """
    try:
        # 1. Inicialización de la Base de Datos
        # Se asegura que la tabla de eventos exista antes de lanzar la interfaz
        init_db()
        
        # 2. Lanzamiento de la Aplicación GUI
        app = QApplication(sys.argv)
        
        # Configuramos el estilo general de la aplicación (opcional)
        app.setApplicationName("OSAA Sync to iCalendar")
        
        window = OSAAApp()
        window.show()
        
        # 3. Ejecución del ciclo de eventos de Qt
        sys.exit(app.exec())
        
    except Exception as e:
        # Captura de errores críticos al iniciar la aplicación
        print(f"Error crítico durante el inicio de la aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
