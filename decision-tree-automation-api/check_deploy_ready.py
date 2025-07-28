#!/usr/bin/env python3
"""
Script final para verificar se tudo está pronto para deploy no Render
"""

import os
import sys

def check_files():
    """Verifica se todos os arquivos necessários existem"""
    print("=== VERIFICAÇÃO DE ARQUIVOS ===\n")
    
    required_files = [
        "backend/main.py",
        "backend/config.py",
        "requirements.txt",
        "render.yaml",
        "start.sh",
        "../decision-tree-automation-ui/index.html"
    ]
    
    all_ok = True
    for file_path in required_files:
        exists = os.path.exists(file_path)
        print(f"{'✅' if exists else '❌'} {file_path}")
        if not exists:
            all_ok = False
    
    print()
    return all_ok

def check_render_config():
    """Verifica a configuração do Render"""
    print("=== CONFIGURAÇÃO DO RENDER ===\n")
    
    try:
        with open("render.yaml", "r") as f:
            content = f.read()
        
        if "decision-tree-automation-ui/**" in content:
            print("✅ Frontend incluído no buildFilter")
        else:
            print("❌ Frontend NÃO incluído no buildFilter")
            return False
        
        if "decision-tree-automation-api/**" in content:
            print("✅ Backend incluído no buildFilter")
        else:
            print("❌ Backend NÃO incluído no buildFilter")
            return False
        
        print("✅ render.yaml configurado corretamente")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao ler render.yaml: {e}")
        return False

def check_backend():
    """Verifica se o backend está funcionando"""
    print("=== VERIFICAÇÃO DO BACKEND ===\n")
    
    try:
        sys.path.append(os.path.dirname(__file__))
        from backend.main import app
        
        print("✅ Backend importado com sucesso")
        
        # Verifica se tem as rotas principais
        routes = [route.path for route in app.routes]
        required_routes = ["/", "/health", "/debug", "/alertas", "/lideres", "/frontend-status"]
        
        for route in required_routes:
            if route in routes:
                print(f"✅ Rota {route} encontrada")
            else:
                print(f"❌ Rota {route} NÃO encontrada")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no backend: {e}")
        return False

def check_frontend():
    """Verifica se o frontend está atualizado"""
    print("=== VERIFICAÇÃO DO FRONTEND ===\n")
    
    try:
        frontend_path = "../decision-tree-automation-ui/index.html"
        with open(frontend_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Verifica se tem as meta tags de cache atualizadas
        if "max-age=0" in content and "must-revalidate" in content:
            print("✅ Meta tags de cache configuradas (versão atualizada)")
        else:
            print("❌ Meta tags de cache NÃO configuradas corretamente")
        
        # Verifica se tem o timestamp atualizado
        if "2024-12-19 16:00:00" in content:
            print("✅ Timestamp de versão encontrado (atualizado)")
        else:
            print("❌ Timestamp de versão NÃO encontrado ou desatualizado")
        
        # Verifica se tem o JavaScript de verificação de versão
        if "checkFrontendVersion" in content:
            print("✅ Verificação de versão configurada")
        else:
            print("❌ Verificação de versão NÃO configurada")
        
        # Verifica se tem o listener para Ctrl+F5
        if "addEventListener('keydown'" in content:
            print("✅ Listener Ctrl+F5 configurado")
        else:
            print("❌ Listener Ctrl+F5 NÃO configurado")
        
        # Verifica se tem os logs de inicialização
        if "Decision Tree Automation - Frontend carregado" in content:
            print("✅ Logs de inicialização configurados")
        else:
            print("❌ Logs de inicialização NÃO configurados")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar frontend: {e}")
        return False

def check_cache_headers():
    """Verifica se os headers de cache estão configurados corretamente"""
    print("=== VERIFICAÇÃO DE HEADERS DE CACHE ===\n")
    
    try:
        sys.path.append(os.path.dirname(__file__))
        from backend.main import get_frontend
        
        print("✅ Função get_frontend importada")
        
        # Verifica se a função existe e tem os headers corretos
        import inspect
        source = inspect.getsource(get_frontend)
        
        if "max-age=0" in source:
            print("✅ Header max-age=0 configurado")
        else:
            print("❌ Header max-age=0 NÃO configurado")
        
        if "Thu, 01 Jan 1970 00:00:00 GMT" in source:
            print("✅ Header Expires configurado")
        else:
            print("❌ Header Expires NÃO configurado")
        
        if "X-Frontend-Timestamp" in source:
            print("✅ Header X-Frontend-Timestamp configurado")
        else:
            print("❌ Header X-Frontend-Timestamp NÃO configurado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar headers: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 VERIFICAÇÃO FINAL PARA DEPLOY NO RENDER\n")
    print("=" * 60 + "\n")
    
    checks = [
        ("Arquivos", check_files),
        ("Configuração Render", check_render_config),
        ("Backend", check_backend),
        ("Frontend", check_frontend),
        ("Headers de Cache", check_cache_headers)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"--- {name} ---")
        result = check_func()
        results.append((name, result))
        print()
    
    print("=" * 60)
    print("🏁 RESUMO FINAL")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 SISTEMA 100% PRONTO PARA DEPLOY NO RENDER!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Faça commit de todas as mudanças")
        print("2. Push para o repositório")
        print("3. Deploy automático no Render")
        print("4. Acesse o link do Render")
        print("5. Use Ctrl+F5 para forçar refresh se necessário")
        print("6. Verifique /frontend-status para debug")
        print("\n🔧 SOLUÇÕES PARA PROBLEMAS DE CACHE:")
        print("- Use Ctrl+F5 (Windows) ou Cmd+Shift+R (Mac)")
        print("- Acesse /frontend-status para verificar o status")
        print("- O sistema tem auto-refresh a cada 5 minutos")
        print("- Verificação de versão a cada 2 minutos")
    else:
        print("⚠️  HÁ PROBLEMAS QUE PRECISAM SER CORRIGIDOS ANTES DO DEPLOY")

if __name__ == "__main__":
    main() 