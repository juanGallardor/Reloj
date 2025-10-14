# backend/app/services/timezone_service.py
"""
Servicio de gestión de zonas horarias usando Lista Circular Doble.
✅ CORREGIDO: Ahora carga zonas horarias de TODO EL MUNDO, no solo África.
"""

from typing import Optional
import logging
import requests
from datetime import datetime, timedelta

from app.data_structures.circular_doubly_linked_list import CircularDoublyLinkedList
from app.models.timezone import Timezone, TimezoneCreate, FavoriteTimezone, generate_timezone_id
from app.database.json_db import JSONDatabase
from app.config import get_settings

logger = logging.getLogger(__name__)


class TimezoneService:
    """Servicio para gestionar zonas horarias usando lista circular doble."""
    
    WORLDTIME_API_BASE = "http://worldtimeapi.org/api"
    CACHE_EXPIRY_HOURS = 24
    
    # ✅ ZONAS HORARIAS MEJORADAS - MÁS PAÍSES
    FALLBACK_TIMEZONES = [
        # América
        ("Colombia", "Bogotá", "UTC-5"),
        ("Estados Unidos", "New York", "UTC-5"),
        ("Estados Unidos", "Los Angeles", "UTC-8"),
        ("Estados Unidos", "Chicago", "UTC-6"),
        ("Canadá", "Toronto", "UTC-5"),
        ("México", "Ciudad de México", "UTC-6"),
        ("Brasil", "São Paulo", "UTC-3"),
        ("Argentina", "Buenos Aires", "UTC-3"),
        ("Chile", "Santiago", "UTC-3"),
        ("Perú", "Lima", "UTC-5"),
        
        # Europa
        ("Reino Unido", "Londres", "UTC+0"),
        ("Francia", "París", "UTC+1"),
        ("Alemania", "Berlín", "UTC+1"),
        ("España", "Madrid", "UTC+1"),
        ("Italia", "Roma", "UTC+1"),
        ("Rusia", "Moscú", "UTC+3"),
        ("Países Bajos", "Amsterdam", "UTC+1"),
        
        # Asia
        ("Japón", "Tokyo", "UTC+9"),
        ("China", "Beijing", "UTC+8"),
        ("India", "New Delhi", "UTC+5:30"),
        ("Emiratos Árabes Unidos", "Dubai", "UTC+4"),
        
        # Oceanía
        ("Australia", "Sydney", "UTC+10"),
        ("Nueva Zelanda", "Auckland", "UTC+12"),
        
        # África
        ("Egipto", "Cairo", "UTC+2"),
        ("Sudáfrica", "Johannesburg", "UTC+2"),
    ]
    
    def __init__(self):
        """Inicializa el servicio."""
        self.favorites = CircularDoublyLinkedList[FavoriteTimezone]()
        self.available_timezones: list[Timezone] = []
        self.last_api_fetch: Optional[datetime] = None
        
        settings = get_settings()
        self.json_db = JSONDatabase(settings.TIMEZONES_FILE)
        
        self._load_available_timezones()
        self._load_favorites_from_json()
        
        logger.info(f"✅ TimezoneService inicializado con {len(self.available_timezones)} zonas horarias")
    
    # ========================================================================
    # MÉTODOS PÚBLICOS - ZONAS HORARIAS DISPONIBLES
    # ========================================================================
    
    def get_available_timezones(self, force_refresh: bool = False) -> list[Timezone]:
        """Obtiene todas las zonas horarias disponibles."""
        if force_refresh or self._should_refresh_cache():
            self._fetch_timezones_from_api()
        return self.available_timezones
    
    def search_timezone(self, query: str) -> list[Timezone]:
        """Busca zonas horarias por país, ciudad o región."""
        query_lower = query.lower()
        return [
            tz for tz in self.available_timezones
            if query_lower in tz.country.lower() 
            or query_lower in tz.city.lower()
            or query_lower in tz.id.lower()
        ]
    
    def get_timezone_by_id(self, timezone_id: str) -> Optional[Timezone]:
        """Busca una zona horaria disponible por su ID."""
        for tz in self.available_timezones:
            if tz.id == timezone_id:
                return tz
        return None
    
    def get_timezones_by_country(self, country: str) -> list[Timezone]:
        """Obtiene todas las zonas horarias de un país."""
        country_lower = country.lower()
        return [
            tz for tz in self.available_timezones
            if tz.country.lower() == country_lower
        ]
    
    def get_countries(self) -> list[str]:
        """Obtiene lista de países únicos disponibles."""
        countries = sorted(set(tz.country for tz in self.available_timezones))
        return countries
    
    def refresh_timezones(self) -> bool:
        """Fuerza refresh de zonas horarias desde la API."""
        return self._fetch_timezones_from_api()
    
    # ========================================================================
    # MÉTODOS PÚBLICOS - GESTIÓN DE FAVORITOS
    # ========================================================================
    
    def add_favorite(self, timezone_id: str) -> Optional[FavoriteTimezone]:
        """Agrega una zona horaria a favoritos."""
        tz = self.get_timezone_by_id(timezone_id)
        if not tz:
            logger.warning(f"Zona horaria no disponible: {timezone_id}")
            return None
        
        if self._is_favorite(timezone_id):
            logger.warning(f"Zona horaria ya en favoritos: {timezone_id}")
            return None
        
        order = self.favorites.size()
        
        favorite = FavoriteTimezone(
            id=tz.id,
            country=tz.country,
            city=tz.city,
            offset=tz.offset,
            order=order
        )
        
        self.favorites.insert_at_end(favorite)
        self._save_favorites_to_json()
        
        logger.info(f"✅ Zona horaria agregada a favoritos: {timezone_id}")
        return favorite
    
    def remove_favorite(self, timezone_id: str) -> bool:
        """Elimina una zona horaria de favoritos."""
        favorite = self._find_favorite(timezone_id)
        if not favorite:
            logger.warning(f"Zona horaria no encontrada en favoritos: {timezone_id}")
            return False
        
        deleted = self.favorites.delete(favorite)
        
        if deleted:
            self._reorder_favorites()
            self._save_favorites_to_json()
            logger.info(f"🗑️ Zona horaria eliminada de favoritos: {timezone_id}")
        
        return deleted
    
    def get_favorites(self) -> list[FavoriteTimezone]:
        """Obtiene todas las zonas horarias favoritas en orden."""
        return self.favorites.get_all()
    
    def reorder_favorite(self, timezone_id: str, new_position: int) -> bool:
        """Cambia el orden de una zona horaria favorita."""
        if new_position < 0 or new_position >= self.favorites.size():
            logger.warning(f"Posición inválida: {new_position}")
            return False
        
        favorite = self._find_favorite(timezone_id)
        if not favorite:
            return False
        
        if favorite.order == new_position:
            return True
        
        all_favorites = self.favorites.get_all()
        all_favorites = [f for f in all_favorites if f.id != timezone_id]
        all_favorites.insert(new_position, favorite)
        
        self.favorites.clear()
        for i, fav in enumerate(all_favorites):
            fav.order = i
            self.favorites.insert_at_end(fav)
        
        self._save_favorites_to_json()
        
        logger.info(f"🔄 Zona horaria reordenada: {timezone_id} -> posición {new_position}")
        return True
    
    def navigate_favorites(self, timezone_id: str, direction: str) -> Optional[FavoriteTimezone]:
        """Navega circularmente entre favoritos."""
        favorite = self._find_favorite(timezone_id)
        if not favorite:
            return None
        
        if direction == "next":
            next_data = self.favorites.get_next(favorite)
        elif direction == "prev":
            next_data = self.favorites.get_previous(favorite)
        else:
            logger.warning(f"Dirección inválida: {direction}")
            return None
        
        return next_data
    
    def get_first_favorite(self) -> Optional[FavoriteTimezone]:
        """Obtiene el primer favorito."""
        if self.favorites.is_empty():
            return None
        return self.favorites.head.data
    
    def count_favorites(self) -> int:
        """Cuenta el número de favoritos."""
        return len(self.favorites)
    
    def is_favorite(self, timezone_id: str) -> bool:
        """Verifica si una zona horaria está en favoritos."""
        return self._is_favorite(timezone_id)
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas del servicio."""
        return {
            "total_available": len(self.available_timezones),
            "total_favorites": self.count_favorites(),
            "total_countries": len(self.get_countries()),
            "last_api_fetch": self.last_api_fetch.isoformat() if self.last_api_fetch else None,
            "cache_valid": not self._should_refresh_cache()
        }
    
    # ========================================================================
    # MÉTODOS PRIVADOS - OPTIMIZADOS
    # ========================================================================
    
    def _load_available_timezones(self) -> None:
        """Carga zonas horarias con estrategia optimizada."""
        if self._should_refresh_cache():
            logger.info("⏳ Intentando obtener zonas horarias desde API...")
            api_success = self._fetch_timezones_from_api()
            
            if not api_success:
                logger.info("ℹ️ Usando zonas horarias de fallback")
                self.available_timezones = self._get_fallback_timezones()
        else:
            if not self.available_timezones:
                logger.info("📦 Usando zonas horarias de fallback (no hay caché)")
                self.available_timezones = self._get_fallback_timezones()
    
    def _fetch_timezones_from_api(self) -> bool:
        """
        Obtiene zonas horarias desde WorldTimeAPI.
        ✅ CORREGIDO: Ahora carga zonas de TODO EL MUNDO.
        """
        try:
            url = f"{self.WORLDTIME_API_BASE}/timezone"
            
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            timezone_names = response.json()
            
            # ✅ FILTRO MEJORADO: Seleccionar zonas de diferentes regiones
            selected_timezones = []
            
            # Definir zonas importantes de cada región
            important_zones = [
                # América
                "America/New_York", "America/Los_Angeles", "America/Chicago",
                "America/Toronto", "America/Mexico_City", "America/Bogota",
                "America/Lima", "America/Santiago", "America/Buenos_Aires",
                "America/Sao_Paulo",
                
                # Europa
                "Europe/London", "Europe/Paris", "Europe/Berlin",
                "Europe/Madrid", "Europe/Rome", "Europe/Moscow",
                "Europe/Amsterdam", "Europe/Brussels", "Europe/Vienna",
                
                # Asia
                "Asia/Tokyo", "Asia/Shanghai", "Asia/Seoul",
                "Asia/Kolkata", "Asia/Dubai", "Asia/Bangkok",
                "Asia/Singapore", "Asia/Hong_Kong",
                
                # Oceanía
                "Australia/Sydney", "Australia/Melbourne",
                "Pacific/Auckland", "Pacific/Fiji",
                
                # África
                "Africa/Cairo", "Africa/Johannesburg", "Africa/Lagos",
                "Africa/Nairobi", "Africa/Casablanca",
            ]
            
            timezones = []
            
            # Primero agregar las zonas importantes
            for tz_name in important_zones:
                if tz_name in timezone_names:
                    try:
                        parts = tz_name.split('/')
                        if len(parts) < 2:
                            continue
                        
                        region = parts[0].replace('_', ' ')
                        city = parts[-1].replace('_', ' ')
                        country = self._map_region_to_country(region, tz_name)
                        offset = self._estimate_offset_from_name(tz_name)
                        tz_id = generate_timezone_id(country, city)
                        
                        tz = Timezone(
                            id=tz_id,
                            country=country,
                            city=city,
                            offset=offset,
                            is_favorite=False
                        )
                        
                        timezones.append(tz)
                        
                    except Exception as e:
                        logger.debug(f"Error procesando zona horaria {tz_name}: {e}")
                        continue
            
            if timezones:
                self.available_timezones = timezones
                self.last_api_fetch = datetime.now()
                logger.info(f"✅ Obtenidas {len(timezones)} zonas horarias desde API")
                return True
            else:
                return False
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.warning("⚠️ Rate limit alcanzado en WorldTimeAPI - usando fallback")
            else:
                logger.error(f"❌ Error HTTP consultando WorldTimeAPI: {e}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error consultando WorldTimeAPI: {e}")
            return False
    
    def _estimate_offset_from_name(self, timezone_name: str) -> str:
        """Estima el offset UTC basado en el nombre de la zona horaria."""
        offset_map = {
            # América
            "America/New_York": "UTC-5", "America/Los_Angeles": "UTC-8",
            "America/Chicago": "UTC-6", "America/Denver": "UTC-7",
            "America/Bogota": "UTC-5", "America/Mexico_City": "UTC-6",
            "America/Sao_Paulo": "UTC-3", "America/Buenos_Aires": "UTC-3",
            "America/Lima": "UTC-5", "America/Santiago": "UTC-3",
            "America/Toronto": "UTC-5",
            
            # Europa
            "Europe/London": "UTC+0", "Europe/Paris": "UTC+1",
            "Europe/Berlin": "UTC+1", "Europe/Madrid": "UTC+1",
            "Europe/Rome": "UTC+1", "Europe/Moscow": "UTC+3",
            "Europe/Amsterdam": "UTC+1",
            
            # Asia
            "Asia/Tokyo": "UTC+9", "Asia/Shanghai": "UTC+8",
            "Asia/Seoul": "UTC+9", "Asia/Kolkata": "UTC+5:30",
            "Asia/Dubai": "UTC+4", "Asia/Bangkok": "UTC+7",
            
            # Oceanía
            "Australia/Sydney": "UTC+10", "Pacific/Auckland": "UTC+12",
            
            # África
            "Africa/Cairo": "UTC+2", "Africa/Johannesburg": "UTC+2",
        }
        
        return offset_map.get(timezone_name, "UTC+0")
    
    def _map_region_to_country(self, region: str, full_name: str) -> str:
        """
        Mapea una región a un nombre de país.
        ✅ MEJORADO: Ahora mapea correctamente TODAS las regiones.
        """
        region_mapping = {
            "America": {
                "New_York": "Estados Unidos", "Los_Angeles": "Estados Unidos",
                "Chicago": "Estados Unidos", "Denver": "Estados Unidos",
                "Toronto": "Canadá", "Mexico_City": "México",
                "Bogota": "Colombia", "Lima": "Perú",
                "Santiago": "Chile", "Buenos_Aires": "Argentina",
                "Sao_Paulo": "Brasil",
            },
            "Europe": {
                "London": "Reino Unido", "Paris": "Francia",
                "Berlin": "Alemania", "Madrid": "España",
                "Rome": "Italia", "Moscow": "Rusia",
                "Amsterdam": "Países Bajos", "Brussels": "Bélgica",
            },
            "Asia": {
                "Tokyo": "Japón", "Seoul": "Corea del Sur",
                "Shanghai": "China", "Beijing": "China",
                "Kolkata": "India", "Dubai": "Emiratos Árabes Unidos",
                "Bangkok": "Tailandia", "Singapore": "Singapur",
            },
            "Australia": {
                "Sydney": "Australia", "Melbourne": "Australia",
            },
            "Africa": {
                "Cairo": "Egipto", "Johannesburg": "Sudáfrica",
                "Lagos": "Nigeria", "Nairobi": "Kenia",
            },
            "Pacific": {
                "Auckland": "Nueva Zelanda", "Fiji": "Fiyi",
            }
        }
        
        parts = full_name.split('/')
        if len(parts) >= 2:
            city_key = parts[-1]
            
            if region in region_mapping and city_key in region_mapping[region]:
                return region_mapping[region][city_key]
        
        # Fallback
        return region.replace("_", " ").title()
    
    def _get_fallback_timezones(self) -> list[Timezone]:
        """Retorna conjunto básico de zonas horarias."""
        timezones = []
        for country, city, offset in self.FALLBACK_TIMEZONES:
            tz_id = generate_timezone_id(country, city)
            tz = Timezone(
                id=tz_id,
                country=country,
                city=city,
                offset=offset,
                is_favorite=False
            )
            timezones.append(tz)
        
        return timezones
    
    def _should_refresh_cache(self) -> bool:
        """Determina si el caché debe refrescarse."""
        if self.last_api_fetch is None:
            return True
        
        elapsed = datetime.now() - self.last_api_fetch
        return elapsed > timedelta(hours=self.CACHE_EXPIRY_HOURS)
    
    # ========================================================================
    # MÉTODOS PRIVADOS - PERSISTENCIA
    # ========================================================================
    
    def _load_favorites_from_json(self) -> None:
        """Carga favoritos desde el archivo JSON."""
        data = self.json_db.read_as_list()
        
        for item in data:
            try:
                favorite = FavoriteTimezone(**item)
                self.favorites.insert_at_end(favorite)
            except Exception as e:
                logger.error(f"Error cargando favorito: {e}")
        
        logger.info(f"📂 Cargados {len(self.favorites)} favoritos desde JSON")
    
    def _save_favorites_to_json(self) -> None:
        """Guarda el estado actual de favoritos en JSON."""
        data = [fav.model_dump(mode='json') for fav in self.get_favorites()]
        self.json_db.write(data)
        logger.debug(f"💾 Guardados {len(data)} favoritos en JSON")
    
    def _find_favorite(self, timezone_id: str) -> Optional[FavoriteTimezone]:
        """Busca un favorito por ID."""
        node = self.favorites.find(lambda f: f.id == timezone_id)
        return node.data if node else None
    
    def _is_favorite(self, timezone_id: str) -> bool:
        """Verifica si una zona está en favoritos."""
        return self._find_favorite(timezone_id) is not None
    
    def _reorder_favorites(self) -> None:
        """Reajusta los órdenes de todos los favoritos."""
        for i, favorite in enumerate(self.get_favorites()):
            favorite.order = i