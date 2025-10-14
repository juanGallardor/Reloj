"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Plus, Trash2, Bell, Clock, Edit2, Check, X, Loader2 } from "lucide-react"
import { alarmsAPI, type Alarm } from "@/lib/api"

export function Alarms() {
  const [alarms, setAlarms] = useState<Alarm[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showAddForm, setShowAddForm] = useState(false)
  const [newAlarmTime, setNewAlarmTime] = useState("08:00")
  const [newAlarmLabel, setNewAlarmLabel] = useState("")
  const [newAlarmDays, setNewAlarmDays] = useState<string[]>([])
  const [editingAlarmId, setEditingAlarmId] = useState<number | null>(null)
  const [editTime, setEditTime] = useState("")
  const [editLabel, setEditLabel] = useState("")
  const [editDays, setEditDays] = useState<string[]>([])

  const weekDays = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

  // ========================================================================
  // CARGAR ALARMAS DESDE EL BACKEND
  // ========================================================================
  
  useEffect(() => {
    loadAlarms()
  }, [])

  const loadAlarms = async () => {
    try {
      setIsLoading(true)
      const alarmsData = await alarmsAPI.getAll()
      setAlarms(alarmsData)
      console.log('✅ Alarmas cargadas:', alarmsData.length)
    } catch (error) {
      console.error('❌ Error cargando alarmas:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // ========================================================================
  // TOGGLE DÍA
  // ========================================================================
  
  const toggleDay = (day: string, isEditing = false) => {
    if (isEditing) {
      setEditDays((prev) => (prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day]))
    } else {
      setNewAlarmDays((prev) => (prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day]))
    }
  }

  // ========================================================================
  // AGREGAR ALARMA
  // ========================================================================
  
  const handleAddAlarm = async () => {
    if (!newAlarmTime) return

    try {
      const newAlarm = await alarmsAPI.create({
        time: newAlarmTime,
        label: newAlarmLabel || "Nueva Alarma",
        enabled: true,
        days: newAlarmDays,
      })

      setAlarms([...alarms, newAlarm])
      setShowAddForm(false)
      setNewAlarmTime("08:00")
      setNewAlarmLabel("")
      setNewAlarmDays([])

      console.log('✅ Alarma creada:', newAlarm)
    } catch (error) {
      console.error('❌ Error creando alarma:', error)
      alert('Error al crear la alarma')
    }
  }

  // ========================================================================
  // EDITAR ALARMA
  // ========================================================================
  
  const startEditing = (alarm: Alarm) => {
    setEditingAlarmId(alarm.id)
    setEditTime(alarm.time)
    setEditLabel(alarm.label)
    setEditDays(alarm.days)
  }

  const saveEdit = async () => {
    if (editingAlarmId === null) return

    try {
      const updatedAlarm = await alarmsAPI.update(editingAlarmId, {
        time: editTime,
        label: editLabel,
        days: editDays,
      })

      setAlarms(alarms.map((alarm) => (alarm.id === editingAlarmId ? updatedAlarm : alarm)))
      setEditingAlarmId(null)

      console.log('✅ Alarma actualizada:', updatedAlarm)
    } catch (error) {
      console.error('❌ Error actualizando alarma:', error)
      alert('Error al actualizar la alarma')
    }
  }

  const cancelEdit = () => {
    setEditingAlarmId(null)
  }

  // ========================================================================
  // ELIMINAR ALARMA
  // ========================================================================
  
  const handleDeleteAlarm = async (id: number) => {
    try {
      await alarmsAPI.delete(id)
      setAlarms(alarms.filter((alarm) => alarm.id !== id))
      console.log('✅ Alarma eliminada:', id)
    } catch (error) {
      console.error('❌ Error eliminando alarma:', error)
      alert('Error al eliminar la alarma')
    }
  }

  // ========================================================================
  // TOGGLE ALARMA (ACTIVAR/DESACTIVAR)
  // ========================================================================
  
  const handleToggleAlarm = async (id: number) => {
    try {
      const updatedAlarm = await alarmsAPI.toggle(id)
      setAlarms(alarms.map((alarm) => (alarm.id === id ? updatedAlarm : alarm)))
      console.log('✅ Alarma toggled:', updatedAlarm)
    } catch (error) {
      console.error('❌ Error toggling alarma:', error)
      alert('Error al cambiar estado de la alarma')
    }
  }

  // ========================================================================
  // LOADING STATE
  // ========================================================================
  
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 min-h-[400px]">
        <Loader2 className="w-12 h-12 text-cyan-400 animate-spin" />
        <p className="text-cyan-400/60">Cargando alarmas...</p>
      </div>
    )
  }

  // ========================================================================
  // RENDER
  // ========================================================================
  
  return (
    <div className="flex flex-col items-center gap-8 w-full max-w-3xl mx-auto">
      <div className="flex items-center justify-between w-full">
        <h2 className="text-3xl font-bold text-cyan-400 drop-shadow-[0_0_10px_rgba(6,182,212,0.8)]">
          Alarmas ({alarms.length})
        </h2>
        <motion.button
          onClick={() => setShowAddForm(!showAddForm)}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="flex items-center gap-2 px-6 py-3 rounded-xl font-semibold bg-cyan-400/20 border-2 border-cyan-400/50 text-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.4)]"
        >
          <Plus className="w-5 h-5" />
          Agregar
        </motion.button>
      </div>

      {/* FORMULARIO AGREGAR ALARMA */}
      <AnimatePresence>
        {showAddForm && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="w-full backdrop-blur-sm border-2 border-cyan-400/50 p-6 shadow-[0_0_30px_rgba(6,182,212,0.3)] rounded-none border-solid bg-black"
          >
            <div className="space-y-4">
              <div>
                <label className="block text-cyan-400 text-sm font-semibold mb-2">Hora</label>
                <input
                  type="time"
                  value={newAlarmTime}
                  onChange={(e) => setNewAlarmTime(e.target.value)}
                  className="w-full bg-black/40 border-2 border-cyan-400/30 rounded-lg px-4 py-3 text-cyan-400 text-2xl font-mono focus:outline-none focus:border-cyan-400/60"
                />
              </div>
              <div>
                <label className="block text-cyan-400 text-sm font-semibold mb-2">Etiqueta</label>
                <input
                  type="text"
                  value={newAlarmLabel}
                  onChange={(e) => setNewAlarmLabel(e.target.value)}
                  placeholder="Ej: Despertar, Reunión..."
                  className="w-full bg-black/40 border-2 border-cyan-400/30 rounded-lg px-4 py-3 text-cyan-400 focus:outline-none focus:border-cyan-400/60 placeholder:text-cyan-400/30"
                />
              </div>
              <div>
                <label className="block text-cyan-400 text-sm font-semibold mb-2">Repetir</label>
                
                {/* Botón Todos los días */}
                <button
                  onClick={() => {
                    if (newAlarmDays.length === 7) {
                      setNewAlarmDays([]) // Deseleccionar todos
                    } else {
                      setNewAlarmDays(weekDays) // Seleccionar todos
                    }
                  }}
                  className="mb-3 px-4 py-2 rounded-lg border-2 bg-cyan-400/10 border-cyan-400/50 text-cyan-400 hover:bg-cyan-400/20 transition-all"
                >
                  {newAlarmDays.length === 7 ? '❌ Quitar todos' : '✅ Todos los días'}
                </button>

                <div className="flex gap-2 flex-wrap">
                  {weekDays.map((day) => (
                    <button
                      key={day}
                      onClick={() => toggleDay(day)}
                      className={`px-4 py-2 rounded-lg border-2 transition-all ${
                        newAlarmDays.includes(day)
                          ? "bg-cyan-400/30 border-cyan-400 text-cyan-400 shadow-[0_0_10px_rgba(6,182,212,0.4)]"
                          : "bg-black/40 border-cyan-400/30 text-cyan-400/50"
                      }`}
                    >
                      {day}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex gap-3 justify-end">
                <button
                  onClick={() => setShowAddForm(false)}
                  className="px-6 py-2 rounded-lg bg-gray-500/20 border border-gray-400/50 text-gray-400"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleAddAlarm}
                  className="px-6 py-2 rounded-lg bg-cyan-400/20 border border-cyan-400/50 text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.3)]"
                >
                  Guardar
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* LISTA DE ALARMAS */}
      <div className="w-full space-y-4">
        <AnimatePresence>
          {alarms.map((alarm) => (
            <motion.div
              key={alarm.id}
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, x: -100 }}
              className={`backdrop-blur-sm border-2 p-6 shadow-[0_0_20px_rgba(6,182,212,0.2)] transition-all rounded-4xl border-solid bg-black ${
                alarm.enabled ? "border-cyan-400/50" : "border-gray-400/30"
              }`}
            >
              {editingAlarmId === alarm.id ? (
                // MODO EDICIÓN
                <div className="space-y-4">
                  <div>
                    <label className="block text-cyan-400 text-sm font-semibold mb-2">Hora</label>
                    <input
                      type="time"
                      value={editTime}
                      onChange={(e) => setEditTime(e.target.value)}
                      className="w-full bg-black/40 border-2 border-cyan-400/30 rounded-lg px-4 py-3 text-cyan-400 text-2xl font-mono focus:outline-none focus:border-cyan-400/60"
                    />
                  </div>
                  <div>
                    <label className="block text-cyan-400 text-sm font-semibold mb-2">Etiqueta</label>
                    <input
                      type="text"
                      value={editLabel}
                      onChange={(e) => setEditLabel(e.target.value)}
                      className="w-full bg-black/40 border-2 border-cyan-400/30 rounded-lg px-4 py-3 text-cyan-400 focus:outline-none focus:border-cyan-400/60"
                    />
                  </div>
                  <div>
                    <label className="block text-cyan-400 text-sm font-semibold mb-2">Repetir</label>
                    <div className="flex gap-2 flex-wrap">
                      {weekDays.map((day) => (
                        <button
                          key={day}
                          onClick={() => toggleDay(day, true)}
                          className={`px-4 py-2 rounded-lg border-2 transition-all ${
                            editDays.includes(day)
                              ? "bg-cyan-400/30 border-cyan-400 text-cyan-400 shadow-[0_0_10px_rgba(6,182,212,0.4)]"
                              : "bg-black/40 border-cyan-400/30 text-cyan-400/50"
                          }`}
                        >
                          {day}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className="flex gap-3 justify-end">
                    <button
                      onClick={cancelEdit}
                      className="p-3 rounded-lg bg-gray-500/20 border border-gray-400/50 text-gray-400"
                    >
                      <X className="w-5 h-5" />
                    </button>
                    <button
                      onClick={saveEdit}
                      className="p-3 rounded-lg bg-cyan-400/20 border border-cyan-400/50 text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.3)]"
                    >
                      <Check className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              ) : (
                // MODO VISUALIZACIÓN
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-6">
                    <button
                      onClick={() => handleToggleAlarm(alarm.id)}
                      className={`w-16 h-16 rounded-full flex items-center justify-center transition-all ${
                        alarm.enabled
                          ? "bg-cyan-400/20 border-2 border-cyan-400/50 shadow-[0_0_20px_rgba(6,182,212,0.4)]"
                          : "bg-gray-500/20 border-2 border-gray-400/30"
                      }`}
                    >
                      <Bell className={`w-7 h-7 ${alarm.enabled ? "text-cyan-400" : "text-gray-400"}`} />
                    </button>
                    <div>
                      <div className="flex items-baseline gap-3">
                        <span
                          className={`text-5xl font-bold font-mono ${
                            alarm.enabled ? "text-cyan-400 drop-shadow-[0_0_10px_rgba(6,182,212,0.8)]" : "text-gray-400"
                          }`}
                        >
                          {alarm.time}
                        </span>
                        <Clock className={`w-6 h-6 ${alarm.enabled ? "text-cyan-400/60" : "text-gray-400/60"}`} />
                      </div>
                      <p className={`text-lg mt-1 ${alarm.enabled ? "text-cyan-400/80" : "text-gray-400/60"}`}>
                        {alarm.label}
                      </p>
                      {alarm.days.length > 0 && (
                        <div className="flex gap-2 mt-2">
                          {alarm.days.map((day) => (
                            <span
                              key={day}
                              className={`text-xs px-2 py-1 rounded ${
                                alarm.enabled
                                  ? "bg-cyan-400/20 text-cyan-400 border border-cyan-400/30"
                                  : "bg-gray-500/20 text-gray-400 border border-gray-400/30"
                              }`}
                            >
                              {day}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <motion.button
                      onClick={() => startEditing(alarm)}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      className="p-3 rounded-lg bg-cyan-500/20 border border-cyan-400/50 text-cyan-400 hover:shadow-[0_0_15px_rgba(6,182,212,0.4)] transition-all"
                    >
                      <Edit2 className="w-5 h-5" />
                    </motion.button>
                    <motion.button
                      onClick={() => handleDeleteAlarm(alarm.id)}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      className="p-3 rounded-lg bg-red-500/20 border border-red-400/50 text-red-400 hover:shadow-[0_0_15px_rgba(239,68,68,0.4)] transition-all"
                    >
                      <Trash2 className="w-5 h-5" />
                    </motion.button>
                  </div>
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {alarms.length === 0 && (
          <div className="text-center py-12 text-cyan-400/50">
            <Bell className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p className="text-lg">No hay alarmas configuradas</p>
            <p className="text-sm mt-2">Haz clic en "Agregar" para crear una alarma</p>
          </div>
        )}
      </div>
    </div>
  )
}