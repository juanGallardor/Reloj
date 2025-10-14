"use client"

import { motion, AnimatePresence } from "framer-motion"
import { Bell, Clock, Timer, X } from "lucide-react"
import { useAlarm } from "@/contexts/alarm-context"
import { useEffect, useState } from "react"

export function AlarmNotification() {
  const { ringingAlarm, snoozeAlarm, dismissAlarm, isRinging } = useAlarm()
  const [currentTime, setCurrentTime] = useState("")

  // DEBUG: Log cuando cambie el estado
  useEffect(() => {
    console.log('🔄 AlarmNotification - Estado cambió:', {
      isRinging,
      hasAlarm: !!ringingAlarm,
      alarmId: ringingAlarm?.id,
      alarmLabel: ringingAlarm?.label,
    })
  }, [isRinging, ringingAlarm])

  // ========================================================================
  // ACTUALIZAR HORA ACTUAL CADA SEGUNDO
  // ========================================================================
  
  useEffect(() => {
    if (!isRinging) return

    const updateTime = () => {
      const now = new Date()
      setCurrentTime(
        now.toLocaleTimeString('es-ES', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
        })
      )
    }

    updateTime()
    const interval = setInterval(updateTime, 1000)

    return () => clearInterval(interval)
  }, [isRinging])

  // ========================================================================
  // SOPORTE PARA TECLADO (INTEGRADO)
  // ========================================================================
  
  useEffect(() => {
    if (!isRinging) return

    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        dismissAlarm()
      } else if (e.key === ' ' || e.key === 'Spacebar') {
        e.preventDefault()
        snoozeAlarm()
      }
    }

    window.addEventListener('keydown', handleKeyPress)

    return () => {
      window.removeEventListener('keydown', handleKeyPress)
    }
  }, [isRinging, dismissAlarm, snoozeAlarm])

  // ========================================================================
  // FORMATEAR DÍAS
  // ========================================================================
  
  const formatDays = (days: string[]) => {
    if (!days || days.length === 0) return "Una vez"
    if (days.length === 7) return "Diaria"
    if (days.length === 5 && !days.includes("Sáb") && !days.includes("Dom")) return "Lun-Vie"
    if (days.length === 2 && days.includes("Sáb") && days.includes("Dom")) return "Fin de semana"
    return days.join(", ")
  }

  return (
    <AnimatePresence mode="wait">
      {isRinging && ringingAlarm && (
        <motion.div
          key="alarm-modal"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/90 backdrop-blur-sm"
          onClick={(e) => {
            // Permitir cerrar haciendo clic fuera del modal
            if (e.target === e.currentTarget) {
              dismissAlarm()
            }
          }}
        >
          <motion.div
            key={`alarm-${ringingAlarm.id}`}
            initial={{ scale: 0.8, y: 50 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.8, y: 50 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="relative w-full max-w-2xl mx-4"
          >
            {/* Glow Effect */}
            <div className="absolute inset-0 bg-cyan-400/30 blur-3xl rounded-full" />

            {/* Main Card */}
            <div className="relative backdrop-blur-md border-4 border-cyan-400 p-12 shadow-[0_0_60px_rgba(6,182,212,0.6)] bg-gradient-to-b from-black/95 to-cyan-950/50 rounded-3xl">
              
              {/* Icono de Alarma Animado */}
              <motion.div
                animate={{
                  rotate: [0, -15, 15, -15, 15, 0],
                  scale: [1, 1.1, 1, 1.1, 1],
                }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  repeatDelay: 0.5,
                }}
                className="flex justify-center mb-8"
              >
                <div className="relative">
                  <div className="absolute inset-0 bg-cyan-400/40 blur-2xl rounded-full" />
                  <Bell className="relative w-24 h-24 text-cyan-400 drop-shadow-[0_0_20px_rgba(6,182,212,1)]" />
                </div>
              </motion.div>

              {/* Título */}
              <h2 className="text-4xl font-bold text-center text-cyan-400 mb-4 drop-shadow-[0_0_15px_rgba(6,182,212,0.8)]">
                ALARMA
              </h2>

              {/* Hora de la Alarma */}
              <div className="flex items-center justify-center gap-4 mb-6">
                <Clock className="w-12 h-12 text-cyan-400/60" />
                <motion.div
                  animate={{ scale: [1, 1.05, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                  className="text-7xl font-bold font-mono text-cyan-400 drop-shadow-[0_0_20px_rgba(6,182,212,1)]"
                >
                  {ringingAlarm.time}
                </motion.div>
              </div>

              {/* Etiqueta de la Alarma */}
              <div className="text-center mb-4">
                <p className="text-3xl font-semibold text-cyan-400/90 mb-2">
                  {ringingAlarm.label}
                </p>
                
                {/* Días de Repetición */}
                {ringingAlarm.days && ringingAlarm.days.length > 0 && (
                  <div className="flex justify-center gap-2 flex-wrap">
                    {ringingAlarm.days.map((day) => (
                      <span
                        key={day}
                        className="text-sm px-3 py-1 rounded-lg bg-cyan-400/20 text-cyan-400 border border-cyan-400/30"
                      >
                        {day}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Hora Actual */}
              <div className="text-center text-cyan-400/60 text-lg font-mono mb-8">
                {currentTime}
              </div>

              {/* Botones de Acción */}
              <div className="flex gap-4 justify-center">
                {/* Botón Posponer */}
                <motion.button
                  onClick={(e) => {
                    e.stopPropagation()
                    snoozeAlarm()
                  }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="flex items-center gap-3 px-8 py-4 font-semibold text-xl bg-yellow-500/20 border-2 border-yellow-400/50 text-yellow-400 shadow-[0_0_30px_rgba(234,179,8,0.4)] rounded-xl hover:bg-yellow-500/30 transition-all"
                >
                  <Timer className="w-6 h-6" />
                  Posponer 5 min
                </motion.button>

                {/* Botón Desactivar */}
                <motion.button
                  onClick={(e) => {
                    e.stopPropagation()
                    dismissAlarm()
                  }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="flex items-center gap-3 px-8 py-4 font-semibold text-xl bg-red-500/20 border-2 border-red-400/50 text-red-400 shadow-[0_0_30px_rgba(239,68,68,0.4)] rounded-xl hover:bg-red-500/30 transition-all"
                >
                  <X className="w-6 h-6" />
                  Desactivar
                </motion.button>
              </div>

              {/* Indicación de Teclas */}
              <div className="mt-6 text-center text-cyan-400/40 text-sm">
                <p>Presiona ESC para desactivar o ESPACIO para posponer</p>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}