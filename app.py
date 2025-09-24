"""
Plex2Sign - Aplicación principal
Muestra lo que estás reproduciendo en Plex en tu perfil de GitHub
"""
import os
import logging
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, Response, request, jsonify
from api.plex_client import create_plex_client
from api.image_generator import ImageGenerator
from api.svg_generator import SVGGenerator

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO if os.getenv('DEBUG', 'false').lower() != 'true' else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__)

# Cache simple para evitar regenerar imágenes constantemente
image_cache = {
    'last_update': None,
    'image_url': None,
    'session_data': None,
    'cache_duration': int(os.getenv('CACHE_DURATION', 60))  # segundos
}


@app.route('/')
def index():
    """Página principal con información del proyecto"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Plex2Sign</title>
        <meta charset="utf-8">
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px; margin: 30px auto; padding: 15px;
                background: #0d1117; color: #f0f6fc;
            }
            .card { 
                background: #161b22; border-radius: 12px; padding: 15px; margin: 15px 0;
                border: 1px solid #9C27B0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            }
            .status { padding: 8px; border-radius: 4px; margin: 8px 0; }
            .success { background: #161b22; color: white; }
            .error { background: #da3633; color: white; }
            .warning { background: #bf8700; color: white; }
            code { background: #21262d; padding: 2px 4px; border-radius: 3px; color: #f0f6fc; font-size: 0.9em; }
            a { color: #9C27B0; text-decoration: none; }
            a:hover { text-decoration: underline; }
            h1 { margin-top: 0; margin-bottom: 16px; }
            h2 { margin-top: 0; margin-bottom: 18px; }
            h3 { margin-top: 16px; margin-bottom: 8px; }
            p { margin-top: 4px; margin-bottom: 4px; }
            img { 
                max-width: 100%; 
                border-radius: 6px; 
                border: 1px solid #ddd; 
                margin: 1px 0;
                padding: 1px;
            }
        </style>
    </head>
    <body>
        <h1>🎵 Plex2Sign</h1>
        <p>Utilidad para generar imágenes dinámicas y estáticas de tu reproducción actual de Plex. Perfecta para perfiles de GitHub, foros, webs y redes sociales.</p>
        <p><small>Basado en <a href="https://github.com/kittinan/spotify-github-profile" target="_blank">spotify-github-profile</a> de kittinan y los estilos de barras de <a href="https://github.com/novatorem/novatorem" target="_blank">Novatorem</a>. Originalmente creado para GitHub, pero expandido para múltiples usos.</small></p>
        
        <div class="card">
            <h2>📊 Estado del Sistema</h2>
            <div id="status">Verificando...</div>
        </div>
        
        <div class="card">
            <h2>🔧 Uso en GitHub</h2>
            <p>Añade esto a tu <code>README.md</code> del perfil:</p>
            <pre><code>![Plex2Sign](''' + request.url_root + '''api/now-playing)</code></pre>
        </div>
        
        <div class="card">
            <h2>🎨 Formatos Disponibles</h2>
            
            <h3>SVG (Animado)</h3>
            <div style="margin: 2px 0;">
                <p style="margin: 2px 0;"><strong>Light SVG</strong> - Tema claro con ecualizador animado</p>
                <img src="/api/now-playing-svg?theme=normal&height=90" alt="Light SVG" style="max-width: 400px;" />
                <br><small><a href="/api/now-playing-svg?theme=normal&height=90">Ver enlace directo</a></small>
            </div>
            
            <div style="margin: 2px 0;">
                <p style="margin: 2px 0;"><strong>Dark SVG</strong> - Tema oscuro con ecualizador animado</p>
                <img src="/api/now-playing-svg?theme=dark&height=90" alt="Dark SVG" style="max-width: 400px;" />
                <br><small><a href="/api/now-playing-svg?theme=dark&height=90">Ver enlace directo</a></small>
            </div>
            
            <h3>PNG (Estático)</h3>
            <div style="margin: 2px 0;">
                <p style="margin: 2px 0;"><strong>Light PNG</strong> - Tema claro con barras estáticas</p>
                <img src="/api/now-playing-png?theme=normal" alt="Light PNG" style="max-width: 400px;" />
                <br><small><a href="/api/now-playing-png?theme=normal">Ver enlace directo</a></small>
            </div>
            
            <div style="margin: 2px 0;">
                <p style="margin: 2px 0;"><strong>Dark PNG</strong> - Tema oscuro con barras estáticas</p>
                <img src="/api/now-playing-png?theme=dark" alt="Dark PNG" style="max-width: 400px;" />
                <br><small><a href="/api/now-playing-png?theme=dark">Ver enlace directo</a></small>
            </div>
            
            <p style="margin-top: 20px;"><small>💡 Se irán agregando otros diseños según se vayan probando.</small></p>
        </div>
        
        <script>
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    const statusDiv = document.getElementById('status');
                    let html = '';
                    
                    if (data.plex.connected) {
                        html += '<div class="success">✅ Plex: Conectado (' + data.plex.server_name + ')</div>';
                    } else {
                        html += '<div class="error">❌ Plex: ' + (data.plex.error || 'No conectado') + '</div>';
                    }
                    
                    // Imgur eliminado
                    
                    if (data.current_session) {
                        html += '<div class="success">🎵 Reproduciendo: ' + data.current_session.title + '</div>';
                    } else {
                        html += '<div class="warning">⏸️ No hay reproducción activa</div>';
                    }
                    
                    statusDiv.innerHTML = html;
                })
                .catch(e => {
                    document.getElementById('status').innerHTML = '<div class="error">❌ Error obteniendo estado</div>';
                });
        </script>
    </body>
    </html>
    '''


@app.route('/api/status')
def api_status():
    """Endpoint para verificar el estado del sistema"""
    # Obtener token de parámetro de consulta o variable de entorno
    token = request.args.get('token')
    plex_client = create_plex_client(token)
    status = {
        'plex': {
            'connected': False,
            'server_name': None,
            'error': None
        },
        'current_session': None,
        'cache': {
            'last_update': image_cache['last_update'].isoformat() if image_cache['last_update'] else None,
            'has_cached_image': image_cache['image_url'] is not None
        }
    }
    
    if plex_client and plex_client.is_connected():
        server_info = plex_client.get_server_info()
        status['plex']['connected'] = True
        status['plex']['server_name'] = server_info.get('name', 'Unknown')
        status['plex']['sessions_count'] = server_info.get('sessions_count', 0)
        
        # Obtener sesión actual
        session_data = plex_client.get_current_session()
        if session_data:
            status['current_session'] = {
                'title': session_data.get('title'),
                'type': session_data.get('type'),
                'state': session_data.get('state'),
                'user': session_data.get('user')
            }
    else:
        status['plex']['error'] = 'No se pudo conectar'
    
    return jsonify(status)


@app.route('/api/now-playing')
def api_now_playing():
    """Endpoint principal que genera y devuelve la imagen de reproducción actual"""
    try:
        # Parámetros de la petición
        theme = request.args.get('theme', os.getenv('DEFAULT_THEME', 'normal'))
        width = int(request.args.get('width', os.getenv('IMAGE_WIDTH', 400)))
        height = int(request.args.get('height', 90))  # Forzado a 90, ignorando IMAGE_HEIGHT
        force_refresh = request.args.get('refresh', 'false').lower() == 'true'
        
        # No usar caché de Imgur ni redirección, solo lógica original
        
        # Obtener datos de Plex
        token = request.args.get('token')
        plex_client = create_plex_client(token)
        if not plex_client:
            logger.error("No se pudo crear cliente de Plex")
            return generate_error_image("Error: Plex no configurado")
        
        # Obtener usuario específico si está configurado
        allowed_user = request.args.get('user')
        session_data = plex_client.get_current_session(allowed_user)
        logger.info(f"Datos de sesión obtenidos: {session_data}")
        
        # Si no hay sesión activa, intentar usar historial
        if not session_data:
            import time
            offset = int(time.time() // 30) % 5  # Alternar entre 0-4 cada 30 segundos
            history_data = plex_client.get_recent_playback_history(allowed_user, limit=10, offset=offset)
            logger.info(f"PNG: Historial obtenido: {history_data}")
            if history_data:
                logger.info("No hay sesión activa, usando historial de reproducciones")
                session_data = history_data
            else:
                logger.info("No hay sesión activa, historial ni cache, generando imagen de 'sin actividad'")
                session_data = None
        
        # Generar imagen y devolver directamente
        image_generator = ImageGenerator(width, height, theme)
        image_buffer = image_generator.generate_now_playing_image(session_data)
        image_buffer.seek(0)
        return Response(image_buffer.read(), mimetype='image/png')
        
    except Exception as e:
        logger.error(f"Error generando imagen: {e}")
        return generate_error_image(f"Error: {str(e)}")


def generate_error_image(message: str) -> Response:
    """Genera imagen de error"""
    try:
        image_generator = ImageGenerator(400, 90, 'default')
        error_data = {
            'title': message,
            'type': 'error',
            'state': 'stopped'
        }
        image_buffer = image_generator.generate_now_playing_image(None)  # Imagen idle
        image_buffer.seek(0)
        return Response(image_buffer.read(), mimetype='image/png')
    except Exception as e:
        logger.error(f"Error generando imagen de error: {e}")
        return Response("Error", mimetype='text/plain', status=500)


def generate_error_svg(message: str) -> Response:
    """Genera SVG de error"""
    try:
        svg_content = f'''
        <svg width="400" height="90" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <style>
                    .error-text {{
                        font-family: Arial, sans-serif;
                        fill: #ff4444;
                        font-size: 14px;
                        text-anchor: middle;
                    }}
                </style>
            </defs>
            <text x="200" y="80" class="error-text">{message}</text>
        </svg>
        '''
        return Response(svg_content, mimetype='image/svg+xml')
    except Exception as e:
        logger.error(f"Error generando SVG de error: {e}")
        return Response("Error SVG", mimetype='text/plain', status=500)


@app.route('/api/now-playing-svg')
def api_now_playing_svg():
    """Endpoint que genera y devuelve SVG animado de reproducción actual"""
    try:
        # Parámetros de la petición
        theme = request.args.get('theme', os.getenv('DEFAULT_THEME', 'normal'))
        width = int(request.args.get('width', os.getenv('IMAGE_WIDTH', 400)))
        height = int(request.args.get('height', 90))  # Forzado a 90, ignorando IMAGE_HEIGHT
        
        # Obtener datos de Plex
        token = request.args.get('token')
        plex_client = create_plex_client(token)
        if not plex_client:
            logger.error("No se pudo crear cliente de Plex")
            return generate_error_svg("Error: Plex no configurado")
        
        # Obtener usuario específico si está configurado
        allowed_user = request.args.get('user')
        session_data = plex_client.get_current_session(allowed_user)
        logger.info(f"Datos de sesión obtenidos para SVG: {session_data}")
        
        # Si no hay sesión activa, intentar usar historial
        if not session_data:
            import time
            offset = int(time.time() // 30) % 5  # Alternar entre 0-4 cada 30 segundos
            history_data = plex_client.get_recent_playback_history(allowed_user, limit=10, offset=offset)
            logger.info(f"Historial obtenido: {history_data}")
            if history_data:
                logger.info("No hay sesión activa, usando historial de reproducciones para SVG")
                session_data = history_data
            else:
                logger.info("No hay sesión activa, historial ni cache, generando SVG de 'sin actividad'")
                session_data = None
        
        # Generar SVG
        svg_generator = SVGGenerator(width, height, theme)
        svg_content = svg_generator.generate_now_playing_svg(session_data)
        
        logger.info("SVG generado exitosamente")
        return Response(svg_content, mimetype='image/svg+xml')
        
    except Exception as e:
        logger.error(f"Error generando SVG: {e}")
        return generate_error_svg(f"Error: {str(e)}")


@app.route('/api/now-playing-png')
def api_now_playing_png():
    """Endpoint que genera y devuelve PNG estático de reproducción actual"""
    try:
        # Parámetros de la petición
        theme = request.args.get('theme', os.getenv('DEFAULT_THEME', 'normal'))
        width = int(request.args.get('width', os.getenv('IMAGE_WIDTH', 400)))
        height = int(request.args.get('height', 90))  # Forzado a 90, ignorando IMAGE_HEIGHT
        
        # Obtener cliente Plex
        token = request.args.get('token')
        plex_client = create_plex_client(token)
        if not plex_client:
            logger.error("No se pudo crear cliente Plex")
            return "Error: No se pudo conectar a Plex", 500
        
        # Obtener sesión actual
        allowed_user = request.args.get('user')
        session_data = plex_client.get_current_session(allowed_user)
        logger.info(f"Datos de sesión obtenidos para PNG: {session_data}")
        
        # Si no hay sesión activa, intentar usar historial
        if not session_data:
            import time
            offset = int(time.time() // 30) % 5  # Alternar entre 0-4 cada 30 segundos
            history_data = plex_client.get_recent_playback_history(allowed_user, limit=10, offset=offset)
            logger.info(f"PNG: Historial obtenido: {history_data}")
            if history_data:
                logger.info("No hay sesión activa, usando historial de reproducciones para PNG")
                session_data = history_data
            else:
                logger.info("No hay sesión activa, historial ni cache, generando PNG de 'sin actividad'")
                session_data = None
        # Generar imagen PNG
        logger.info(f"Generando PNG con dimensiones: {width}x{height}")
        image_generator = ImageGenerator(theme=theme, width=width, height=height)
        image_buffer = image_generator.generate_now_playing_image(session_data)
        image_bytes = image_buffer.getvalue()  # Convertir BytesIO a bytes
        logger.info(f"PNG generado exitosamente - Tema: {theme}, Dimensiones: {width}x{height}, Tamaño: {len(image_bytes)} bytes")
        return Response(
            image_bytes,
            mimetype='image/png',
            headers={
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        )
        
    except Exception as e:
        logger.error(f"Error generando PNG: {e}")
        return "Error generando imagen PNG", 500


@app.route('/api/cache/clear')
def api_clear_cache():
    """Endpoint para limpiar el cache manualmente"""
    global image_cache
    image_cache = {
        'last_update': None,
        'image_url': None,
        'session_data': None,
        'cache_duration': image_cache['cache_duration']
    }
    return jsonify({'success': True, 'message': 'Cache limpiado'})


if __name__ == '__main__':
    # Verificar configuración
    if not os.getenv('PLEX_URL') or not os.getenv('PLEX_TOKEN'):
        logger.error("⚠️  Faltan variables de entorno PLEX_URL y/o PLEX_TOKEN")
        logger.info("💡 Copia .env.example a .env y configura tus credenciales")
    
    # Imgur eliminado: no se requiere advertencia
    
    # Ejecutar aplicación
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"🚀 Iniciando Plex2Sign en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
