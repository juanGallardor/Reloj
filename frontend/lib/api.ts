// lib/api.ts - Cliente API CORREGIDO
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============================================================================
// TIPOS TYPESCRIPT (basados en tus modelos Pydantic)
// ============================================================================

export interface Alarm {
  id: number;
  time: string;
  label: string;
  enabled: boolean;
  days: string[];
  created_at: string;
}

export interface AlarmCreate {
  time: string;
  label?: string;
  enabled?: boolean;
  days?: string[];
}

export interface AlarmUpdate {
  time?: string;
  label?: string;
  enabled?: boolean;
  days?: string[];
}

export interface Lap {
  id: number;
  lap_number: number;
  lap_time: number;
  total_time: number;
  timestamp: string;
}

export interface LapCreate {
  lap_time: number;
  total_time: number;
}

export interface LapStatistics {
  total_laps: number;
  fastest_lap: Lap | null;
  slowest_lap: Lap | null;
  average_lap_time: number;
  total_elapsed_time: number;
}

export interface Timezone {
  id: string;
  country: string;
  city: string;
  offset: string;
  is_favorite: boolean;
}

export interface FavoriteTimezone {
  id: string;
  country: string;
  city: string;
  offset: string;
  order: number;
}

export interface Settings {
  time_format: '12h' | '24h';
  alarm_sound: string;
  alarm_volume: number;
  theme: 'light' | 'dark' | 'auto';
}

export interface SettingsResponse extends Settings {
  available_sounds: string[];
  available_themes: string[];
  available_time_formats: string[];
}

// ============================================================================
// FUNCIONES AUXILIARES
// ============================================================================

async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  console.log(`🌐 API Request: ${options?.method || 'GET'} ${url}`);
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  console.log(`📡 API Response: ${response.status} ${response.statusText}`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ 
      detail: `HTTP error! status: ${response.status}` 
    }));
    console.error('❌ API Error:', error);
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  console.log('✅ API Data received:', data);
  return data;
}

// ============================================================================
// API DE ALARMAS - RUTAS CORREGIDAS
// ============================================================================

