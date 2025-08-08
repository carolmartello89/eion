#!/usr/bin/env python3
"""
Sistema de Testes Automatizados para IAON
Testa todas as funcionalidades principais do aplicativo
"""
import requests
import json
import time
import urllib3

# Desabilitar avisos SSL para certificados auto-assinados
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class IAONTester:
    def __init__(self, base_url="https://192.168.15.36:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.verify = False  # Ignora certificados auto-assinados
        self.auth_token = None
        
    def log(self, message, status="INFO"):
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "TEST": "🧪"}
        print(f"{icons.get(status, 'ℹ️')} {message}")
        
    def test_server_status(self):
        """Testa se o servidor está rodando"""
        self.log("Testando status do servidor...", "TEST")
        try:
            response = self.session.get(self.base_url, timeout=10)
            if response.status_code == 200:
                self.log("Servidor HTTPS está funcionando", "SUCCESS")
                return True
            else:
                self.log(f"Servidor retornou código {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Erro ao conectar com servidor: {e}", "ERROR")
            return False
    
    def test_ssl_security(self):
        """Testa se o SSL está funcionando"""
        self.log("Testando segurança SSL...", "TEST")
        try:
            # Teste sem verificação SSL (deve funcionar)
            response = self.session.get(self.base_url)
            if response.status_code == 200:
                self.log("SSL configurado corretamente (certificado auto-assinado)", "SUCCESS")
                return True
        except Exception as e:
            self.log(f"Erro no SSL: {e}", "ERROR")
            return False
    
    def test_login_system(self):
        """Testa o sistema de login"""
        self.log("Testando sistema de login...", "TEST")
        try:
            # Dados de login
            login_data = {
                'email': 'admin@demo.com',
                'password': '123456'
            }
            
            response = self.session.post(f"{self.base_url}/login", 
                                       data=login_data, 
                                       allow_redirects=False)
            
            if response.status_code in [200, 302]:
                self.log("Sistema de login funcionando", "SUCCESS")
                return True
            else:
                self.log(f"Login falhou com código {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Erro no teste de login: {e}", "ERROR")
            return False
    
    def test_dashboard_access(self):
        """Testa acesso ao dashboard"""
        self.log("Testando acesso ao dashboard...", "TEST")
        try:
            response = self.session.get(f"{self.base_url}/dashboard")
            if response.status_code == 200:
                self.log("Dashboard acessível", "SUCCESS")
                return True
            else:
                self.log(f"Dashboard inacessível - código {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Erro no acesso ao dashboard: {e}", "ERROR")
            return False
    
    def test_api_endpoints(self):
        """Testa endpoints da API"""
        self.log("Testando endpoints da API...", "TEST")
        endpoints = [
            '/api/compromissos',
            '/api/contatos', 
            '/api/financeiro',
            '/api/reunioes'
        ]
        
        working_endpoints = 0
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code in [200, 401]:  # 401 é esperado se não autenticado
                    working_endpoints += 1
                    self.log(f"Endpoint {endpoint} OK", "SUCCESS")
                else:
                    self.log(f"Endpoint {endpoint} falhou - {response.status_code}", "ERROR")
            except Exception as e:
                self.log(f"Erro no endpoint {endpoint}: {e}", "ERROR")
        
        if working_endpoints >= len(endpoints) * 0.75:  # 75% dos endpoints funcionando
            self.log("APIs principais funcionando", "SUCCESS")
            return True
        else:
            self.log("Muitos endpoints com problema", "ERROR")
            return False
    
    def test_voice_features(self):
        """Testa funcionalidades de voz"""
        self.log("Testando funcionalidades de voz...", "TEST")
        try:
            # Verificar se as páginas com recursos de voz carregam
            response = self.session.get(self.base_url)
            content = response.text
            
            voice_features = [
                'recognition',
                'voice',
                'speechRecognition',
                'biometr',
                'microfone'
            ]
            
            found_features = 0
            for feature in voice_features:
                if feature.lower() in content.lower():
                    found_features += 1
            
            if found_features >= 3:
                self.log("Recursos de voz presentes no código", "SUCCESS")
                return True
            else:
                self.log("Recursos de voz podem estar ausentes", "ERROR")
                return False
        except Exception as e:
            self.log(f"Erro no teste de voz: {e}", "ERROR")
            return False
    
    def test_mobile_compatibility(self):
        """Testa compatibilidade mobile"""
        self.log("Testando compatibilidade mobile...", "TEST")
        try:
            # Simular user agent mobile
            mobile_headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1'
            }
            
            response = self.session.get(self.base_url, headers=mobile_headers)
            content = response.text
            
            mobile_features = [
                'viewport',
                'mobile',
                'responsive',
                'touch'
            ]
            
            found_mobile = 0
            for feature in mobile_features:
                if feature.lower() in content.lower():
                    found_mobile += 1
            
            if found_mobile >= 2:
                self.log("Compatibilidade mobile detectada", "SUCCESS")
                return True
            else:
                self.log("Compatibilidade mobile limitada", "ERROR")
                return False
        except Exception as e:
            self.log(f"Erro no teste mobile: {e}", "ERROR")
            return False
    
    def test_pwa_features(self):
        """Testa recursos PWA"""
        self.log("Testando recursos PWA...", "TEST")
        try:
            # Testar manifest.json
            response = self.session.get(f"{self.base_url}/static/manifest.json")
            if response.status_code == 200:
                manifest = response.json()
                if 'name' in manifest and 'icons' in manifest:
                    self.log("Manifest PWA válido", "SUCCESS")
                    
                    # Testar service worker
                    sw_response = self.session.get(f"{self.base_url}/static/sw.js")
                    if sw_response.status_code == 200:
                        self.log("Service Worker disponível", "SUCCESS")
                        return True
                    else:
                        self.log("Service Worker não encontrado", "ERROR")
                        return False
                else:
                    self.log("Manifest inválido", "ERROR")
                    return False
            else:
                self.log("Manifest não encontrado", "ERROR")
                return False
        except Exception as e:
            self.log(f"Erro no teste PWA: {e}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Executa todos os testes"""
        self.log("🚀 Iniciando Bateria de Testes IAON", "INFO")
        self.log("="*50, "INFO")
        
        tests = [
            ("Status do Servidor", self.test_server_status),
            ("Segurança SSL", self.test_ssl_security),
            ("Sistema de Login", self.test_login_system),
            ("Acesso ao Dashboard", self.test_dashboard_access),
            ("Endpoints API", self.test_api_endpoints),
            ("Funcionalidades de Voz", self.test_voice_features),
            ("Compatibilidade Mobile", self.test_mobile_compatibility),
            ("Recursos PWA", self.test_pwa_features)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"\n📋 Executando: {test_name}", "INFO")
            if test_func():
                passed += 1
                
        # Relatório final
        self.log("\n" + "="*50, "INFO")
        self.log(f"📊 RELATÓRIO FINAL", "INFO")
        self.log(f"✅ Testes Aprovados: {passed}/{total}", "SUCCESS" if passed >= total * 0.8 else "ERROR")
        self.log(f"📈 Taxa de Sucesso: {(passed/total)*100:.1f}%", "INFO")
        
        if passed >= total * 0.8:
            self.log("🎉 SISTEMA APROVADO - Funcionando corretamente!", "SUCCESS")
        else:
            self.log("⚠️ SISTEMA COM PROBLEMAS - Verificar falhas", "ERROR")
            
        return passed >= total * 0.8

if __name__ == "__main__":
    tester = IAONTester()
    tester.run_all_tests()
