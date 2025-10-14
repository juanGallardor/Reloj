"use client"

import { useState } from "react"
import { ClockNavbar } from "@/components/clock-navbar"
import { AnalogClock } from "@/components/analog-clock"
import { TimezoneSelector } from "@/components/timezone-selector"
import { Stopwatch } from "@/components/stopwatch"
import { Alarms } from "@/components/alarms"
import { Settings } from "@/components/settings"
import { useAlarm } from "@/contexts/alarm-context"
import { FavoriteTimezone } from "@/lib/api"
import Image from "next/image"
import { motion, AnimatePresence } from "framer-motion"

export default function Page() {
  const [activeSection, setActiveSection] = useState("main-clock")
  const [timeFormat, setTimeFormat] = useState<"12h" | "24h">("24h")
  const [activeTimezone, setActiveTimezone] = useState<FavoriteTimezone | null>(null)
  
  // ✅ CONECTAR CON ALARM CONTEXT PARA USAR TIMEZONE EN ALARMAS
  const { setActiveTimezone: setAlarmTimezone } = useAlarm()

  const handleTimezoneChange = (timezone: FavoriteTimezone | null) => {
    setActiveTimezone(timezone)
    setAlarmTimezone(timezone) // ✅ Sincronizar timezone con las alarmas
    console.log("🌍 Zona horaria activa cambiada:", timezone?.city, timezone?.country)
  }

  const displayCountry = activeTimezone?.country.toUpperCase() || "COLOMBIA"
  const displayCity = activeTimezone?.city.toUpperCase() || "BOGOTÁ"

  // Convertir texto a letras separadas
  const countryLetters = displayCountry.split('')
  const cityLetters = displayCity.split('')

  return (
    <div className="min-h-screen bg-gradient-to-t from-black via-slate-950 to-cyan-950/40 flex flex-col relative overflow-hidden">
      <div className="w-full px-8 pt-4">
        <ClockNavbar activeSection={activeSection} onSectionChange={setActiveSection} />
      </div>

      {activeSection === "main-clock" && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none select-none overflow-hidden">
          <div className="absolute inset-0 flex items-center justify-center">
            <AnalogClock.BackgroundTime timeFormat={timeFormat} timezone={activeTimezone} />
          </div>
        </div>
      )}

      {activeSection === "time-zones" && (
        <>
          <div className="absolute inset-0 flex items-center justify-center opacity-5 pointer-events-none">
            <Image src="/images/world-map.png" alt="" fill className="object-cover" priority />
          </div>
          
          <div className="absolute inset-0 pointer-events-none select-none">
            <AnimatePresence mode="wait">
              <motion.div
                key={`country-${displayCountry}`}
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                className="absolute left-4 top-1/2 -translate-y-1/2 flex flex-col items-center gap-0.5"
              >
                {countryLetters.map((letter, index) => (
                  <div
                    key={`${letter}-${index}`}
                    className="text-[4rem] md:text-[5rem] lg:text-[6rem] font-black text-cyan-400/10 leading-none"
                  >
                    {letter}
                  </div>
                ))}
              </motion.div>
            </AnimatePresence>

            <AnimatePresence mode="wait">
              <motion.div
                key={`city-${displayCity}`}
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 50 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                className="absolute right-4 top-1/2 -translate-y-1/2 flex flex-col items-center gap-0.5"
              >
                {cityLetters.map((letter, index) => (
                  <div
                    key={`${letter}-${index}`}
                    className="text-[4rem] md:text-[5rem] lg:text-[6rem] font-black text-cyan-400/10 leading-none"
                  >
                    {letter}
                  </div>
                ))}
              </motion.div>
            </AnimatePresence>
          </div>
        </>
      )}

      {activeSection === "stopwatch" && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none select-none overflow-hidden opacity-[0.02]">
          <div className="text-[20rem] font-bold text-cyan-400 font-mono">00:00</div>
        </div>
      )}

      {/* ✅ BACKGROUND SIN EMOJI - SOLO TEXTO */}
      {activeSection === "alarms" && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none select-none overflow-hidden opacity-[0.02]">
          <div className="text-[15rem] font-bold text-cyan-400"></div>
        </div>
      )}

      {/* ✅ BACKGROUND SIN EMOJI - SOLO TEXTO */}
      {activeSection === "settings" && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none select-none overflow-hidden opacity-[0.02]">
          <div className="text-[12rem] font-bold text-cyan-400">⚙️</div>
        </div>
      )}

      <div className="flex-1 w-full flex items-center justify-center px-8 relative">
        <div className="relative z-10 w-full max-w-[90rem]">
          {activeSection === "main-clock" && (
            <div className="flex items-center gap-8 mt-0 flex-col">
              <AnalogClock timeFormat={timeFormat} timezone={activeTimezone} />
            </div>
          )}

          {activeSection === "time-zones" && (
            <TimezoneSelector onActiveTimezoneChange={handleTimezoneChange} />
          )}

          {activeSection === "stopwatch" && <Stopwatch />}

          {activeSection === "alarms" && <Alarms />}

          {activeSection === "settings" && <Settings timeFormat={timeFormat} onTimeFormatChange={setTimeFormat} />}
        </div>
      </div>

      {activeSection === "main-clock" && (
        <div className="w-full flex justify-center pb-0 relative">
          <div className="relative w-full max-w-2xl h-48">
            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-48 h-[500px] bg-gradient-to-t from-cyan-400/40 via-cyan-400/15 to-transparent blur-3xl pointer-events-none" />
            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-32 h-[400px] bg-gradient-to-t from-cyan-400/50 via-cyan-400/20 to-transparent blur-2xl pointer-events-none" />
            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-24 h-[300px] bg-gradient-to-t from-cyan-400/60 via-cyan-400/25 to-transparent blur-xl pointer-events-none" />

            <Image
              src="/images/apple-watch.png"
              alt="Apple Watch"
              width={500}
              height={192}
              className="absolute bottom-0 left-1/2 -translate-x-1/2 object-contain h-auto w-[500px]"
              priority
            />
          </div>
        </div>
      )}
    </div>
  )
}