"use client"

import type * as React from "react"
import { motion } from "framer-motion"
import { Clock, Globe, Timer, Bell, Settings } from "lucide-react"

interface MenuItem {
  icon: React.ReactNode
  label: string
  id: string
  gradient: string
  iconColor: string
}

const menuItems: MenuItem[] = [
  {
    icon: <Clock className="h-5 w-5" />,
    label: "Reloj Principal",
    id: "main-clock",
    gradient: "radial-gradient(circle, rgba(6,182,212,0.3) 0%, rgba(8,145,178,0.15) 50%, rgba(21,94,117,0) 100%)",
    iconColor: "text-cyan-400",
  },
  {
    icon: <Globe className="h-5 w-5" />,
    label: "Zonas Horarias",
    id: "time-zones",
    gradient: "radial-gradient(circle, rgba(6,182,212,0.3) 0%, rgba(8,145,178,0.15) 50%, rgba(21,94,117,0) 100%)",
    iconColor: "text-cyan-400",
  },
  {
    icon: <Timer className="h-5 w-5" />,
    label: "Cronómetro",
    id: "stopwatch",
    gradient: "radial-gradient(circle, rgba(6,182,212,0.3) 0%, rgba(8,145,178,0.15) 50%, rgba(21,94,117,0) 100%)",
    iconColor: "text-cyan-400",
  },
  {
    icon: <Bell className="h-5 w-5" />,
    label: "Alarmas",
    id: "alarms",
    gradient: "radial-gradient(circle, rgba(6,182,212,0.3) 0%, rgba(8,145,178,0.15) 50%, rgba(21,94,117,0) 100%)",
    iconColor: "text-cyan-400",
  },
  {
    icon: <Settings className="h-5 w-5" />,
    label: "Configuración",
    id: "settings",
    gradient: "radial-gradient(circle, rgba(6,182,212,0.3) 0%, rgba(8,145,178,0.15) 50%, rgba(21,94,117,0) 100%)",
    iconColor: "text-cyan-400",
  },
]

const itemVariants = {
  initial: { rotateX: 0, opacity: 1 },
  hover: { rotateX: -90, opacity: 0 },
}

const backVariants = {
  initial: { rotateX: 90, opacity: 0 },
  hover: { rotateX: 0, opacity: 1 },
}

const glowVariants = {
  initial: (isActive: boolean) => ({
    opacity: isActive ? 1 : 0,
    scale: isActive ? 2 : 0.8,
  }),
  hover: {
    opacity: 1,
    scale: 2,
    transition: {
      opacity: { duration: 0.5, ease: [0.4, 0, 0.2, 1] },
      scale: { duration: 0.5, type: "spring", stiffness: 300, damping: 25 },
    },
  },
}

const navGlowVariants = {
  initial: { opacity: 0 },
  hover: {
    opacity: 1,
    transition: {
      duration: 0.5,
      ease: [0.4, 0, 0.2, 1],
    },
  },
}

const sharedTransition = {
  type: "spring",
  stiffness: 100,
  damping: 20,
  duration: 0.5,
}

interface ClockNavbarProps {
  activeSection: string
  onSectionChange: (section: string) => void
}

export function ClockNavbar({ activeSection, onSectionChange }: ClockNavbarProps) {
  const activeIndex = menuItems.findIndex((item) => item.id === activeSection)

  return (
    <motion.nav
      className="p-2 bg-black/80 backdrop-blur-lg border border-cyan-500/20 shadow-cyan-500/20 relative overflow-hidden w-full max-w-7xl mx-auto border-none shadow-xl rounded-full"
      initial="initial"
      whileHover="hover"
    >
      <motion.div
        className="absolute -inset-2 bg-gradient-radial from-transparent via-cyan-400/20 via-50% to-transparent rounded-3xl z-0 pointer-events-none"
        variants={navGlowVariants}
      />
      <motion.div
        className="absolute top-0 bottom-0 rounded-xl pointer-events-none z-0"
        style={{
          background:
            "radial-gradient(ellipse, rgba(6,182,212,0.35) 0%, rgba(6,182,212,0.2) 30%, rgba(8,145,178,0.1) 60%, rgba(21,94,117,0) 100%)",
          filter: "blur(20px)",
        }}
        initial={false}
        animate={{
          left: `${(activeIndex / menuItems.length) * 100}%`,
          width: `${100 / menuItems.length}%`,
        }}
        transition={{
          type: "spring",
          stiffness: 250,
          damping: 25,
          duration: 0.7,
        }}
      />
      <ul className="flex items-center justify-around gap-2 relative z-10">
        {menuItems.map((item) => {
          const isActive = activeSection === item.id
          return (
            <motion.li key={item.label} className="relative flex-1">
              <motion.div
                className="block rounded-xl overflow-visible group relative"
                style={{ perspective: "600px" }}
                whileHover="hover"
                initial="initial"
              >
                <motion.button
                  onClick={() => onSectionChange(item.id)}
                  className={`flex items-center justify-center gap-2 px-6 py-4 relative z-10 bg-transparent transition-colors rounded-xl w-full ${
                    isActive ? "text-cyan-400" : "text-gray-400"
                  } group-hover:text-cyan-400`}
                  variants={itemVariants}
                  transition={sharedTransition}
                  style={{ transformStyle: "preserve-3d", transformOrigin: "center bottom" }}
                >
                  <span className="transition-colors duration-300">{item.icon}</span>
                  <span className="text-sm font-medium whitespace-nowrap">{item.label}</span>
                </motion.button>
                <motion.button
                  onClick={() => onSectionChange(item.id)}
                  className={`flex items-center justify-center gap-2 px-6 py-4 absolute inset-0 z-10 bg-transparent transition-colors rounded-xl w-full ${
                    isActive ? "text-cyan-400" : "text-gray-400"
                  } group-hover:text-cyan-400`}
                  variants={backVariants}
                  transition={sharedTransition}
                  style={{ transformStyle: "preserve-3d", transformOrigin: "center top", rotateX: 90 }}
                >
                  <span className="transition-colors duration-300">{item.icon}</span>
                  <span className="text-sm font-medium whitespace-nowrap">{item.label}</span>
                </motion.button>
              </motion.div>
            </motion.li>
          )
        })}
      </ul>
    </motion.nav>
  )
}
