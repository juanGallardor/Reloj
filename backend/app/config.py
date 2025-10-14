"""
Configuración de la aplicación Clock App.
Maneja variables de entorno y paths a archivos de datos.
"""

from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings.
    Lee variables de entorno desde archivo .env
    """
    
    # ============================================================================
    # CONFIGURACIÓN GENERAL
    # ============================================================================
    
    APP_NAME: str = "Clock App API"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # ============================================================================
    # CONFIGURACIÓN DEL FRONTEND
    # ============================================================================
    
    FRONTEND_URL: str = "http://localhost:3000"
    
    # ============================================================================
    # CONFIGURACIÓN DE ALMACENAMIENTO
    # ============================================================================
    
    DATA_DIR: str = "data"  # Directorio base para archivos JSON
    
    # ============================================================================
    # CONFIGURACIÓN DEL SERVIDOR
    # ============================================================================
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True  # Hot reload en desarrollo
    
    # ============================================================================
    # CONFIGURACIÓN DE PYDANTIC
    # ============================================================================
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignorar variables de entorno no definidas
    )
    
    # ============================================================================
    # PROPIEDADES COMPUTADAS - PATHS A ARCHIVOS JSON
    # ============================================================================
    
    @property
    def data_directory(self) -> Path:
        """
        Retorna el Path del directorio de datos.
        Crea el directorio si no existe.
        """
        data_path = Path(self.DATA_DIR)
        data_path.mkdir(parents=True, exist_ok=True)
        return data_path
    
    @property
    def ALARMS_FILE(self) -> Path:
        """Path al archivo JSON de alarmas"""
        return self.data_directory / "alarms.json"
    
    @property
    def LAPS_FILE(self) -> Path:
        """Path al archivo JSON de laps del cronómetro"""
        return self.data_directory / "laps.json"
    
    @property
    def TIMEZONES_FILE(self) -> Path:
        """Path al archivo JSON de zonas horarias"""
        return self.data_directory / "timezones.json"
    
    @property
    def SETTINGS_FILE(self) -> Path:
        """Path al archivo JSON de configuración de usuario"""
        return self.data_directory / "settings.json"
    
    # ============================================================================
    # MÉTODOS ÚTILES
    # ============================================================================
    
    def ensure_data_files_exist(self) -> None:
        """
        Verifica que existan todos los archivos de datos.
        Si no existen, los crea con valores por defecto.
        """
        import json
        
        # Archivo de alarmas
        if not self.ALARMS_FILE.exists():
            with open(self.ALARMS_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)
        
        # Archivo de laps
        if not self.LAPS_FILE.exists():
            with open(self.LAPS_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)
        
        # Archivo de zonas horarias
        if not self.TIMEZONES_FILE.exists():
            with open(self.TIMEZONES_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)
        
        # Archivo de configuración
        if not self.SETTINGS_FILE.exists():
            default_settings = {
                "time_format": "24h",
                "alarm_sound": "classic",
                "volume": 50,
                "theme": "dark"
            }
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, indent=2)
    
    def get_all_data_files(self) -> dict[str, Path]:
        """
        Retorna un diccionario con todos los archivos de datos.
        """
        return {
            "alarms": self.ALARMS_FILE,
            "laps": self.LAPS_FILE,
            "timezones": self.TIMEZONES_FILE,
            "settings": self.SETTINGS_FILE,
        }


# ============================================================================
# SINGLETON - INSTANCIA ÚNICA DE CONFIGURACIÓN
# ============================================================================

@lru_cache()
def get_settings() -> Settings:
    """
    Retorna una instancia singleton de Settings.
    
    El decorador @lru_cache asegura que solo se cree una instancia,
    mejorando el rendimiento y garantizando consistencia.
    
    Returns:
        Settings: Instancia única de configuración
    """
    settings = Settings()
    
    # Asegurar que existan los archivos de datos
    settings.ensure_data_files_exist()
    
    return settings


# ============================================================================
# INSTANCIA GLOBAL (para imports directos)
# ============================================================================

settings = get_settings()


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Obtener configuración
    config = get_settings()
    
    print("=" * 60)
    print("⚙️  CONFIGURACIÓN DE LA APLICACIÓN")
    print("=" * 60)
    print(f"📱 App Name: {config.APP_NAME}")
    print(f"🐛 Debug Mode: {config.DEBUG}")
    print(f"🌍 Environment: {config.ENVIRONMENT}")
    print(f"🌐 Frontend URL: {config.FRONTEND_URL}")
    print(f"📁 Data Directory: {config.data_directory}")
    print()
    print("📄 Archivos de datos:")
    for name, path in config.get_all_data_files().items():
        status = "✅" if path.exists() else "❌"
        print(f"  {status} {name}: {path}")
    print("=" * 60)