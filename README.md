# OSAA Sync to iCalendar 📅

Aplicación de escritorio diseñada para sincronizar eventos deportivos de la **OSAA (Oregon School Activities Association)** y transformarlos en un formato de calendario estándar (`.ics`), permitiendo su integración en Google Calendar, Apple Calendar y Outlook.

## 🎯 ¿Para qué sirve este programa?
El programa se conecta a la API de la OSAA para obtener horarios de eventos deportivos. Utiliza un motor de sincronización inteligente (**Upsert**) que guarda los datos en una base de datos local SQLite, evitando duplicados y gestionando las versiones de los eventos (SEQUENCE) para que, al importar el calendario, las actualizaciones se reflejen correctamente.

---

## 🚀 Guía de Inicio Rápido

### 1. Requisitos Previos
Asegúrate de tener instalado Python 3.10 o superior. Instala las dependencias necesarias ejecutando:
```bash
pip install -r requirements.txt
```

### 2. Ejecución del Programa
Para iniciar la aplicación, ejecuta el siguiente comando en tu terminal:
```bash
python main.py
```

### 3. Flujo de Trabajo (Sincronización y Exportación)
Para ver los eventos en tu calendario, sigue estos pasos dentro de la aplicación:

1.  **Sincronizar**: Haz clic en **"Sincronizar Ahora"**. El programa descargará los eventos y los guardará en `osaa_events.db`.
2.  **Configurar Ruta**: Haz clic en **"Buscar..."** y elige dónde quieres guardar tu archivo de calendario (ej. `calendario_osaa.ics`).
3.  **Exportar**: Haz clic en **"Exportar .ics"**. Esto generará el archivo físico en tu computadora.

### 4. Cómo importar el calendario
Una vez generado el archivo `.ics`, impórtalo en tu aplicación preferida:

*   **Google Calendar**: Configuración $\rightarrow$ Importar y exportar $\rightarrow$ Seleccionar archivo `.ics`.
*   **Apple Calendar**: Archivo $\rightarrow$ Importar $\rightarrow$ Seleccionar archivo `.ics`.
*   **Outlook**: Archivo $\rightarrow$ Abrir y exportar $\rightarrow$ Importar/Exportar $\rightarrow$ Importar archivo iCalendar.

---

## 📦 Empaquetado e Instalación en otra Máquina

Si deseas distribuir el programa como un archivo ejecutable (`.exe`) para que funcione en computadoras que no tengan Python instalado:

### 1. Instalar PyInstaller
```bash
pip install pyinstaller
```

### 2. Crear el Ejecutable
Ejecuta el siguiente comando en la raíz del proyecto:
```bash
pyinstaller --noconsole --onefile --name "OSAA_Sync_Calendar" main.py
```

### 3. Distribución
El archivo ejecutable se encontrará en la carpeta `dist/OSAA_Sync_Calendar.exe`. 
*   **Instalación**: Solo necesitas copiar ese archivo `.exe` a la otra máquina.
*   **Ejecución**: El usuario solo debe hacer doble clic en el ejecutable. La base de datos se creará automáticamente en la misma carpeta donde se encuentre el programa.

---

## 🛠️ Detalles Técnicos
- **Lenguaje:** Python 3.10+
- **GUI:** PyQt6
- **Base de Datos:** SQLite3
- **Formato de Salida:** iCalendar (RFC 5545)
- **Protección de Red:** Implementa headers de alta fidelidad y soporte para API Keys para superar bloqueos de seguridad.
