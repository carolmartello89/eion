import { createContext, useContext, useEffect, useState } from 'react'

const ThemeContext = createContext()

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState('light')
  const [systemTheme, setSystemTheme] = useState('light')

  useEffect(() => {
    // Verifica preferência do sistema
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    setSystemTheme(mediaQuery.matches ? 'dark' : 'light')

    // Listener para mudanças na preferência do sistema
    const handleChange = (e) => {
      setSystemTheme(e.matches ? 'dark' : 'light')
    }

    mediaQuery.addEventListener('change', handleChange)

    // Carrega tema salvo ou usa o do sistema
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme && ['light', 'dark', 'system'].includes(savedTheme)) {
      setTheme(savedTheme)
    } else {
      setTheme('system')
    }

    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  useEffect(() => {
    // Aplica o tema ao documento
    const root = document.documentElement
    const effectiveTheme = theme === 'system' ? systemTheme : theme

    if (effectiveTheme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }

    // Salva no localStorage
    localStorage.setItem('theme', theme)
  }, [theme, systemTheme])

  const setThemeAndSave = (newTheme) => {
    setTheme(newTheme)
  }

  const toggleTheme = () => {
    const currentEffective = theme === 'system' ? systemTheme : theme
    setThemeAndSave(currentEffective === 'light' ? 'dark' : 'light')
  }

  const value = {
    theme,
    setTheme: setThemeAndSave,
    toggleTheme,
    effectiveTheme: theme === 'system' ? systemTheme : theme,
    systemTheme
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}

