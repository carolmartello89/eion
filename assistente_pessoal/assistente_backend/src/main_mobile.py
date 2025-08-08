#!/usr/bin/env python3
"""
IAON - Servidor Mobile-First
Versão otimizada para iPhone/Android sem problemas de SSL
"""
# Importar tudo do arquivo principal
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main_saas import app

if __name__ == '__main__':
    print("📱 IAON Mobile Server")
    print("🚀 Iniciando IAON...")
    print("🌐 Servidor HTTP: http://localhost:5000")
    print("🌐 Servidor HTTP: http://192.168.15.36:5000")
    print("📱 Acesso Mobile: http://192.168.15.36:5000")
    print("👤 Demo: admin@demo.com / 123456")
    print("🏢 Multi-organizacional: Suporte a múltiplas empresas")
    print("💰 Pronto para comercialização!")
    print("📱 Compatível com iPhone/Android")
    print("🔊 Reconhecimento de voz ativado")
    print("=" * 50)
    print("📲 Para iPhone: Abra Safari e acesse:")
    print("   http://192.168.15.36:5000")
    print("   Depois adicione à tela inicial!")
    print("=" * 50)
    
    # Servidor HTTP simples para máxima compatibilidade
    app.run(host='0.0.0.0', port=5000, debug=True)
