"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import Image from "next/image"

interface AnalogClockProps {
  timeFormat: "12h" | "24h"
  timezone?: {
    id: string
    country: string
    city: string
    offset: string
  } | null
}

export function AnalogClock({ timeFormat, timezone }: AnalogClockProps) {
  const [mounted, setMounted] = useState(false)
  const [time, setTime] = useState(new Date())

  const getAdjustedTime = (): Date => {
    if (!timezone) {
      return new Date()
    }

    const offsetStr = timezone.offset.replace("UTC", "").trim()
    let offsetHours = 0
    let offsetMinutes = 0

    if (offsetStr.includes(':')) {
      const [hours, minutes] = offsetStr.split(':')
      offsetHours = parseInt(hours)
      offsetMinutes = parseInt(minutes)
    } else {
      offsetHours = parseInt(offsetStr)
    }

    const sign = offsetHours >= 0 ? 1 : -1
    const totalOffsetMinutes = (Math.abs(offsetHours) * 60 + offsetMinutes) * sign

    const now = new Date()
    const utcTime = now.getTime() + (now.getTimezoneOffset() * 60000)
    
    return new Date(utcTime + (totalOffsetMinutes * 60000))
  }

  useEffect(() => {
    setMounted(true)
    
    const timer = setInterval(() => {
      setTime(getAdjustedTime())
    }, 1000)

    return () => clearInterval(timer)
  }, [timezone])

  if (!mounted) {
    return (
      <div className="relative flex flex-col items-center justify-center">
        <div className="mb-6 text-cyan-400 text-4xl font-bold tracking-wider">
          <span className="drop-shadow-[0_0_30px_rgba(6,182,212,1)] drop-shadow-[0_0_60px_rgba(6,182,212,0.8)] drop-shadow-[0_0_90px_rgba(6,182,212,0.6)]">
            --:--:--
          </span>
        </div>
        <div className="relative w-[350px] h-[350px]">
          <div className="absolute inset-0 bg-cyan-400/30 blur-[100px] rounded-full animate-pulse" />
        </div>
      </div>
    )
  }

  const seconds = time.getSeconds()
  const minutes = time.getMinutes()
  const hours = time.getHours() % 12

  const secondAngle = seconds * 6
  const minuteAngle = minutes * 6 + seconds * 0.1
  const hourAngle = hours * 30 + minutes * 0.5

  const formatTime = () => {
    if (timeFormat === "12h") {
      const hours12 = time.getHours() % 12 || 12
      const minutes = time.getMinutes().toString().padStart(2, "0")
      const seconds = time.getSeconds().toString().padStart(2, "0")
      const ampm = time.getHours() >= 12 ? "PM" : "AM"
      return `${hours12}:${minutes}:${seconds} ${ampm}`
    } else {
      const hours = time.getHours().toString().padStart(2, "0")
      const minutes = time.getMinutes().toString().padStart(2, "0")
      const seconds = time.getSeconds().toString().padStart(2, "0")
      return `${hours}:${minutes}:${seconds}`
    }
  }

  return (
    <div className="relative flex flex-col items-center justify-center">
      {timezone && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-2 text-cyan-400/80 text-sm font-medium"
        >
          {timezone.city}, {timezone.country} ({timezone.offset})
        </motion.div>
      )}

      <div className="mb-6 text-cyan-400 text-4xl font-bold tracking-wider">
        <span 
          className="drop-shadow-[0_0_30px_rgba(6,182,212,1)] drop-shadow-[0_0_60px_rgba(6,182,212,0.8)] drop-shadow-[0_0_90px_rgba(6,182,212,0.6)]"
          suppressHydrationWarning
        >
          {formatTime()}
        </span>
      </div>

      <div className="relative w-[350px] h-[350px]">
        <div className="absolute inset-0 bg-cyan-400/30 blur-[100px] rounded-full animate-pulse" />
        <div
          className="absolute inset-6 bg-cyan-400/40 blur-[80px] rounded-full animate-pulse"
          style={{ animationDelay: "0.3s" }}
        />
        <div
          className="absolute inset-12 bg-cyan-400/50 blur-[60px] rounded-full animate-pulse"
          style={{ animationDelay: "0.6s" }}
        />

        <div className="absolute inset-0 flex items-center justify-center">
          <div className="relative w-full h-full">
            <Image
              src="/images/clock-face-clean.png"
              alt="Clock Face"
              fill
              className="object-contain drop-shadow-[0_0_40px_rgba(6,182,212,1)] drop-shadow-[0_0_80px_rgba(6,182,212,0.8)] drop-shadow-[0_0_120px_rgba(6,182,212,0.6)]"
              priority
            />
          </div>
        </div>

        <div className="absolute inset-0 flex items-center justify-center mt-0">
          <motion.div
            className="absolute top-1/2 left-1/2 origin-bottom z-20"
            style={{
              width: "8px",
              height: "25%",
              marginLeft: "-4px",
              marginTop: "-25%",
            }}
            animate={{ rotate: hourAngle }}
            transition={{ duration: 0.5, ease: "linear" }}
          >
            <div className="w-full h-full bg-gradient-to-t from-cyan-500 via-cyan-400 to-cyan-300 rounded-full shadow-[0_0_20px_rgba(6,182,212,1),0_0_40px_rgba(6,182,212,0.9),0_0_60px_rgba(6,182,212,0.7)]" />
          </motion.div>

          <motion.div
            className="absolute top-1/2 left-1/2 origin-bottom z-25"
            style={{
              width: "6px",
              height: "35%",
              marginLeft: "-3px",
              marginTop: "-35%",
            }}
            animate={{ rotate: minuteAngle }}
            transition={{ duration: 0.5, ease: "linear" }}
          >
            <div className="w-full h-full bg-gradient-to-t from-cyan-400 via-cyan-300 to-cyan-200 rounded-full shadow-[0_0_20px_rgba(6,182,212,1),0_0_40px_rgba(6,182,212,0.9),0_0_60px_rgba(6,182,212,0.7)]" />
          </motion.div>

          <motion.div
            className="absolute top-1/2 left-1/2 origin-bottom z-30"
            style={{
              width: "4px",
              height: "35%",
              marginLeft: "-2px",
              marginTop: "-35%",
            }}
            animate={{ rotate: secondAngle }}
            transition={{ duration: 0.5, ease: "linear" }}
          >
            <div className="w-full h-full bg-gradient-to-t from-red-500 via-red-400 to-red-300 rounded-full shadow-[0_0_15px_rgba(239,68,68,1),0_0_30px_rgba(239,68,68,0.9),0_0_45px_rgba(239,68,68,0.7)]" />
          </motion.div>

          <div className="absolute top-1/2 left-1/2 w-3 h-3 bg-cyan-400 rounded-full -translate-x-1/2 -translate-y-1/2 shadow-[0_0_20px_rgba(6,182,212,1),0_0_40px_rgba(6,182,212,0.9),0_0_60px_rgba(6,182,212,0.7)] z-40" />
        </div>
      </div>
    </div>
  )
}

