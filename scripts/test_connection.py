#!/usr/bin/env python3
"""
Script para probar la conexión con Plex y generar imagen de prueba
"""
import os
import sys
from dotenv import load_dotenv

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.plex_client import create_plex_client
from api.image_generator import ImageGenerator
from api.imgur_client import create_imgur_client

def test_plex_connection():
    """Prueba la conexión con Plex"""
    print("🔍 Probando conexión con Plex...")
    
    client = create_plex_client()
    if not client:
        print("❌ No se pudo crear cliente de Plex")
        return False
    
    if not client.is_connected():
        print("❌ No se pudo conectar al servidor Plex")
        return False
    
    server_info = client.get_server_info()
    print(f"✅ Conectado a: {server_info.get('name', 'Unknown')}")
    print(f"   Versión: {server_info.get('version', 'Unknown')}")
    print(f"   Sesiones activas: {server_info.get('sessions_count', 0)}")
    
    # Probar obtener sesión actual
    session = client.get_current_session()
    if session:
        print(f"🎵 Reproduciendo: {session.get('title', 'Unknown')}")
        print(f"   Tipo: {session.get('type', 'Unknown')}")
        print(f"   Estado: {session.get('state', 'Unknown')}")
        print(f"   Usuario: {session.get('user', 'Unknown')}")
    else:
        print("⏸️  No hay reproducción activa")
    
    return True

def test_image_generation():
    """Prueba la generación de imágenes"""
    print("\n🖼️  Probando generación de imágenes...")
    
    # Datos de prueba
    test_data = {
        'title': 'Canción de Prueba',
        'type': 'track',
        'state': 'playing',
        'user': 'TestUser',
        'progress': 120,
        'duration': 240,
        'track_title': 'Canción de Prueba',
        'artist': 'Artista de Prueba',
        'album': 'Álbum de Prueba'
    }
    
    generator = ImageGenerator()
    
    try:
        # Generar imagen con datos de prueba
        image_buffer = generator.generate_now_playing_image(test_data)
        
        # Guardar imagen localmente
        with open('test_image.png', 'wb') as f:
            image_buffer.seek(0)
            f.write(image_buffer.read())
        
        print("✅ Imagen generada exitosamente: test_image.png")
        return True
        
    except Exception as e:
        print(f"❌ Error generando imagen: {e}")
        return False

def test_imgur_upload():
    """Prueba la subida a Imgur"""
    print("\n📤 Probando subida a Imgur...")
    
    client = create_imgur_client()
    if not client:
        print("❌ No se pudo crear cliente de Imgur (Client ID no configurado)")
        return False
    
    # Generar imagen de prueba
    generator = ImageGenerator()
    test_data = {
        'title': 'Plex2Sign Test',
        'type': 'track',
        'state': 'playing',
        'track_title': 'Test Song',
        'artist': 'Test Artist',
        'album': 'Test Album'
    }
    
    image_buffer = generator.generate_now_playing_image(test_data)
    
    try:
        image_url = client.upload_image(image_buffer, "Plex2Sign Test")
        if image_url:
            print(f"✅ Imagen subida exitosamente: {image_url}")
            return True
        else:
            print("❌ Error subiendo imagen a Imgur")
            return False
    except Exception as e:
        print(f"❌ Error subiendo a Imgur: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 Plex2Sign - Test de Conexiones\n")
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Verificar variables requeridas
    required_vars = ['PLEX_URL', 'PLEX_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Faltan variables de entorno: {', '.join(missing_vars)}")
        print("💡 Asegúrate de tener un archivo .env configurado")
        return False
    
    success = True
    
    # Probar Plex
    success &= test_plex_connection()
    
    # Probar generación de imágenes
    success &= test_image_generation()
    
    # Probar Imgur (opcional)
    if os.getenv('IMGUR_CLIENT_ID'):
        success &= test_imgur_upload()
    else:
        print("\n📤 Imgur no configurado (opcional)")
    
    print(f"\n{'✅ Todas las pruebas pasaron' if success else '❌ Algunas pruebas fallaron'}")
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
