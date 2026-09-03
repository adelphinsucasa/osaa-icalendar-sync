import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple

DB_NAME = "osaa_events.db"

def get_connection():
    """Retorna una conexión a la base de datos SQLite."""
    return sqlite3.connect(DB_NAME)

def init_db():
    """Inicializa la base de datos y crea la tabla de eventos si no existe."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
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
            )
        ''')
        conn.commit()

def upsert_event(event_id: str, summary: str, description: Optional[str], 
                 location: Optional[str], start_time: str, end_time: Optional[str], 
                 updated_at: Optional[str]) -> Tuple[str, int]:
    """
    Implementa la lógica de Upsert para eventos.
    Retorna una tupla (status, new_sequence) donde status es 'new', 'updated' o 'no_change'.
    """
    now = datetime.now().isoformat()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Buscar evento existente
        cursor.execute("SELECT start_time, location, updated_at, sequence FROM events WHERE id = ?", (event_id,))
        row = cursor.fetchone()
        
        if row is None:
            # Evento Nuevo
            cursor.execute('''
                INSERT INTO events (id, summary, description, location, start_time, end_time, updated_at, sequence, last_synced)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
            ''', (event_id, summary, description, location, start_time, end_time, updated_at, now))
            conn.commit()
            return 'new', 0
        
        db_start, db_loc, db_updated, db_seq = row
        
        # Comparar para detectar cambios
        if db_start != start_time or db_loc != location or db_updated != updated_at:
            # Evento Modificado
            new_seq = db_seq + 1
            cursor.execute('''
                UPDATE events 
                SET summary = ?, description = ?, location = ?, start_time = ?, 
                    end_time = ?, updated_at = ?, sequence = ?, last_synced = ?
                WHERE id = ?
            ''', (summary, description, location, start_time, end_time, updated_at, new_seq, now, event_id))
            conn.commit()
            return 'updated', new_seq
        else:
            # Evento Invariable
            cursor.execute("UPDATE events SET last_synced = ? WHERE id = ?", (now, event_id))
            conn.commit()
            return 'no_change', db_seq

def get_all_events() -> List[Tuple]:
    """Retorna todos los eventos almacenados en la base de datos."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events")
        return cursor.fetchall()

if __name__ == "__main__":
    init_db()
    print("Base de datos inicializada correctamente.")
