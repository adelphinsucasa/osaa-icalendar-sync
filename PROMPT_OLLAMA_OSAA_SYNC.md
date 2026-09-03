# Prompt de Desarrollo: Aplicación de Escritorio OSAA Sync to iCalendar

## 🎯 Objetivo del Proyecto
Desarrollar una aplicación de escritorio nativa, ligera y eficiente que se conecte a la API de la OSAA (*Oregon School Activities Association*) (`https://www.osaa.org/api`), obtenga eventos y calendarios deportivos, y los transforme a formato iCalendar (`.ics`). 

La aplicación debe contar con un mecanismo de **sincronización inteligente (Upsert)** para actualizar eventos modificados, evitar duplicados y controlar el historial mediante una base de datos SQLite local.

---

## 🛠️ Stack Tecnológico
- **Lenguaje:** Python 3.10+
- **Interfaz Gráfica (GUI):** PyQt6 o PySide6
- **Consumo HTTP:** `requests` / `httpx`
- **Generación iCalendar:** `icalendar`
- **Base de Datos Local:** SQLite3 (incluido en la biblioteca estándar de Python)
- **Empaquetado:** `PyInstaller`

---

## 🏗️ Arquitectura y Componentes Clave

### 1. Base de Datos Local (`database.py`)
Crea una base de datos SQLite local llamada `osaa_events.db` con la siguiente tabla principal:

```sql
CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,           -- ID único retornado por la API de OSAA
    summary TEXT NOT NULL,         -- Ejemplo: "Team A vs Team B"
    description TEXT,              -- Detalles adicionales, ubicación, deporte, etc.
    location TEXT,                 -- Lugar del evento o estadio
    start_time TEXT NOT NULL,      -- Fecha/Hora inicio en formato ISO (YYYY-MM-DDTHH:MM:SS)
    end_time TEXT,                 -- Fecha/Hora fin
    updated_at TEXT,               -- Marca de tiempo de última actualización de la API
    sequence INTEGER DEFAULT 0,    -- Contador de versión para el estándar iCalendar (SEQUENCE)
    last_synced TEXT NOT NULL      -- Timestamp local de cuándo se sincronizó
);
```

### 2. Módulo de Integración con API OSAA (`osaa_api.py`)
- Módulo encargado de realizar peticiones HTTP a los endpoints de la API (`https://www.osaa.org/api/...`).
- Manejo estructurado de respuestas JSON.
- Control de errores de red, timeouts e imprevistos en las respuestas del servidor.

### 3. Motor de Sincronización y Comparación (`sync_engine.py`)
Implementa la siguiente lógica para cada evento obtenido de la API:

1. **Evento Nuevo:**
   - Si el `id` no existe en la base de datos local:
     - Insertar en SQLite con `sequence = 0`.
     - Marcar para agregar al archivo `.ics`.
2. **Evento Existente con Cambios:**
   - Si el `id` existe en la base de datos pero `start_time`, `location` o `updated_at` difieren de la API:
     - Incrementar `sequence` (`sequence = sequence + 1`).
     - Actualizar el registro en SQLite.
     - Marcar para actualización en el archivo `.ics`.
3. **Evento Invariable:**
   - Si los datos son idénticos, actualizar únicamente `last_synced`.

### 4. Generador iCalendar (`ics_generator.py`)
- Lee los eventos vigentes almacenados en SQLite.
- Genera o regenera un archivo `.ics` válido cumpliendo la especificación RFC 5545:
  - Asignar un `UID` persistente único por evento: `UID: osaa-event-{id}@osaasync.app`.
  - Asignar el campo `SEQUENCE` según el valor almacenado en SQLite.
  - Formatear adecuadamente `DTSTART`, `DTEND`, `SUMMARY`, `DESCRIPTION` y `LOCATION`.

### 5. Interfaz Gráfica (`gui.py`)
Construye una interfaz minimalista y moderna usando PyQt6/PySide6 con:
- **Barra/Campo de Configuración:** Selección de ruta de guardado del archivo `.ics` y filtro de deporte/equipo (si aplica en la API).
- **Botones de Acción:** "Sincronizar Ahora" y "Exportar .ics".
- **Área de Log / Consola Interna:** Muestra el progreso de la sincronización (ej. "Nuevos: 5, Actualizados: 2, Sin cambios: 18").
- **Barra de Progreso:** Indicador visual mientras se realiza el consumo de la API.
- **Opción de Auto-Sincronización:** Interruptor para programar sincronización automática en segundo plano (usando `QTimer` o `QThread`).

---

## 📝 Requerimientos de Código
1. Escribe el proyecto modularizado en múltiples archivos (`main.py`, `gui.py`, `database.py`, `osaa_api.py`, `sync_engine.py`, `ics_generator.py`).
2. Utiliza `QThread` para realizar las peticiones a la API en segundo plano sin congelar la interfaz de usuario.
3. Incluye un archivo `requirements.txt` con todas las dependencias necesarias (`PyQt6`, `requests`, `icalendar`).
4. Agrega un script o instrucciones breves para empaquetar el proyecto con `PyInstaller`.