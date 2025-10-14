// app/layout.tsx
import "./globals.css"
import { Jost } from "next/font/google"
import { ThemeProvider } from "@/components/theme-provider"
import { StopwatchProvider } from "@/contexts/stopwatch-context"
import { AlarmProvider } from "@/contexts/alarm-context"
import { AlarmNotification } from "@/components/alarm-notification"
import type React from "react"

const jost = Jost({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
  variable: "--font-jost",
})

export const metadata = {
  title: "Clock App - Estructuras de Datos",
  description: "Aplicación de reloj con Listas Circulares Dobles",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body className={jost.className}>
        <ThemeProvider 
          attribute="class" 
          defaultTheme="dark"
          enableSystem={false}
        >
          <StopwatchProvider>
            {/* ✅ AGREGAR EL ALARM PROVIDER */}
            <AlarmProvider>
              {children}
              
              {/* ✅ NOTIFICACIÓN GLOBAL DE ALARMAS */}
              <AlarmNotification />
            </AlarmProvider>
          </StopwatchProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}