// ✅ BACKGROUNDTIME CON TIMEZONE
AnalogClock.BackgroundTime = function BackgroundTime({ 
  timeFormat,
  timezone 
}: { 
  timeFormat: "12h" | "24h"
  timezone?: { offset: string } | null
}) {
  const [mounted, setMounted] = useState(false)
  const [time, setTime] = useState(new Date())

  const getAdjustedTime = (): Date => {
    if (!timezone) {
      return new Date()
    }

    const offsetStr = timezone.offset.replace("UTC", "").trim()
    let offsetHours = 0
    let offsetMinutes = 0

    if (offsetStr.includes(':')) {
      const [hours, minutes] = offsetStr.split(':')
      offsetHours = parseInt(hours)
      offsetMinutes = parseInt(minutes)
    } else {
      offsetHours = parseInt(offsetStr)
    }

    const sign = offsetHours >= 0 ? 1 : -1
    const totalOffsetMinutes = (Math.abs(offsetHours) * 60 + offsetMinutes) * sign

    const now = new Date()
    const utcTime = now.getTime() + (now.getTimezoneOffset() * 60000)
    
    return new Date(utcTime + (totalOffsetMinutes * 60000))
  }

  useEffect(() => {
    setMounted(true)
    
    const timer = setInterval(() => {
      setTime(getAdjustedTime())
    }, 1000)

    return () => clearInterval(timer)
  }, [timezone])

  if (!mounted) {
    return (
      <div className="flex gap-8 text-[15rem] font-bold text-cyan-400/[0.03] font-mono leading-none">
        <span>--</span>
        <span>:</span>
        <span>--</span>
        <span>:</span>
        <span>--</span>
      </div>
    )
  }

  const hours = time.getHours().toString().padStart(2, "0")
  const minutes = time.getMinutes().toString().padStart(2, "0")
  const seconds = time.getSeconds().toString().padStart(2, "0")

  return (
    <div className="flex gap-8 text-[15rem] font-bold text-cyan-400/[0.03] font-mono leading-none" suppressHydrationWarning>
      <span suppressHydrationWarning>{hours}</span>
      <span>:</span>
      <span suppressHydrationWarning>{minutes}</span>
      <span>:</span>
      <span suppressHydrationWarning>{seconds}</span>
    </div>
  )
}