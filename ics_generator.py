from icalendar import Calendar, Event
from datetime import datetime
import os
from typing import List, Tuple
import logging
from database import get_all_events

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_ics_file(output_path: str) -> bool:
    """
    Lee los eventos de la base de datos y genera un archivo .ics válido.
    
    Args:
        output_path: Ruta absoluta donde se guardará el archivo .ics.
        
    Returns:
        True si el archivo se generó correctamente, False en caso contrario.
    """
    try:
        # 1. Obtener eventos de la DB
        events_data = get_all_events()
        if not events_data:
            logger.warning("No hay eventos en la base de datos para exportar.")
            return False

        # 2. Crear el calendario
        cal = Calendar()
        cal.add('prodid', '-//OSAA Sync to iCalendar//mx.osaasync.app//')
        cal.add('version', '2.0')
        cal.add('x-wr-calname', 'OSAA Sports Events')

        for event_row in events_data:
            # Mapeo de columnas según database.py:
            # 0: id, 1: summary, 2: description, 3: location, 4: start_time, 
            # 5: end_time, 6: updated_at, 7: sequence, 8: last_synced
            e_id, summary, description, location, start_time, end_time, _, sequence, _ = event_row
            
            event = Event()
            
            # UID Persistente: osaa-event-{id}@osaasync.app
            event.add('uid', f"osaa-event-{e_id}@osaasync.app")
            event.add('summary', summary)
            
            # Manejo de Descripción
            desc = description if description else "Evento de OSAA"
            event.add('description', desc)
            
            # Ubicación
            if location:
                event.add('location', location)
            
            # Fechas (ISO format YYYY-MM-DDTHH:MM:SS)
            try:
                # Convertir string ISO a objeto datetime
                start_dt = datetime.fromisoformat(start_time)
                event.add('dtstart', start_dt)
                
                if end_time:
                    end_dt = datetime.fromisoformat(end_time)
                    event.add('dtend', end_dt)
            except ValueError as e:
                logger.error(f"Error de formato de fecha en evento {e_id}: {e}")
                continue

            # SEQUENCE: Control de versión
            event.add('sequence', sequence)
            
            # Agregar evento al calendario
            cal.add_component(event)

        # 3. Escribir el archivo al disco
        with open(output_path, 'wb') as f:
            f.write(cal.to_ical())
            
        logger.info(f"Archivo .ics generado exitosamente en: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error crítico generando el archivo .ics: {e}")
        return False

if __name__ == "__main__":
    # Prueba rápida de generación
    test_path = "test_output.ics"
    if generate_ics_file(test_path):
        print(f"Prueba exitosa. Archivo creado: {test_path}")
    else:
        print("La prueba de generación falló.")
