import { useState, useEffect, createContext, useContext } from 'react'

// Contexto de autenticação
const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  // Verifica se há token salvo no localStorage
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const savedToken = localStorage.getItem('auth_token')
        const savedUser = localStorage.getItem('user_data')

        if (savedToken && savedUser) {
          // Verifica se o token ainda é válido
          const response = await fetch('/api/auth/verify', {
            headers: {
              'Authorization': `Bearer ${savedToken}`
            }
          })

          if (response.ok) {
            const data = await response.json()
            setToken(savedToken)
            setUser(JSON.parse(savedUser))
            setIsAuthenticated(true)
          } else {
            // Token inválido, remove do localStorage
            localStorage.removeItem('auth_token')
            localStorage.removeItem('user_data')
          }
        }
      } catch (error) {
        console.error('Erro ao verificar autenticação:', error)
        localStorage.removeItem('auth_token')
        localStorage.removeItem('user_data')
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [])

  const login = (userData, userToken) => {
    setUser(userData)
    setToken(userToken)
    setIsAuthenticated(true)
    localStorage.setItem('auth_token', userToken)
    localStorage.setItem('user_data', JSON.stringify(userData))
  }

  const logout = async () => {
    try {
      // Chama endpoint de logout se houver token
      if (token) {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
      }
    } catch (error) {
      console.error('Erro no logout:', error)
    } finally {
      // Limpa estado local independente do resultado da API
      setUser(null)
      setToken(null)
      setIsAuthenticated(false)
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user_data')
    }
  }

  const getAuthHeaders = () => {
    if (!token) return {}
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  }

  const authenticatedFetch = async (url, options = {}) => {
    const headers = {
      ...getAuthHeaders(),
      ...options.headers
    }

    const response = await fetch(url, {
      ...options,
      headers
    })

    // Se receber 401, faz logout automático
    if (response.status === 401) {
      logout()
      throw new Error('Sessão expirada')
    }

    return response
  }

  const value = {
    user,
    token,
    isLoading,
    isAuthenticated,
    login,
    logout,
    getAuthHeaders,
    authenticatedFetch
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export default useAuth

