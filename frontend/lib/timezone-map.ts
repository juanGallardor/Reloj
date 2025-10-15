// lib/timezone-map.ts
/**
 * Mapeo de IDs personalizados a formato IANA
 * Usado para convertir zonas horarias del backend al formato que JavaScript entiende
 */

export const TIMEZONE_MAP: Record<string, string> = {
  // América
  "colombia-bogota": "America/Bogota",
  "estados-unidos-new-york": "America/New_York",
  "estados-unidos-los-angeles": "America/Los_Angeles",
  "estados-unidos-chicago": "America/Chicago",
  "canada-toronto": "America/Toronto",
  "mexico-ciudad-de-mexico": "America/Mexico_City",
  "brasil-sao-paulo": "America/Sao_Paulo",
  "argentina-buenos-aires": "America/Argentina/Buenos_Aires",
  "chile-santiago": "America/Santiago",
  "peru-lima": "America/Lima",
  
  // Europa
  "reino-unido-londres": "Europe/London",
  "francia-paris": "Europe/Paris",
  "alemania-berlin": "Europe/Berlin",
  "espana-madrid": "Europe/Madrid",
  "italia-roma": "Europe/Rome",
  "rusia-moscu": "Europe/Moscow",
  "paises-bajos-amsterdam": "Europe/Amsterdam",
  
  // Asia
  "japon-tokyo": "Asia/Tokyo",
  "china-beijing": "Asia/Shanghai",
  "india-new-delhi": "Asia/Kolkata",
  "emiratos-arabes-unidos-dubai": "Asia/Dubai",
  
  // Oceanía
  "australia-sydney": "Australia/Sydney",
  "nueva-zelanda-auckland": "Pacific/Auckland",
  "fiyi-fiji": "Pacific/Fiji",
  
  // África
  "egipto-cairo": "Africa/Cairo",
  "sudafrica-johannesburg": "Africa/Johannesburg",
}

/**
 * Convierte un ID personalizado a formato IANA
 * @param customId - ID en formato "pais-ciudad"
 * @returns ID en formato IANA o null si no existe
 */
export function toIANATimezone(customId: string): string | null {
  return TIMEZONE_MAP[customId] || null
}

/**
 * Verifica si un timezone ID es válido (formato IANA)
 * @param timezoneId - ID a verificar
 * @returns true si es válido
 */
export function isValidIANATimezone(timezoneId: string): boolean {
  try {
    Intl.DateTimeFormat(undefined, { timeZone: timezoneId })
    return true
  } catch {
    return false
  }
}