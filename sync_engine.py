from typing import Dict, List, Tuple
import logging
from osaa_api import fetch_events, OSAAAPIError
from database import init_db, upsert_event

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SyncResult:
    """Clase para almacenar el resumen de una sincronización."""
    def __init__(self):
        self.new = 0
        self.updated = 0
        self.no_change = 0
        self.errors = 0

    def __str__(self):
        return f"Nuevos: {self.new}, Actualizados: {self.updated}, Sin cambios: {self.no_change}, Errores: {self.errors}"

def synchronize_events(params: Dict = None, api_key: str = None) -> SyncResult:
    """
    Orquestador de sincronización:
    1. Obtiene eventos de la API (usando API Key si está disponible).
    2. Aplica la lógica Upsert en la base de datos.
    3. Retorna un resumen de los cambios.
    """
    result = SyncResult()
    
    # Asegurar que la DB esté inicializada
    init_db()
    
    try:
        # 1. Obtener datos de la API
        logger.info("Iniciando sincronización de eventos...")
        api_events = fetch_events(params=params, api_key=api_key)
        
        # 2. Procesar cada evento
        for event_data in api_events:
            try:
                # Extraer campos necesarios según el prompt de desarrollo
                # Se asume que la API entrega estas claves, se usan .get() por seguridad
                event_id = str(event_data.get('id', ''))
                if not event_id:
                    logger.warning("Se encontró un evento sin ID, omitiendo...")
                    result.errors += 1
                    continue
                
                summary = event_data.get('summary', 'Sin título')
                description = event_data.get('description')
                location = event_data.get('location')
                start_time = event_data.get('start_time')
                
                if not start_time:
                    logger.warning(f"Evento {event_id} sin start_time, omitiendo...")
                    result.errors += 1
                    continue
                
                end_time = event_data.get('end_time')
                updated_at = event_data.get('updated_at')
                
                # Aplicar lógica de Upsert en database.py
                status, _ = upsert_event(
                    event_id=event_id,
                    summary=summary,
                    description=description,
                    location=location,
                    start_time=start_time,
                    end_time=end_time,
                    updated_at=updated_at
                )
                
                # Contabilizar resultado
                if status == 'new':
                    result.new += 1
                elif status == 'updated':
                    result.updated += 1
                else:
                    result.no_change += 1
                    
            except Exception as e:
                logger.error(f"Error procesando evento {event_data.get('id')}: {e}")
                result.errors += 1
                
        logger.info(f"Sincronización completada: {result}")
        
    except OSAAAPIError as e:
        logger.error(f"Error crítico de API durante la sincronización: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error inesperado durante la sincronización: {e}")
        raise e
        
    return result

if __name__ == "__main__":
    # Prueba rápida de sincronización
    try:
        res = synchronize_events()
        print(f"Resultado de la prueba: {res}")
    except Exception as e:
        print(f"La prueba falló: {e}")
