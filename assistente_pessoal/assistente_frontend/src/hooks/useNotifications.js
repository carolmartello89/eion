import { useState, useEffect } from 'react'

export const useNotifications = () => {
  const [permission, setPermission] = useState(Notification.permission)
  const [registration, setRegistration] = useState(null)

  useEffect(() => {
    // Registra o service worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js')
        .then((reg) => {
          console.log('Service Worker registrado:', reg)
          setRegistration(reg)
        })
        .catch((error) => {
          console.error('Erro ao registrar Service Worker:', error)
        })
    }
  }, [])

  const requestPermission = async () => {
    if (!('Notification' in window)) {
      console.log('Este navegador não suporta notificações')
      return false
    }

    if (permission === 'granted') {
      return true
    }

    if (permission !== 'denied') {
      const result = await Notification.requestPermission()
      setPermission(result)
      return result === 'granted'
    }

    return false
  }

  const showNotification = (title, options = {}) => {
    if (permission !== 'granted') {
      console.log('Permissão para notificações não concedida')
      return
    }

    const defaultOptions = {
      icon: '/icon-192x192.png',
      badge: '/icon-192x192.png',
      vibrate: [100, 50, 100],
      requireInteraction: true,
      ...options
    }

    if (registration && registration.showNotification) {
      // Usa service worker para notificações mais avançadas
      registration.showNotification(title, defaultOptions)
    } else {
      // Fallback para notificações básicas
      new Notification(title, defaultOptions)
    }
  }

  const scheduleNotification = (title, options, delay) => {
    setTimeout(() => {
      showNotification(title, options)
    }, delay)
  }

  const checkCompromissos = async () => {
    try {
      const response = await fetch('/api/compromissos/alertas')
      if (response.ok) {
        const compromissos = await response.json()
        
        compromissos.forEach((compromisso) => {
          const dataCompromisso = new Date(compromisso.data_hora)
          const agora = new Date()
          const tempoRestante = dataCompromisso - agora
          const minutosRestantes = Math.floor(tempoRestante / (1000 * 60))
          
          if (minutosRestantes <= compromisso.alerta_antecedencia && minutosRestantes > 0) {
            showNotification(
              `Compromisso em ${minutosRestantes} minutos`,
              {
                body: compromisso.titulo,
                tag: `compromisso-${compromisso.id}`,
                data: { compromissoId: compromisso.id },
                actions: [
                  {
                    action: 'view',
                    title: 'Ver detalhes'
                  },
                  {
                    action: 'snooze',
                    title: 'Adiar 5 min'
                  }
                ]
              }
            )
          }
        })
      }
    } catch (error) {
      console.error('Erro ao verificar compromissos:', error)
    }
  }

  return {
    permission,
    requestPermission,
    showNotification,
    scheduleNotification,
    checkCompromissos,
    isSupported: 'Notification' in window
  }
}

