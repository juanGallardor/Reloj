"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Plus, X, Check, Loader2, Globe, AlertCircle, MapPin } from "lucide-react"
import { CustomDropdown } from "./custom-dropdown"
import { timezonesAPI, Timezone, FavoriteTimezone } from "@/lib/api"

interface TimezoneSelectorProps {
  onActiveTimezoneChange?: (timezone: FavoriteTimezone | null) => void
}

const DEFAULT_TIMEZONE: FavoriteTimezone = {
  id: "colombia-bogota",
  country: "Colombia",
  city: "Bogotá",
  offset: "UTC-5",
  order: -1
}

export function TimezoneSelector({ onActiveTimezoneChange }: TimezoneSelectorProps = {}) {
  const [availableTimezones, setAvailableTimezones] = useState<Timezone[]>([])
  const [favoriteTimezones, setFavoriteTimezones] = useState<FavoriteTimezone[]>([])
  const [countries, setCountries] = useState<string[]>([])
  
  const [selectedCountry, setSelectedCountry] = useState("")
  const [selectedCity, setSelectedCity] = useState("")
  const [activeTimezoneId, setActiveTimezoneId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentTimes, setCurrentTimes] = useState<Record<string, string>>({})
  const [currentDates, setCurrentDates] = useState<Record<string, string>>({})

  const calculateLocalTime = (offset: string): { time: string; date: string } => {
    try {
      const offsetStr = offset.replace("UTC", "").trim()
      let offsetHours = 0
      let offsetMinutes = 0

      if (offsetStr.includes(':')) {
        const [hours, minutes] = offsetStr.split(':')
        offsetHours = parseInt(hours)
        offsetMinutes = parseInt(minutes)
      } else {
        offsetHours = parseInt(offsetStr) || 0
      }

      const sign = offsetHours >= 0 ? 1 : -1
      const totalOffsetMinutes = (Math.abs(offsetHours) * 60 + Math.abs(offsetMinutes)) * sign

      const now = new Date()
      
      const utcTimestamp = Date.UTC(
        now.getUTCFullYear(),
        now.getUTCMonth(),
        now.getUTCDate(),
        now.getUTCHours(),
        now.getUTCMinutes(),
        now.getUTCSeconds()
      )

      const localTimestamp = utcTimestamp + (totalOffsetMinutes * 60 * 1000)
      const localDate = new Date(localTimestamp)

      const hours = String(localDate.getUTCHours()).padStart(2, '0')
      const minutes = String(localDate.getUTCMinutes()).padStart(2, '0')
      const seconds = String(localDate.getUTCSeconds()).padStart(2, '0')
      const time = `${hours}:${minutes}:${seconds}`

      const year = localDate.getUTCFullYear()
      const month = String(localDate.getUTCMonth() + 1).padStart(2, '0')
      const day = String(localDate.getUTCDate()).padStart(2, '0')
      const date = `${year}-${month}-${day}`

      return { time, date }
    } catch (err) {
      return { time: "--:--:--", date: "--" }
    }
  }

  const saveActiveTimezone = (timezoneId: string | null) => {
    if (typeof window !== 'undefined' && timezoneId) {
      localStorage.setItem('activeTimezoneId', timezoneId)
    }
  }

  const loadActiveTimezone = (): string | null => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('activeTimezoneId')
    }
    return null
  }

  useEffect(() => {
    loadInitialData()
  }, [])

  const loadInitialData = async () => {
    try {
      setIsLoading(true)
      setError(null)

      console.log("🔄 === CARGANDO DATOS INICIALES ===")

      let timezones: Timezone[] = []
      let favorites: FavoriteTimezone[] = []

      // Cargar zonas horarias
      try {
        timezones = await timezonesAPI.getAll()
        console.log("✅ Zonas horarias cargadas:", timezones.length)
        console.log("📍 Primeras 3 zonas:", timezones.slice(0, 3))
      } catch (err) {
        console.error("⚠️ Error cargando zonas horarias:", err)
      }

      // ✅ SIEMPRE extraer países de las zonas horarias (NO usar el endpoint /countries)
      let countriesList: string[] = []
      
      if (timezones.length > 0) {
        // Extraer países únicos de las zonas horarias
        const uniqueCountries = [...new Set(timezones.map(tz => tz.country))]
          .filter(country => country && country !== 'Africa') // Filtrar "Africa" si aparece
          .sort()
        
        console.log("✅ Países extraídos de zonas horarias:", uniqueCountries.length)
        console.log("🌍 Lista completa de países:", uniqueCountries)
        
        countriesList = uniqueCountries
      } else {
        console.warn("⚠️ No hay zonas horarias, usando lista vacía de países")
      }

      // Cargar favoritos
      try {
        favorites = await timezonesAPI.getFavorites()
        console.log("✅ Favoritos cargados:", favorites.length)
      } catch (err) {
        console.error("⚠️ Error cargando favoritos:", err)
      }

      console.log("📊 RESUMEN FINAL:")
      console.log("   Zonas horarias:", timezones.length)
      console.log("   Países:", countriesList.length)
      console.log("   Favoritos:", favorites.length)

      setAvailableTimezones(timezones)
      setCountries(countriesList)

      const allFavorites = [DEFAULT_TIMEZONE, ...favorites]
      setFavoriteTimezones(allFavorites)

      const savedActiveId = loadActiveTimezone()
      
      if (savedActiveId && allFavorites.some(fav => fav.id === savedActiveId)) {
        setActiveTimezoneId(savedActiveId)
        const savedTimezone = allFavorites.find(fav => fav.id === savedActiveId)
        if (savedTimezone) {
          onActiveTimezoneChange?.(savedTimezone)
        }
      } else {
        setActiveTimezoneId(DEFAULT_TIMEZONE.id)
        onActiveTimezoneChange?.(DEFAULT_TIMEZONE)
      }

    } catch (err) {
      console.error("❌ Error general:", err)
      setError("Error al cargar datos")
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (favoriteTimezones.length === 0) return

    const updateTimes = () => {
      const newTimes: Record<string, string> = {}
      const newDates: Record<string, string> = {}

      favoriteTimezones.forEach((fav) => {
        const { time, date } = calculateLocalTime(fav.offset)
        newTimes[fav.id] = time
        newDates[fav.id] = date
      })

      setCurrentTimes(newTimes)
      setCurrentDates(newDates)
    }

    updateTimes()
    const timer = setInterval(updateTimes, 1000)

    return () => clearInterval(timer)
  }, [favoriteTimezones])

  const handleAddFavorite = async () => {
    if (!selectedCountry || !selectedCity) return

    try {
      const timezone = availableTimezones.find(
        (tz) => tz.country === selectedCountry && tz.city === selectedCity
      )

      if (!timezone) {
        setError("Zona horaria no encontrada")
        setTimeout(() => setError(null), 3000)
        return
      }

      const alreadyFavorite = favoriteTimezones.some((fav) => fav.id === timezone.id)
      if (alreadyFavorite) {
        setError("Esta zona horaria ya está en favoritos")
        setTimeout(() => setError(null), 3000)
        return
      }

      const newFavorite = await timezonesAPI.addFavorite(timezone.id)

      setFavoriteTimezones(prev => [DEFAULT_TIMEZONE, ...prev.filter(f => f.id !== DEFAULT_TIMEZONE.id), newFavorite])

      setActiveTimezoneId(newFavorite.id)
      saveActiveTimezone(newFavorite.id)
      onActiveTimezoneChange?.(newFavorite)

      setSelectedCountry("")
      setSelectedCity("")
      setError(null)

    } catch (err: any) {
      console.error("❌ Error agregando favorito:", err)
      setError(err?.message || "Error al agregar zona horaria")
      setTimeout(() => setError(null), 5000)
    }
  }

  const handleRemoveFavorite = async (timezoneId: string) => {
    if (timezoneId === DEFAULT_TIMEZONE.id) {
      setError("No puedes eliminar la zona horaria de Colombia")
      setTimeout(() => setError(null), 3000)
      return
    }

    try {
      await timezonesAPI.removeFavorite(timezoneId)
      
      const newFavorites = favoriteTimezones.filter(fav => fav.id !== timezoneId)
      setFavoriteTimezones(newFavorites)
      
      if (activeTimezoneId === timezoneId) {
        setActiveTimezoneId(DEFAULT_TIMEZONE.id)
        saveActiveTimezone(DEFAULT_TIMEZONE.id)
        onActiveTimezoneChange?.(DEFAULT_TIMEZONE)
      }

    } catch (err) {
      console.error("❌ Error eliminando favorito:", err)
      setError("Error al eliminar zona horaria")
      setTimeout(() => setError(null), 3000)
    }
  }

  const handleSetActiveTimezone = (timezoneId: string) => {
    setActiveTimezoneId(timezoneId)
    saveActiveTimezone(timezoneId)
    
    const timezone = favoriteTimezones.find(fav => fav.id === timezoneId)
    if (timezone) {
      onActiveTimezoneChange?.(timezone)
    }
  }

  const countryOptions = countries.map((country) => ({
    value: country,
    label: country,
  }))

  const cityOptions = availableTimezones
    .filter((tz) => tz.country === selectedCountry)
    .map((tz) => ({
      value: tz.city,
      label: tz.city,
    }))

  if (isLoading) {
    return (
      <div className="w-full max-w-4xl mx-auto flex items-center justify-center py-20">
        <div className="text-center space-y-4">
          <Loader2 className="w-12 h-12 text-cyan-400 animate-spin mx-auto" />
          <p className="text-cyan-400/60">Cargando zonas horarias...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full max-w-4xl mx-auto relative">
      <div className="relative space-y-8">
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="bg-red-500/20 border border-red-500/50 px-4 py-3 rounded-sm flex items-start gap-3"
            >
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-red-400 text-sm flex-1">{error}</p>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="bg-black/40 backdrop-blur-sm border border-cyan-400/30 p-6 space-y-4 rounded-none">
          <h3 className="text-cyan-400 font-semibold mb-4">Agregar Zona Horaria</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="relative" style={{ zIndex: 50 }}>
              <CustomDropdown
                options={countryOptions}
                value={selectedCountry}
                onChange={(value) => {
                  setSelectedCountry(value)
                  setSelectedCity("")
                  setError(null)
                }}
                placeholder="Seleccionar país"
              />
            </div>

            <div className="relative" style={{ zIndex: 40 }}>
              <CustomDropdown
                options={cityOptions}
                value={selectedCity}
                onChange={(value) => {
                  setSelectedCity(value)
                  setError(null)
                }}
                placeholder="Seleccionar ciudad"
                disabled={!selectedCountry}
              />
            </div>

            <button
              onClick={handleAddFavorite}
              disabled={!selectedCountry || !selectedCity}
              className="bg-cyan-400/20 hover:bg-cyan-400/30 border border-cyan-400/50 px-4 py-3 text-cyan-400 font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 rounded-xs"
            >
              <Plus className="w-5 h-5" />
              Agregar
            </button>
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-cyan-400 font-semibold flex items-center gap-2">
            <Globe className="w-5 h-5" />
            Zonas Horarias Favoritas ({favoriteTimezones.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <AnimatePresence>
              {favoriteTimezones.map((tz) => {
                const isDefault = tz.id === DEFAULT_TIMEZONE.id
                
                return (
                  <motion.div
                    key={tz.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    onClick={() => handleSetActiveTimezone(tz.id)}
                    className={`bg-black/40 backdrop-blur-sm border p-4 relative group rounded-xs cursor-pointer transition-all ${
                      activeTimezoneId === tz.id
                        ? "border-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.5)]"
                        : "border-cyan-400/30 hover:border-cyan-400/50"
                    } ${isDefault ? "bg-cyan-950/20" : ""}`}
                  >
                    {isDefault && (
                      <div className="absolute top-2 right-2 flex items-center gap-1 bg-cyan-400/20 px-2 py-1 rounded text-xs text-cyan-400">
                        <MapPin className="w-3 h-3" />
                        Por defecto
                      </div>
                    )}

                    {activeTimezoneId === tz.id && (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="absolute top-2 left-2 text-cyan-400"
                      >
                        <Check className="w-5 h-5 drop-shadow-[0_0_8px_rgba(6,182,212,1)]" />
                      </motion.div>
                    )}

                    {!isDefault && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleRemoveFavorite(tz.id)
                        }}
                        className="absolute top-2 right-2 text-red-400 hover:text-red-300 opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    )}

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-lg text-cyan-400 mt-2.5">
                          {tz.city}
                        </span>
                        <span className="text-cyan-400/60 text-sm">{tz.offset}</span>
                      </div>
                      <div className="text-cyan-400/80 text-sm">{tz.country}</div>
                      <div className="text-cyan-400/60 text-xs">
                        {currentDates[tz.id] || '--'}
                      </div>
                      <div
                        className={`text-2xl font-bold mt-2 font-mono ${
                          activeTimezoneId === tz.id
                            ? "text-cyan-400 drop-shadow-[0_0_10px_rgba(6,182,212,0.8)]"
                            : "text-cyan-400"
                        }`}
                      >
                        {currentTimes[tz.id] || '--:--:--'}
                      </div>
                    </div>
                  </motion.div>
                )
              })}
            </AnimatePresence>
          </div>
        </div>

        <div className="text-center text-cyan-400/40 text-xs">
          {countries.length} países • {availableTimezones.length} zonas disponibles
        </div>
      </div>
    </div>
  )
}