export const alarmsAPI = {
  getAll: () => fetchAPI<Alarm[]>('/api/alarms'),
  
  getById: (id: number) => fetchAPI<Alarm>(`/api/alarms/${id}`),
  
  create: (data: AlarmCreate) => {
    console.log('🔥 Creating alarm with data:', data);
    return fetchAPI<Alarm>('/api/alarms', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  
  update: (id: number, data: AlarmUpdate) =>
    fetchAPI<Alarm>(`/api/alarms/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  
  delete: (id: number) =>
    fetchAPI<{ message: string; alarm_id: number }>(`/api/alarms/${id}`, {
      method: 'DELETE',
    }),
  
  toggle: (id: number) =>
    fetchAPI<Alarm>(`/api/alarms/${id}/toggle`, {
      method: 'PATCH',
    }),
  
  getNext: () => fetchAPI<Alarm | null>('/api/alarms/next'),
  
  getActive: () => fetchAPI<Alarm[]>('/api/alarms/active'),
  
  navigate: (id: number, direction: 'next' | 'prev') =>
    fetchAPI<Alarm>(`/api/alarms/${id}/navigate?direction=${direction}`),
};

// ============================================================================
// API DE CRONÓMETRO - RUTAS CORREGIDAS
// ============================================================================

export const stopwatchAPI = {
  getAllLaps: () => fetchAPI<Lap[]>('/api/stopwatch/laps'),
  
  addLap: (data: LapCreate) => {
    console.log('⏱️ Adding lap with data:', data);
    return fetchAPI<Lap>('/api/stopwatch/laps', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  
  getLapById: (id: number) => fetchAPI<Lap>(`/api/stopwatch/laps/${id}`),
  
  deleteLap: (id: number) =>
    fetchAPI<{ message: string; lap_id: number }>(`/api/stopwatch/laps/${id}`, {
      method: 'DELETE',
    }),
  
  clearLaps: () =>
    fetchAPI<{ message: string; remaining_laps: number }>('/api/stopwatch/laps', {
      method: 'DELETE',
    }),
  
  getFastest: () => fetchAPI<Lap | null>('/api/stopwatch/laps/fastest'),
  
  getSlowest: () => fetchAPI<Lap | null>('/api/stopwatch/laps/slowest'),
  
  getStatistics: () => fetchAPI<LapStatistics>('/api/stopwatch/laps/statistics'),
  
  navigate: (lapNumber: number, direction: 'next' | 'prev') =>
    fetchAPI<Lap>(`/api/stopwatch/laps/${lapNumber}/navigate?direction=${direction}`),
  
  getFirst: () => fetchAPI<Lap | null>('/api/stopwatch/laps/first'),
  
  getLast: () => fetchAPI<Lap | null>('/api/stopwatch/laps/last'),
};

// ============================================================================
// API DE ZONAS HORARIAS - RUTAS CORREGIDAS
// ============================================================================

export const timezonesAPI = {
  getAll: (refresh = false) =>
    fetchAPI<Timezone[]>(`/api/timezones?refresh=${refresh}`),
  
  search: (query: string) =>
    fetchAPI<Timezone[]>(`/api/timezones/search?query=${encodeURIComponent(query)}`),
  
  getById: (id: string) =>
    fetchAPI<Timezone>(`/api/timezones/${encodeURIComponent(id)}`),
  
  getCountries: () => fetchAPI<string[]>('/api/timezones/countries'),
  
  getByCountry: (country: string) =>
    fetchAPI<Timezone[]>(`/api/timezones/by-country/${encodeURIComponent(country)}`),
  
  // Favoritos
  getFavorites: () => fetchAPI<FavoriteTimezone[]>('/api/timezones/favorites'),
  
  addFavorite: (timezoneId: string) =>
    fetchAPI<FavoriteTimezone>('/api/timezones/favorites', {
      method: 'POST',
      body: JSON.stringify({ timezone_id: timezoneId }),
    }),
  
  removeFavorite: (timezoneId: string) =>
    fetchAPI<{ message: string; timezone_id: string }>(
      `/api/timezones/favorites/${encodeURIComponent(timezoneId)}`,
      { method: 'DELETE' }
    ),
  
  reorderFavorite: (timezoneId: string, newPosition: number) =>
    fetchAPI<FavoriteTimezone[]>('/api/timezones/favorites/reorder', {
      method: 'PUT',
      body: JSON.stringify({ timezone_id: timezoneId, new_position: newPosition }),
    }),
  
  navigateFavorites: (timezoneId: string, direction: 'next' | 'prev') =>
    fetchAPI<FavoriteTimezone>(
      `/api/timezones/favorites/${encodeURIComponent(timezoneId)}/navigate?direction=${direction}`
    ),
  
  getCurrentTime: (timezoneId: string) =>
    fetchAPI<{
      timezone_id: string;
      city: string;
      country: string;
      offset: string;
      utc_time: string;
      current_time: string;
      current_date: string;
      day_of_week: string;
      full_datetime: string;
    }>(`/api/timezones/${encodeURIComponent(timezoneId)}/current`),
  
  isFavorite: (timezoneId: string) =>
    fetchAPI<{ timezone_id: string; is_favorite: boolean }>(
      `/api/timezones/favorites/check/${encodeURIComponent(timezoneId)}`
    ),
  
  refresh: () =>
    fetchAPI<{ message: string; total_timezones: number }>('/api/timezones/refresh', {
      method: 'POST',
    }),
};

// ============================================================================
// API DE CONFIGURACIÓN - RUTAS CORREGIDAS
// ============================================================================

export const settingsAPI = {
  get: () => fetchAPI<SettingsResponse>('/api/settings'),
  
  update: (data: Partial<Settings>) => {
    console.log('⚙️ Updating settings with:', data);
    return fetchAPI<Settings>('/api/settings', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },
  
  reset: () =>
    fetchAPI<Settings>('/api/settings/reset', {
      method: 'POST',
    }),
  
  updateTimeFormat: (format: '12h' | '24h') =>
    fetchAPI<Settings>('/api/settings/time-format', {
      method: 'PATCH',
      body: JSON.stringify({ time_format: format }),
    }),
  
  updateAlarmSound: (sound: string) =>
    fetchAPI<Settings>('/api/settings/alarm-sound', {
      method: 'PATCH',
      body: JSON.stringify({ sound }),
    }),
  
  updateVolume: (volume: number) =>
    fetchAPI<Settings>('/api/settings/volume', {
      method: 'PATCH',
      body: JSON.stringify({ volume }),
    }),
  
  updateTheme: (theme: 'light' | 'dark' | 'auto') =>
    fetchAPI<Settings>('/api/settings/theme', {
      method: 'PATCH',
      body: JSON.stringify({ theme }),
    }),
  
  toggleMute: () =>
    fetchAPI<Settings>('/api/settings/volume/toggle-mute', {
      method: 'POST',
    }),
  
  increaseVolume: (amount = 10) =>
    fetchAPI<Settings>(`/api/settings/volume/increase`, {
      method: 'PATCH',
      body: JSON.stringify({ amount }),
    }),
  
  decreaseVolume: (amount = 10) =>
    fetchAPI<Settings>(`/api/settings/volume/decrease`, {
      method: 'PATCH',
      body: JSON.stringify({ amount }),
    }),
};

// ============================================================================
// FUNCIONES DE UTILIDAD PARA DEBUGGING
// ============================================================================

export const debugAPI = {
  testConnection: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      const data = await response.json();
      console.log('🔗 API Connection test:', data);
      return data;
    } catch (error) {
      console.error('❌ API Connection failed:', error);
      throw error;
    }
  },
  
  getApiInfo: () => fetchAPI('/api'),
};

// Exportar URL base para referencia
export { API_BASE_URL };