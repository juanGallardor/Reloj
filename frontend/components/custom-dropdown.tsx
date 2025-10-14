"use client"

import { useState, useRef, useEffect } from "react"
import { createPortal } from "react-dom"
import { motion, AnimatePresence } from "framer-motion"
import { ChevronDown, Check } from "lucide-react"

interface DropdownOption {
  value: string
  label: string
}

interface CustomDropdownProps {
  options: DropdownOption[]
  value: string
  onChange: (value: string) => void
  placeholder?: string
  disabled?: boolean
  className?: string
}

export function CustomDropdown({ options, value, onChange, placeholder, disabled, className }: CustomDropdownProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [mounted, setMounted] = useState(false)
  const buttonRef = useRef<HTMLButtonElement>(null)
  const [buttonRect, setButtonRect] = useState<DOMRect | null>(null)

  const selectedOption = options.find((opt) => opt.value === value)

  // Montar en cliente
  useEffect(() => {
    setMounted(true)
  }, [])

  // Actualizar posición cuando se abre
  useEffect(() => {
    if (isOpen && buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect()
      setButtonRect(rect)
    }
  }, [isOpen])

  // Cerrar al hacer clic fuera
  useEffect(() => {
    if (!isOpen) return

    const handleClickOutside = (event: MouseEvent) => {
      if (buttonRef.current && !buttonRef.current.contains(event.target as Node)) {
        const dropdownMenu = document.getElementById('dropdown-portal-menu')
        if (dropdownMenu && !dropdownMenu.contains(event.target as Node)) {
          setIsOpen(false)
        }
      }
    }

    const handleScroll = () => {
      if (buttonRef.current) {
        const rect = buttonRef.current.getBoundingClientRect()
        setButtonRect(rect)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    window.addEventListener("scroll", handleScroll, true)
    
    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
      window.removeEventListener("scroll", handleScroll, true)
    }
  }, [isOpen])

  const dropdownMenu = isOpen && buttonRect && mounted ? createPortal(
    <AnimatePresence>
      <motion.div
        id="dropdown-portal-menu"
        initial={{ opacity: 0, y: -10, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -10, scale: 0.95 }}
        transition={{ duration: 0.2 }}
        style={{
          position: 'fixed',
          top: `${buttonRect.bottom + 8}px`,
          left: `${buttonRect.left}px`,
          width: `${buttonRect.width}px`,
          zIndex: 999999, // 🔥 Z-INDEX SÚPER ALTO
        }}
        className="bg-black/95 backdrop-blur-md border-2 border-cyan-400/50 rounded-xl shadow-[0_0_30px_rgba(6,182,212,0.4)] overflow-hidden"
      >
        <div className="max-h-64 overflow-y-auto custom-scrollbar">
          {options.length === 0 ? (
            <div className="px-4 py-3 text-cyan-400/60 text-center text-sm">
              No hay opciones disponibles
            </div>
          ) : (
            options.map((option, index) => (
              <motion.button
                key={option.value}
                type="button"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.03 }}
                onClick={() => {
                  onChange(option.value)
                  setIsOpen(false)
                }}
                className={`w-full px-4 py-3 text-left flex items-center justify-between transition-all ${
                  option.value === value
                    ? "bg-cyan-400/30 text-cyan-400 shadow-[inset_0_0_20px_rgba(6,182,212,0.3)]"
                    : "text-cyan-400/80 hover:bg-cyan-400/20 hover:text-cyan-400"
                }`}
              >
                <span className="text-lg">{option.label}</span>
                {option.value === value && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="text-cyan-400 drop-shadow-[0_0_8px_rgba(6,182,212,1)]"
                  >
                    <Check className="w-5 h-5" />
                  </motion.div>
                )}
              </motion.button>
            ))
          )}
        </div>
      </motion.div>
    </AnimatePresence>,
    document.body
  ) : null

  return (
    <>
      <div className={`relative ${className}`}>
        <button
          ref={buttonRef}
          type="button"
          onClick={() => !disabled && setIsOpen(!isOpen)}
          disabled={disabled}
          className={`w-full border-2 px-4 py-3 text-left flex items-center justify-between rounded-xl transition-all ${
            disabled
              ? "opacity-50 cursor-not-allowed border-cyan-400/20"
              : isOpen
                ? "border-cyan-400 shadow-[0_0_25px_rgba(6,182,212,0.4)]"
                : "border-cyan-400/40 hover:border-cyan-400/60 hover:shadow-[0_0_15px_rgba(6,182,212,0.2)]"
          }`}
        >
          <span className={`text-lg ${selectedOption ? "text-cyan-400" : "text-cyan-400/50"}`}>
            {selectedOption ? selectedOption.label : placeholder || "Seleccionar..."}
          </span>
          <motion.div animate={{ rotate: isOpen ? 180 : 0 }} transition={{ duration: 0.2 }}>
            <ChevronDown className="w-5 h-5 text-cyan-400" />
          </motion.div>
        </button>
      </div>

      {/* Dropdown menu renderizado en el body */}
      {dropdownMenu}

      {/* Estilos globales para el scrollbar */}
      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(6, 182, 212, 0.1);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(6, 182, 212, 0.5);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(6, 182, 212, 0.7);
        }
      `}</style>
    </>
  )
}