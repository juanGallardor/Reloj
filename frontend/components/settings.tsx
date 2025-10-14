"use client"

import { useState, useEffect, useRef } from "react"
import { motion } from "framer-motion"
import { Volume2, VolumeX, Clock, Music, Play, Loader2 } from "lucide-react"
import { CustomDropdown } from "./custom-dropdown"
import { settingsAPI } from "@/lib/api"

interface SettingsProps {
  timeFormat: "12h" | "24h"
  onTimeFormatChange: (format: "12h" | "24h") => void
}

export function Settings({ timeFormat, onTimeFormatChange }: SettingsProps) {
  const [alarmVolume, setAlarmVolume] = useState(50)
  const [alarmSound, setAlarmSound] = useState("classic")
  const [isLoading, setIsLoading] = useState(true)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  const alarmSoundOptions = [
    { value: "classic", label: "Clásico" },
    { value: "gentle", label: "Suave" },
    { value: "radar", label: "Radar" },
    { value: "beacon", label: "Faro" },
    { value: "chimes", label: "Campanas" },
    { value: "digital", label: "Digital" },
  ]

  const timeFormatOptions = [
    { value: "12h", label: "12 horas (AM/PM)" },
    { value: "24h", label: "24 horas" },
  ]

  // ========================================================================
  // CARGAR CONFIGURACIÓN DESDE EL BACKEND
  // ========================================================================
  
  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      setIsLoading(true)
      const settings = await settingsAPI.get()
      
      setAlarmVolume(settings.alarm_volume)
      setAlarmSound(settings.alarm_sound)
      onTimeFormatChange(settings.time_format)
      
      console.log('✅ Configuración cargada desde backend:', settings)
    } catch (error) {
      console.error('❌ Error cargando configuración:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // ========================================================================
  // INICIALIZAR AUDIO
  // ========================================================================
  
  useEffect(() => {
    // Crear instancia de Audio
    if (typeof window !== 'undefined') {
      audioRef.current = new Audio()
      audioRef.current.addEventListener('ended', () => {
        setIsPlaying(false)
      })
    }

    return () => {
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }
    }
  }, [])

  // ========================================================================
  // ACTUALIZAR VOLUMEN DEL AUDIO CUANDO CAMBIA EL SLIDER
  // ========================================================================
  
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = alarmVolume / 100
    }
  }, [alarmVolume])

  // ========================================================================
  // PROBAR SONIDO
  // ========================================================================
  
  const handlePlaySound = async () => {
    if (!audioRef.current) return

    try {
      // Si está reproduciendo, detener
      if (isPlaying) {
        audioRef.current.pause()
        audioRef.current.currentTime = 0
        setIsPlaying(false)
        return
      }

      // Reproducir sonido
      setIsPlaying(true)
      audioRef.current.src = `/sounds/alarms/${alarmSound}.mp3`
      audioRef.current.volume = alarmVolume / 100
      
      await audioRef.current.play()
      console.log(`🔊 Reproduciendo sonido: ${alarmSound} al ${alarmVolume}%`)
    } catch (error) {
      console.error('Error reproduciendo sonido:', error)
      setIsPlaying(false)
    }
  }

  // ========================================================================
  // GUARDAR CAMBIOS EN EL BACKEND
  // ========================================================================
  
  const saveSettings = async (field: 'alarm_sound' | 'alarm_volume' | 'time_format', value: any) => {
    try {
      setIsSaving(true)
      
      const updateData: any = {}
      updateData[field] = value

      await settingsAPI.update(updateData)
      console.log(`✅ ${field} guardado:`, value)
    } catch (error) {
      console.error(`❌ Error guardando ${field}:`, error)
    } finally {
      setIsSaving(false)
    }
  }

  // ========================================================================
  // HANDLERS
  // ========================================================================
  
  const handleSoundChange = async (newSound: string) => {
    setAlarmSound(newSound)
    
    // Detener sonido si está reproduciendo
    if (isPlaying && audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      setIsPlaying(false)
    }

    await saveSettings('alarm_sound', newSound)
  }

  const handleVolumeChange = (newVolume: string) => {
    const volumeNum = parseInt(newVolume)
    setAlarmVolume(volumeNum)
  }

  const handleVolumeChangeComplete = async (e: React.MouseEvent | React.TouchEvent) => {
    // Guardar cuando el usuario suelta el slider
    await saveSettings('alarm_volume', alarmVolume)
  }

  const handleTimeFormatChange = async (format: string) => {
    const newFormat = format as "12h" | "24h"
    onTimeFormatChange(newFormat)
    await saveSettings('time_format', newFormat)
  }

  const handleMuteToggle = async () => {
    const newVolume = alarmVolume > 0 ? 0 : 50
    setAlarmVolume(newVolume)
    await saveSettings('alarm_volume', newVolume)
  }

  // ========================================================================
  // OBTENER DESCRIPCIÓN DEL NIVEL DE VOLUMEN
  // ========================================================================
  
  const getVolumeDescription = () => {
    if (alarmVolume === 0) return "Silenciado"
    if (alarmVolume <= 25) return "Bajo"
    if (alarmVolume <= 50) return "Medio"
    if (alarmVolume <= 75) return "Alto"
    return "Muy alto"
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 min-h-[400px]">
        <Loader2 className="w-12 h-12 text-cyan-400 animate-spin" />
        <p className="text-cyan-400/60">Cargando configuración...</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center gap-8 w-full max-w-2xl mx-auto pb-32">
      <div className="leading-[4.75rem] tracking-normal w-full space-y-7">
        
        {/* FORMATO DE HORA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="backdrop-blur-sm border-2 border-cyan-400/30 p-6 shadow-[0_0_20px_rgba(6,182,212,0.2)] py-6 rounded-4xl border-solid bg-black"
        >
          <div className="flex items-center gap-3 mb-4">
            <Clock className="w-6 h-6 text-cyan-400 drop-shadow-[0_0_8px_rgba(6,182,212,0.8)]" />
            <h3 className="text-xl font-semibold text-cyan-400">Formato de Hora</h3>
          </div>
          <CustomDropdown
            options={timeFormatOptions}
            value={timeFormat}
            onChange={handleTimeFormatChange}
          />
        </motion.div>

        {/* SONIDO DE ALARMA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="backdrop-blur-sm border-2 border-cyan-400/30 p-6 shadow-[0_0_20px_rgba(6,182,212,0.2)] rounded-4xl border-solid bg-black"
        >
          <div className="flex items-center gap-3 mb-4">
            <Music className="w-6 h-6 text-cyan-400 drop-shadow-[0_0_8px_rgba(6,182,212,0.8)]" />
            <h3 className="text-xl font-semibold text-cyan-400">Sonido de Alarma</h3>
          </div>
          
          <CustomDropdown 
            options={alarmSoundOptions} 
            value={alarmSound} 
            onChange={handleSoundChange} 
          />
          
          {/* BOTÓN PROBAR SONIDO */}
          <motion.button
            onClick={handlePlaySound}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            disabled={alarmVolume === 0}
            className={`w-full mt-4 flex items-center justify-center gap-3 px-6 py-3 font-semibold text-lg transition-all rounded-xl ${
              isPlaying
                ? "bg-red-500/20 border-2 border-red-400/50 text-red-400 shadow-[0_0_20px_rgba(239,68,68,0.4)]"
                : "bg-cyan-400/20 border-2 border-cyan-400/50 text-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.4)]"
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            <Play className={`w-5 h-5 ${isPlaying ? 'animate-pulse' : ''}`} />
            {isPlaying ? 'Reproduciendo...' : 'Probar Sonido'}
          </motion.button>

          <p className="text-cyan-400/50 text-sm mt-3">
            Selecciona el sonido que se reproducirá cuando suene la alarma
          </p>
        </motion.div>

        {/* VOLUMEN DE ALARMA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="backdrop-blur-sm border-2 border-cyan-400/30 p-6 shadow-[0_0_20px_rgba(6,182,212,0.2)] bg-black rounded-4xl border-solid"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              {alarmVolume === 0 ? (
                <VolumeX className="w-6 h-6 text-red-400 drop-shadow-[0_0_8px_rgba(239,68,68,0.8)]" />
              ) : (
                <Volume2 className="w-6 h-6 text-cyan-400 drop-shadow-[0_0_8px_rgba(6,182,212,0.8)]" />
              )}
              <h3 className="text-xl font-semibold text-cyan-400">Volumen de Alarma</h3>
            </div>

            {/* BOTÓN MUTE/UNMUTE */}
            <motion.button
              onClick={handleMuteToggle}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              className="p-2 rounded-lg bg-cyan-400/10 hover:bg-cyan-400/20 transition-all"
            >
              {alarmVolume === 0 ? (
                <VolumeX className="w-5 h-5 text-red-400" />
              ) : (
                <Volume2 className="w-5 h-5 text-cyan-400" />
              )}
            </motion.button>
          </div>

          <div className="space-y-3">
            <input
              type="range"
              min="0"
              max="100"
              value={alarmVolume}
              onChange={(e) => handleVolumeChange(e.target.value)}
              onMouseUp={handleVolumeChangeComplete}
              onTouchEnd={handleVolumeChangeComplete}
              className="w-full h-3 bg-cyan-400/20 appearance-none cursor-pointer rounded-full [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-6 [&::-webkit-slider-thumb]:h-6 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-cyan-400 [&::-webkit-slider-thumb]:shadow-[0_0_15px_rgba(6,182,212,1)] [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:transition-all hover:[&::-webkit-slider-thumb]:scale-110"
            />
            
            <div className="flex justify-between items-center text-cyan-400/60 text-sm">
              <span>0%</span>
              <motion.div
                key={alarmVolume}
                initial={{ scale: 1.2 }}
                animate={{ scale: 1 }}
                className="flex flex-col items-center"
              >
                <span className="text-cyan-400 font-semibold text-lg drop-shadow-[0_0_8px_rgba(6,182,212,0.6)]">
                  {alarmVolume}%
                </span>
                <span className="text-cyan-400/50 text-xs">
                  {getVolumeDescription()}
                </span>
              </motion.div>
              <span>100%</span>
            </div>

            {/* INDICADOR DE GUARDADO */}
            {isSaving && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center gap-2 text-cyan-400/60 text-xs justify-center"
              >
                <Loader2 className="w-3 h-3 animate-spin" />
                <span>Guardando...</span>
              </motion.div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  )
}