import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import logging
import re

# Configuración de logging básica
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://www.osaa.org"
# Ejemplo de URL pública de calendario (esto debe ajustarse según la sección real de la web)
CALENDAR_URL = "https://www.osaa.org/calendars" 

class OSAAAPIError(Exception):
    """Excepción personalizada para errores de acceso a OSAA."""
    pass

def fetch_events_from_api(endpoint: str = "/api/events", api_key: Optional[str] = None, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Intenta obtener eventos vía API (Requiere API Key o IP registrada).
    """
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
    if api_key:
        headers["X-API-Key"] = api_key # Nombre hipotético del header de la clave

    try:
        logger.info(f"Intentando API oficial: {url}")
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data['events'] if isinstance(data, dict) and 'events' in data else data if isinstance(data, list) else []
    except Exception as e:
        logger.warning(f"API Oficial no disponible o denegada: {e}")
        raise OSAAAPIError(f"Acceso API fallido: {e}")

def fetch_events_via_scraping() -> List[Dict[str, Any]]:
    """
    Intenta extraer eventos analizando la página pública (Fallback).
    ESTE MÉTODO ES EXPERIMENTAL y depende de la estructura HTML de la web.
    """
    try:
        logger.info("Intentando extracción vía Web Scraping de la página pública...")
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(CALENDAR_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        events = []
        
        # NOTA: Este selector es hipotético. Debería ajustarse al analizar el HTML real de osaa.org/calendars
        # Buscamos tablas o divs que contengan fechas y nombres de equipos
        rows = soup.find_all('tr', class_='event-row') # Ejemplo de selector
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                events.append({
                    'id': f"scrape-{hash(row.text)}", # ID generado
                    'summary': cols[1].text.strip(),
                    'start_time': cols[0].text.strip(), # Requiere parsing a ISO
                    'location': cols[2].text.strip(),
                    'description': "Extraído vía Scraping"
                })
        
        logger.info(f"Scraping completado. Eventos encontrados: {len(events)}")
        return events
    except Exception as e:
        logger.error(f"Error en Web Scraping: {e}")
        return []

def fetch_events(params: Optional[Dict[str, Any]] = None, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Punto de entrada unificado. Intenta API primero, si falla intenta Scraping.
    """
    try:
        return fetch_events_from_api(params=params, api_key=api_key)
    except OSAAAPIError:
        return fetch_events_via_scraping()

if __name__ == "__main__":
    try:
        print(fetch_events())
    except Exception as e:
        print(f"Error: {e}")
