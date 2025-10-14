"use client"

import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react'
import { stopwatchAPI, type Lap as APILap } from '@/lib/api'

// ============================================================================
// TIPOS
// ============================================================================

interface Lap {
  id: number
  time: number
  lapTime: number
}

interface StopwatchContextType {
  time: number
  isRunning: boolean
  laps: Lap[]
  startStop: () => void
  reset: () => void
  addLap: () => void
  formatTime: (milliseconds: number) => {
    hours: string
    minutes: string
    seconds: string
    milliseconds: string
  }
}

// ============================================================================
// CONTEXT
// ============================================================================

const StopwatchContext = createContext<StopwatchContextType | undefined>(undefined)

// ============================================================================
// PROVIDER
// ============================================================================

export function StopwatchProvider({ children }: { children: React.ReactNode }) {
  const [time, setTime] = useState(0)
  const [isRunning, setIsRunning] = useState(false)
  const [laps, setLaps] = useState<Lap[]>([])
  const [lastLapTime, setLastLapTime] = useState(0)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const startTimeRef = useRef<number>(0)

  // ========================================================================
  // CARGAR ESTADO DESDE LOCALSTORAGE AL MONTAR
  // ========================================================================
  
  useEffect(() => {
    const savedState = localStorage.getItem('stopwatch-state')
    if (savedState) {
      try {
        const parsed = JSON.parse(savedState)
        setTime(parsed.time || 0)
        setIsRunning(parsed.isRunning || false)
        setLastLapTime(parsed.lastLapTime || 0)
        
        // Si estaba corriendo, ajustar el tiempo
        if (parsed.isRunning && parsed.startTime) {
          const elapsed = Date.now() - parsed.startTime
          setTime(parsed.time + elapsed)
          startTimeRef.current = Date.now() - (parsed.time + elapsed)
        }
        
        console.log('⏱️ Estado del cronómetro restaurado desde localStorage')
      } catch (error) {
        console.error('Error cargando estado del cronómetro:', error)
      }
    }

    // Cargar laps desde el backend
    loadLapsFromBackend()
  }, [])

  // ========================================================================
  // GUARDAR ESTADO EN LOCALSTORAGE CUANDO CAMBIE
  // ========================================================================
  
  useEffect(() => {
    const state = {
      time,
      isRunning,
      lastLapTime,
      startTime: isRunning ? startTimeRef.current : null,
    }
    localStorage.setItem('stopwatch-state', JSON.stringify(state))
  }, [time, isRunning, lastLapTime])

  // ========================================================================
  // CRONÓMETRO - INTERVALO
  // ========================================================================
  
  useEffect(() => {
    if (isRunning) {
      if (!startTimeRef.current) {
        startTimeRef.current = Date.now() - time
      }

      intervalRef.current = setInterval(() => {
        const elapsed = Date.now() - startTimeRef.current
        setTime(elapsed)
      }, 10)
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [isRunning])

  // ========================================================================
  // CARGAR LAPS DESDE BACKEND
  // ========================================================================
  
  const loadLapsFromBackend = useCallback(async () => {
    try {
      const apiLaps = await stopwatchAPI.getAllLaps()
      
      // Convertir formato backend a formato frontend
      const convertedLaps: Lap[] = apiLaps.map((apiLap) => ({
        id: apiLap.id,
        time: apiLap.total_time * 1000, // Convertir segundos a milisegundos
        lapTime: apiLap.lap_time * 1000,
      }))
      
      setLaps(convertedLaps)
      console.log('✅ Laps cargados desde backend:', convertedLaps.length)
    } catch (error) {
      console.error('Error cargando laps desde backend:', error)
    }
  }, [])

  // ========================================================================
  // FUNCIONES DE CONTROL
  // ========================================================================
  
  const startStop = useCallback(() => {
    if (!isRunning) {
      startTimeRef.current = Date.now() - time
    }
    setIsRunning(!isRunning)
  }, [isRunning, time])

  const reset = useCallback(async () => {
    setIsRunning(false)
    setTime(0)
    setLastLapTime(0)
    startTimeRef.current = 0
    
    // Limpiar laps del backend
    try {
      await stopwatchAPI.clearLaps()
      setLaps([])
      console.log('✅ Cronómetro reiniciado y laps limpiados')
    } catch (error) {
      console.error('Error limpiando laps en backend:', error)
    }
  }, [])

  const addLap = useCallback(async () => {
    if (time > 0) {
      const lapTime = time - lastLapTime
      
      try {
        // Guardar en el backend (en SEGUNDOS)
        const newLap = await stopwatchAPI.addLap({
          lap_time: lapTime / 1000, // Convertir milisegundos a segundos
          total_time: time / 1000,
        })
        
        // Agregar al estado local
        const localLap: Lap = {
          id: newLap.id,
          time: time,
          lapTime: lapTime,
        }
        
        setLaps((prevLaps) => [localLap, ...prevLaps])
        setLastLapTime(time)
        
        console.log('✅ Lap guardado en backend:', newLap)
      } catch (error) {
        console.error('Error guardando lap en backend:', error)
        
        // Si falla el backend, agregar solo localmente
        const localLap: Lap = {
          id: laps.length + 1,
          time: time,
          lapTime: lapTime,
        }
        setLaps((prevLaps) => [localLap, ...prevLaps])
        setLastLapTime(time)
      }
    }
  }, [time, lastLapTime, laps.length])

  // ========================================================================
  // FORMATEAR TIEMPO
  // ========================================================================
  
  const formatTime = useCallback((milliseconds: number) => {
    const totalSeconds = Math.floor(milliseconds / 1000)
    const hours = Math.floor(totalSeconds / 3600)
    const minutes = Math.floor((totalSeconds % 3600) / 60)
    const seconds = totalSeconds % 60
    const ms = Math.floor((milliseconds % 1000) / 10)

    return {
      hours: hours.toString().padStart(2, "0"),
      minutes: minutes.toString().padStart(2, "0"),
      seconds: seconds.toString().padStart(2, "0"),
      milliseconds: ms.toString().padStart(2, "0"),
    }
  }, [])

  // ========================================================================
  // PROVIDER VALUE
  // ========================================================================
  
  const value: StopwatchContextType = {
    time,
    isRunning,
    laps,
    startStop,
    reset,
    addLap,
    formatTime,
  }

  return (
    <StopwatchContext.Provider value={value}>
      {children}
    </StopwatchContext.Provider>
  )
}

// ============================================================================
// HOOK PERSONALIZADO
// ============================================================================

export function useStopwatch() {
  const context = useContext(StopwatchContext)
  if (context === undefined) {
    throw new Error('useStopwatch debe usarse dentro de StopwatchProvider')
  }
  return context
}