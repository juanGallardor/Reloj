"use client"

import { motion, AnimatePresence } from "framer-motion"
import { Play, Pause, RotateCcw, Flag } from "lucide-react"
import { useStopwatch } from "@/contexts/stopwatch-context"

export function Stopwatch() {
  // ✅ USAR EL HOOK DEL CONTEXTO GLOBAL
  const { time, isRunning, laps, startStop, reset, addLap, formatTime } = useStopwatch()

  const formatTimeString = (milliseconds: number) => {
    const formatted = formatTime(milliseconds)
    return `${formatted.hours}:${formatted.minutes}:${formatted.seconds}.${formatted.milliseconds}`
  }

  const formattedTime = formatTime(time)

  return (
    <div className="flex flex-col items-center gap-8">
      {/* Time display - SIN ANIMACIONES EN LOS NÚMEROS PARA EVITAR DUPLICACIÓN */}
      <div className="relative">
        <div className="absolute inset-0 bg-cyan-400/20 blur-3xl rounded-full" />
        <div className="relative backdrop-blur-sm border-2 border-cyan-400/50 px-12 py-8 shadow-[0_0_30px_rgba(6,182,212,0.3)] rounded-xs border-none shadow-none bg-transparent">
          <div className="flex items-center gap-2 text-cyan-400 font-mono">
            <span className="text-7xl font-bold drop-shadow-[0_0_15px_rgba(6,182,212,1)]">
              {formattedTime.hours}
            </span>
            <span className="text-7xl font-bold drop-shadow-[0_0_15px_rgba(6,182,212,1)]">:</span>
            <span className="text-7xl font-bold drop-shadow-[0_0_15px_rgba(6,182,212,1)]">
              {formattedTime.minutes}
            </span>
            <span className="text-7xl font-bold drop-shadow-[0_0_15px_rgba(6,182,212,1)]">:</span>
            <span className="text-7xl font-bold drop-shadow-[0_0_15px_rgba(6,182,212,1)]">
              {formattedTime.seconds}
            </span>
            <span className="text-4xl font-bold drop-shadow-[0_0_10px_rgba(6,182,212,0.8)] ml-2">
              .{formattedTime.milliseconds}
            </span>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-6">
        <motion.button
          onClick={startStop}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className={`flex items-center gap-3 px-8 py-4 font-semibold text-lg transition-all rounded-xl ${
            isRunning
              ? "bg-red-500/20 border-2 border-red-400/50 text-red-400 shadow-[0_0_20px_rgba(239,68,68,0.4)]"
              : "bg-cyan-400/20 border-2 border-cyan-400/50 text-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.4)]"
          }`}
        >
          {isRunning ? (
            <>
              <Pause className="w-6 h-6" />
              Pausar
            </>
          ) : (
            <>
              <Play className="w-6 h-6" />
              Iniciar
            </>
          )}
        </motion.button>

        <motion.button
          onClick={addLap}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          disabled={time === 0}
          className="flex items-center gap-3 px-8 py-4 font-semibold text-lg bg-cyan-400/20 border-2 border-cyan-400/50 text-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.4)] transition-all disabled:opacity-50 disabled:cursor-not-allowed rounded-xl"
        >
          <Flag className="w-6 h-6" />
          Vuelta
        </motion.button>

        <motion.button
          onClick={reset}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          disabled={time === 0}
          className="flex items-center gap-3 px-8 py-4 font-semibold text-lg bg-gray-500/20 border-2 border-gray-400/50 text-gray-400 shadow-[0_0_20px_rgba(156,163,175,0.3)] transition-all disabled:opacity-50 disabled:cursor-not-allowed rounded-xl"
        >
          <RotateCcw className="w-6 h-6" />
          Reiniciar
        </motion.button>
      </div>

      {/* Indicator cuando el cronómetro está corriendo */}
      {isRunning && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex items-center gap-2 text-cyan-400/80 text-sm"
        >
          <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          <span>Cronómetro activo</span>
        </motion.div>
      )}

      {/* Lista de Laps */}
      <AnimatePresence>
        {laps.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="w-full max-w-2xl mt-4"
          >
            <div className="backdrop-blur-sm border-2 border-cyan-400/30 p-6 shadow-[0_0_20px_rgba(6,182,212,0.2)] bg-black/40 rounded-xs">
              <h3 className="text-xl font-semibold text-cyan-400 mb-4 drop-shadow-[0_0_8px_rgba(6,182,212,0.8)]">
                Registros ({laps.length})
              </h3>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                <AnimatePresence>
                  {laps.map((lap, index) => (
                    <motion.div
                      key={lap.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      transition={{ delay: index * 0.05 }}
                      className="flex items-center justify-between p-3 border border-cyan-400/20 rounded-lg hover:bg-cyan-400/10 transition-all border-none bg-transparent"
                    >
                      <span className="text-cyan-400/80 font-semibold">Vuelta {lap.id}</span>
                      <div className="flex gap-6 font-mono">
                        <span className="text-cyan-400">{formatTimeString(lap.lapTime)}</span>
                        <span className="text-cyan-400/60">{formatTimeString(lap.time)}</span>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}