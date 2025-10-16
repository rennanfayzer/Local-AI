#!/usr/bin/env python3
"""
Script de Teste Rápido do Sistema de Voz
Execute após containers estarem rodando
"""

import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000"

def print_header(text):
    """Printa header formatado"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def test_api_health():
    """Testa se API está respondendo"""
    print_header("TESTE 1: API Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API está rodando!")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            return True
        else:
            print(f"❌ API retornou status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar à API")
        print("   Certifique-se de que os containers estão rodando:")
        print("   docker-compose up -d")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_voice_info():
    """Testa endpoint de informações de voz"""
    print_header("TESTE 2: Voice System Info")
    
    try:
        response = requests.get(f"{BASE_URL}/voice/info", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Sistema de voz disponível!")
            print(f"   Whisper Model: {data['whisper_model']}")
            print(f"   TTS Model: {data['tts_model']}")
            print(f"   Device: {data['device']}")
            print(f"   Idiomas: {len(data['supported_languages'])} suportados")
            print(f"   Formatos: {', '.join(data['supported_formats'])}")
            print(f"   Whisper Carregado: {data['whisper_loaded']}")
            print(f"   TTS Carregado: {data['tts_loaded']}")
            return True
        elif response.status_code == 404:
            print("❌ Endpoint /voice/info não encontrado")
            print("   Sistema de voz pode não estar habilitado")
            return False
        else:
            print(f"❌ Erro: status {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_voice_synthesize():
    """Testa síntese de voz"""
    print_header("TESTE 3: Text-to-Speech (Síntese)")
    
    print("🔊 Sintetizando: 'Olá! Este é um teste do sistema de voz.'")
    
    try:
        payload = {
            "text": "Olá! Este é um teste do sistema de voz.",
            "language": "pt",
            "output_format": "wav"
        }
        
        print("   Enviando requisição... (pode demorar no primeiro uso)")
        response = requests.post(
            f"{BASE_URL}/voice/synthesize",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            output_file = "test_synthesis_output.wav"
            with open(output_file, "wb") as f:
                f.write(response.content)
            
            print(f"✅ Síntese concluída!")
            print(f"   Arquivo salvo: {output_file}")
            print(f"   Tamanho: {len(response.content)} bytes")
            print(f"   Você pode abrir o arquivo para ouvir!")
            return True
        else:
            print(f"❌ Erro: status {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.Timeout:
        print("⏱️  Timeout - pode ser normal no primeiro uso (download de modelos)")
        print("   Tente novamente em alguns segundos")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_voice_transcribe():
    """Testa transcrição (usa áudio do teste anterior)"""
    print_header("TESTE 4: Speech-to-Text (Transcrição)")
    
    audio_file = "test_synthesis_output.wav"
    
    try:
        # Verificar se arquivo existe
        import os
        if not os.path.exists(audio_file):
            print(f"⚠️  Arquivo {audio_file} não encontrado")
            print("   Execute o teste de síntese primeiro")
            return False
        
        print(f"🎤 Transcrevendo: {audio_file}")
        print("   (pode demorar no primeiro uso)")
        
        with open(audio_file, "rb") as f:
            files = {"audio": f}
            data = {"language": "pt", "return_metadata": "true"}
            
            response = requests.post(
                f"{BASE_URL}/voice/transcribe",
                files=files,
                data=data,
                timeout=60
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Transcrição concluída!")
            print(f"   Texto: {result['text']}")
            print(f"   Idioma detectado: {result['language']}")
            if result.get('duration'):
                print(f"   Duração: {result['duration']:.2f}s")
            return True
        else:
            print(f"❌ Erro: status {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.Timeout:
        print("⏱️  Timeout - download de modelos Whisper em andamento")
        print("   Modelo base (~74MB). Aguarde e tente novamente")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_api_root():
    """Testa endpoint raiz (mostra features)"""
    print_header("TESTE 5: API Features")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API v" + data.get('version', 'unknown'))
            print("\n📋 Features disponíveis:")
            for feature in data.get('features', []):
                print(f"   • {feature}")
            
            if data.get('capabilities', {}).get('voice_processing'):
                print("\n🎤 Sistema de voz: HABILITADO")
            else:
                print("\n⚠️  Sistema de voz: NÃO HABILITADO")
            
            return True
        else:
            print(f"❌ Erro: status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("\n" + "🎤" * 30)
    print("   TESTE RÁPIDO - SISTEMA DE VOZ")
    print("   Escrita Sincerta LLM Pro v2.1.0")
    print("🎤" * 30)
    
    results = {}
    
    # Teste 1: API Health
    results["API Health"] = test_api_health()
    if not results["API Health"]:
        print("\n❌ API não está acessível. Abortando testes.")
        print("\nPara iniciar a API:")
        print("   docker-compose up -d")
        return
    
    time.sleep(1)
    
    # Teste 2: Voice Info
    results["Voice Info"] = test_voice_info()
    time.sleep(1)
    
    # Teste 3: Features
    results["API Features"] = test_api_root()
    time.sleep(1)
    
    # Teste 4: Síntese (pode demorar)
    results["Synthesis (TTS)"] = test_voice_synthesize()
    time.sleep(2)
    
    # Teste 5: Transcrição (pode demorar)
    if results["Synthesis (TTS)"]:
        results["Transcription (STT)"] = test_voice_transcribe()
    
    # Resumo
    print_header("RESUMO DOS TESTES")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"  RESULTADO: {passed}/{total} testes passaram")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema de voz está funcionando perfeitamente!")
        print("\n📁 Arquivo gerado: test_synthesis_output.wav")
        print("   Abra o arquivo para ouvir o áudio sintetizado!")
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam")
        print("\n💡 Dicas:")
        print("   • Primeiro uso pode demorar (download de modelos)")
        print("   • Aguarde alguns minutos e tente novamente")
        print("   • Verifique logs: docker-compose logs -f api")
    
    print("\n📖 Para mais informações:")
    print("   • Guia completo: VOICE.md")
    print("   • Instalação: VOICE_SETUP.md")
    print("   • Documentação API: http://localhost:8000/docs")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
        sys.exit(0)
