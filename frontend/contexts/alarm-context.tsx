"use client"

import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react'
import { alarmsAPI, settingsAPI, type Alarm, type Settings, type FavoriteTimezone } from '@/lib/api'
import { toIANATimezone } from '@/lib/timezone-map'

// ============================================================================
// TIPOS
// ============================================================================

interface AlarmContextType {
  ringingAlarm: Alarm | null
  snoozeAlarm: () => Promise<void>
  dismissAlarm: () => void
  isRinging: boolean
  setActiveTimezone: (timezone: FavoriteTimezone | null) => void
}

const AlarmContext = createContext<AlarmContextType | undefined>(undefined)

// ============================================================================
// PROVIDER
// ============================================================================

export function AlarmProvider({ children }: { children: React.ReactNode }) {
  const [ringingAlarm, setRingingAlarm] = useState<Alarm | null>(null)
  const [settings, setSettings] = useState<Settings | null>(null)
  const [activeTimezone, setActiveTimezone] = useState<FavoriteTimezone | null>(null)
  const [lastCheckedTime, setLastCheckedTime] = useState<string>("")
  const [dismissedAlarms, setDismissedAlarms] = useState<Set<string>>(new Set())
  
  // ✅ USAR REF PARA SIEMPRE TENER EL VALOR MÁS RECIENTE
  const activeTimezoneRef = useRef<FavoriteTimezone | null>(null)
  const settingsRef = useRef<Settings | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const checkIntervalRef = useRef<NodeJS.Timeout | null>(null)

  // ✅ ACTUALIZAR REF CUANDO CAMBIE EL STATE
  useEffect(() => {
    activeTimezoneRef.current = activeTimezone
    console.log('🔄 Timezone actualizado en ref:', activeTimezone?.city || 'Local')
  }, [activeTimezone])

  useEffect(() => {
    settingsRef.current = settings
  }, [settings])

  // ========================================================================
  // CARGAR CONFIGURACIÓN AL INICIAR
  // ========================================================================
  
  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      const settingsData = await settingsAPI.get()
      setSettings(settingsData)
      console.log('⚙️ Configuración de alarmas cargada:', settingsData)
    } catch (error) {
      console.error('Error cargando configuración:', error)
    }
  }

  // ========================================================================
  // INICIALIZAR AUDIO
  // ========================================================================
  
  useEffect(() => {
    if (typeof window !== 'undefined') {
      audioRef.current = new Audio()
      audioRef.current.loop = true
    }

    return () => {
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }
    }
  }, [])

  // ========================================================================
  // VERIFICAR ALARMAS CADA 10 SEGUNDOS
  // ========================================================================
  
  useEffect(() => {
    checkAlarms()

    checkIntervalRef.current = setInterval(() => {
      checkAlarms()
    }, 10000)

    return () => {
      if (checkIntervalRef.current) {
        clearInterval(checkIntervalRef.current)
      }
    }
  }, []) // ✅ SIN DEPENDENCIAS - usa refs internamente

  // ========================================================================
  // FUNCIÓN PARA VERIFICAR SI UNA ALARMA DEBE SONAR
  // ========================================================================
  
  const checkAlarms = async () => {
    try {
      // ✅ USAR REF PARA OBTENER EL VALOR MÁS RECIENTE
      const currentTimezone = activeTimezoneRef.current
      
      let currentTime: string
      let currentDay: number

      if (currentTimezone) {
        try {
          const ianaTimezone = toIANATimezone(currentTimezone.id)
          
          if (ianaTimezone) {
            const now = new Date()
            
            const formatter = new Intl.DateTimeFormat('en-US', {
              timeZone: ianaTimezone,
              hour: '2-digit',
              minute: '2-digit',
              hour12: false
            })
            
            const parts = formatter.formatToParts(now)
            const hour = parts.find(part => part.type === 'hour')?.value || '00'
            const minute = parts.find(part => part.type === 'minute')?.value || '00'
            
            currentTime = `${hour}:${minute}`
            
            const dayFormatter = new Intl.DateTimeFormat('en-US', {
              timeZone: ianaTimezone,
              weekday: 'short'
            })
            const dayString = dayFormatter.format(now)
            
            const dayMap: Record<string, number> = {
              'Sun': 0, 'Mon': 1, 'Tue': 2, 'Wed': 3, 
              'Thu': 4, 'Fri': 5, 'Sat': 6
            }
            currentDay = dayMap[dayString] || 0
            
            console.log(`🌐 Usando timezone: ${currentTimezone.city} (${ianaTimezone})`)
            console.log(`⏰ Hora en ${currentTimezone.city}: ${currentTime}, Día: ${currentDay}`)
          } else {
            console.warn(`⚠️ Timezone no mapeado: "${currentTimezone.id}", usando hora local`)
            const now = new Date()
            currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
            currentDay = now.getDay()
          }
        } catch (timezoneError) {
          console.warn(`⚠️ Error con timezone: "${currentTimezone.id}"`, timezoneError)
          const now = new Date()
          currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
          currentDay = now.getDay()
        }
      } else {
        const now = new Date()
        currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
        currentDay = now.getDay()
        console.log(`🏠 Usando timezone local: ${currentTime}`)
      }

      // Evitar verificar la misma hora múltiples veces
      if (currentTime === lastCheckedTime) {
        return
      }

      // Limpiar alarmas descartadas del minuto anterior
      if (currentTime !== lastCheckedTime) {
        setDismissedAlarms(new Set())
        setLastCheckedTime(currentTime)
        console.log('🗑️ Limpieza de alarmas descartadas (nuevo minuto)')
      }

      // Si ya hay una alarma sonando, no verificar
      if (ringingAlarm) {
        return
      }

      console.log(`🔍 Verificando alarmas a las ${currentTime}... (Día: ${currentDay})`)

      let activeAlarms: Alarm[] = []
      
      try {
        const allAlarms = await alarmsAPI.getAll()
        activeAlarms = allAlarms.filter(alarm => alarm.enabled)
        console.log(`📋 Alarmas activas encontradas: ${activeAlarms.length}`)
      } catch (error) {
        console.error('⚠️ Error obteniendo alarmas:', error)
        return
      }

      // Buscar si alguna alarma debe sonar ahora
      for (const alarm of activeAlarms) {
        const alarmKey = `${alarm.id}-${currentTime}`
        if (dismissedAlarms.has(alarmKey)) {
          console.log(`⭕ Alarma ${alarm.id} ya fue descartada en este minuto, saltando...`)
          continue
        }

        console.log(`   🔎 Revisando: ${alarm.time} - ${alarm.label}`)
        console.log(`   🔍 Comparando: "${alarm.time}" === "${currentTime}"`)
        
        if (alarm.time === currentTime) {
          const shouldRingToday = shouldAlarmRingToday(alarm, currentDay)

          console.log(`   ⏰ Hora coincide! ¿Debe sonar hoy? ${shouldRingToday}`)

          if (shouldRingToday) {
            console.log(`🔔 ¡ALARMA ACTIVADA! ${alarm.time} - ${alarm.label}`)
            triggerAlarm(alarm)
            break
          }
        }
      }
    } catch (error) {
      console.error('❌ Error inesperado verificando alarmas:', error)
    }
  }

  // ========================================================================
  // VERIFICAR SI LA ALARMA DEBE SONAR HOY
  // ========================================================================
  
  const shouldAlarmRingToday = (alarm: Alarm, currentDay: number): boolean => {
    console.log(`   📅 Verificando si alarma "${alarm.label}" debe sonar hoy...`)
    console.log(`      - Días configurados: ${alarm.days.length > 0 ? alarm.days.join(', ') : 'Ninguno (una vez)'}`)
    console.log(`      - Día actual (número): ${currentDay}`)

    if (!alarm.days || alarm.days.length === 0) {
      console.log(`      ✅ Alarma sin días = suena cualquier día`)
      return true
    }

    const dayNames = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
    const currentDayName = dayNames[currentDay]
    
    console.log(`      - Día actual (nombre): ${currentDayName}`)

    const shouldRing = alarm.days.includes(currentDayName)
    console.log(`      ${shouldRing ? '✅' : '❌'} ¿Está "${currentDayName}" en [${alarm.days.join(', ')}]? ${shouldRing}`)
    
    return shouldRing
  }

  // ========================================================================
  // ACTIVAR ALARMA
  // ========================================================================
  
  const triggerAlarm = useCallback(async (alarm: Alarm) => {
    console.log(`🚨 ACTIVANDO ALARMA: ${alarm.label}`)
    
    const labelMatch = alarm.label.match(/\(Pospuesta desde (\d{2}:\d{2})\)/)
    if (labelMatch) {
      const originalTime = labelMatch[1]
      const originalLabel = alarm.label.replace(/ \(Pospuesta desde \d{2}:\d{2}\)/, '')
      
      setTimeout(async () => {
        try {
          await alarmsAPI.update(alarm.id, {
            time: originalTime,
            label: originalLabel,
            enabled: true,
          })
          console.log(`✅ Alarma restaurada: ${originalTime}`)
        } catch (error) {
          console.error('❌ Error restaurando alarma:', error)
        }
      }, 1000)
    }

    setRingingAlarm(alarm)

    // ✅ USAR REF PARA SETTINGS
    const currentSettings = settingsRef.current
    
    if (audioRef.current && currentSettings) {
      const soundPath = `/sounds/alarms/${currentSettings.alarm_sound}.mp3`
      console.log('🎵 Reproduciendo:', soundPath)
      console.log('🔊 Volumen:', currentSettings.alarm_volume)
      
      audioRef.current.src = soundPath
      audioRef.current.volume = currentSettings.alarm_volume / 100
      audioRef.current.loop = true

      audioRef.current.play()
        .then(() => {
          console.log(`✅ Sonando: ${soundPath}`)
        })
        .catch((error) => {
          console.error('❌ Error reproduciendo:', error)
        })
    } else {
      console.warn('⚠️ No se pudo reproducir sonido')
      console.log('audioRef:', !!audioRef.current)
      console.log('settings:', currentSettings)
    }

    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('Alarma', {
        body: `${alarm.time} - ${alarm.label}`,
        icon: '/favicon.ico',
        tag: `alarm-${alarm.id}`,
      })
    }
  }, [])

  // ========================================================================
  // POSPONER ALARMA
  // ========================================================================
  
  const snoozeAlarm = useCallback(async () => {
    if (!ringingAlarm) return

    try {
      const now = new Date()
      const currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
      const alarmKey = `${ringingAlarm.id}-${currentTime}`
      
      setDismissedAlarms(prev => new Set(prev).add(alarmKey))

      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current.currentTime = 0
        audioRef.current.loop = false
        audioRef.current.src = ''
      }

      const alarmToSnooze = ringingAlarm
      setRingingAlarm(null)

      now.setMinutes(now.getMinutes() + 5)
      const snoozeTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`

      const labelMatch = alarmToSnooze.label.match(/\(Pospuesta desde (\d{2}:\d{2})\)/)
      const originalTime = labelMatch ? labelMatch[1] : alarmToSnooze.time
      const originalLabel = alarmToSnooze.label.replace(/ \(Pospuesta desde \d{2}:\d{2}\)/, '')
      
      await alarmsAPI.update(alarmToSnooze.id, {
        time: snoozeTime,
        label: `${originalLabel} (Pospuesta desde ${originalTime})`,
        enabled: true,
      })

      console.log(`✅ Alarma pospuesta: ${snoozeTime}`)
    } catch (error) {
      console.error('❌ Error posponiendo:', error)
      setRingingAlarm(null)
    }
  }, [ringingAlarm])

  // ========================================================================
  // DESACTIVAR ALARMA
  // ========================================================================
  
  const dismissAlarm = useCallback(() => {
    if (!ringingAlarm) return

    const now = new Date()
    const currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
    const alarmKey = `${ringingAlarm.id}-${currentTime}`
    
    setDismissedAlarms(prev => new Set(prev).add(alarmKey))

    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      audioRef.current.loop = false
      audioRef.current.src = ''
    }

    setRingingAlarm(null)
    console.log('✅ Alarma desactivada')
  }, [ringingAlarm])

  // ========================================================================
  // SOLICITAR PERMISOS
  // ========================================================================
  
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission()
    }
  }, [])

  // ========================================================================
  // PROVIDER VALUE
  // ========================================================================
  
  const value: AlarmContextType = {
    ringingAlarm,
    snoozeAlarm,
    dismissAlarm,
    isRinging: ringingAlarm !== null,
    setActiveTimezone,
  }

  return (
    <AlarmContext.Provider value={value}>
      {children}
    </AlarmContext.Provider>
  )
}

// ============================================================================
// HOOK
// ============================================================================

export function useAlarm() {
  const context = useContext(AlarmContext)
  if (context === undefined) {
    throw new Error('useAlarm debe usarse dentro de AlarmProvider')
  }
  return context
}