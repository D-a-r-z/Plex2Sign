"""
Cliente para interactuar con Plex Media Server
"""
import os
import logging
import requests
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any
from plexapi.server import PlexServer
from plexapi.exceptions import PlexApiException, Unauthorized
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PlexClient:
    """Cliente para obtener información de reproducción actual de Plex"""
    
    def __init__(self, token: str, plex_url: str = None):
        """
        Inicializa el cliente de Plex
        
        Args:
            token: Token de autenticación de Plex
            plex_url: URL opcional del servidor Plex (si no se proporciona, se obtiene automáticamente)
        """
        self.token = token
        self.base_url = plex_url
        self.plex = None
        
        # Si no se proporciona URL, obtenerla automáticamente
        if not self.base_url:
            self.base_url = self._get_server_url()
        
        if self.base_url:
            self._connect()
    
    def _get_server_url(self) -> Optional[str]:
        """
        Obtiene la URL del servidor Plex usando la API de Plex Account
        
        Returns:
            URL del servidor Plex o None si no se puede obtener
        """
        try:
            # API de Plex Account para obtener recursos
            api_url = f"https://plex.tv/api/resources?X-Plex-Token={self.token}"
            
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            # Parsear XML
            root = ET.fromstring(response.content)
            
            # Buscar el servidor Plex Media Server
            external_connection = None
            local_connection = None
            
            for device in root.findall('Device'):
                if device.get('provides') and 'server' in device.get('provides'):
                    # Buscar todas las conexiones
                    for connection in device.findall('Connection'):
                        uri = connection.get('uri')
                        local = connection.get('local', 'true')
                        
                        if uri:
                            if local == 'false' or local == '0' or 'plex.direct' in uri:
                                # Conexión externa
                                external_connection = uri
                                logger.info(f"Servidor Plex encontrado (externo): {device.get('name')} - {uri}")
                            else:
                                # Conexión local (solo si no hay externa)
                                if not external_connection:
                                    local_connection = uri
                                    logger.info(f"Servidor Plex encontrado (local): {device.get('name')} - {uri}")
            
            # Retornar conexión externa si existe, sino local
            if external_connection:
                return external_connection
            elif local_connection:
                return local_connection
            
            logger.warning("No se encontró ningún servidor Plex en la cuenta")
            return None
            
        except requests.RequestException as e:
            logger.error(f"Error obteniendo recursos de Plex: {e}")
            return None
        except ET.ParseError as e:
            logger.error(f"Error parseando respuesta XML: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado obteniendo URL del servidor: {e}")
            return None
    
    def _connect(self) -> bool:
        """
        Establece conexión con el servidor Plex
        
        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        try:
            self.plex = PlexServer(self.base_url, self.token)
            logger.info(f"Conectado exitosamente a Plex Server: {self.plex.friendlyName}")
            return True
        except Unauthorized:
            logger.error("Token de Plex inválido o expirado")
            return False
        except PlexApiException as e:
            logger.error(f"Error conectando a Plex: {e}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado conectando a Plex: {e}")
            return False
    
    def _get_token_user(self) -> Optional[str]:
        """
        Obtiene el usuario asociado al token actual
        
        Returns:
            Nombre de usuario del token o None si no se puede obtener
        """
        try:
            # Obtener información de la cuenta usando el token
            api_url = f"https://plex.tv/api/v2/user"
            headers = {'X-Plex-Token': self.token}
            
            response = requests.get(api_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # La API de Plex devuelve XML, no JSON
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            username = root.get('username')
            logger.info(f"Usuario del token: {username}")
            return username
            
        except Exception as e:
            logger.warning(f"Error obteniendo usuario del token: {e}")
            return None

    def get_current_session(self, allowed_user: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Obtiene la sesión de reproducción actual
        
        Args:
            allowed_user: Usuario específico a buscar (opcional)
        
        Returns:
            Diccionario con información de la sesión actual o None si no hay reproducción
        """
        if not self.plex:
            logger.error("No hay conexión con Plex")
            return None
        
        try:
            sessions = self.plex.sessions()
            if not sessions:
                logger.info("No hay sesiones activas")
                return None
            
            # Determinar usuario objetivo
            target_user = None
            if allowed_user:
                # Usuario específico proporcionado
                target_user = allowed_user
            else:
                # Usar usuario del token automáticamente
                target_user = self._get_token_user()
                if not target_user:
                    # Fallback a variable de entorno si no se puede obtener del token
                    target_user = os.getenv('PLEX_ALLOWED_USER')
            
            # Filtrar por usuario objetivo
            if target_user:
                # Buscar sesión del usuario objetivo
                for session in sessions:
                    if session.usernames and session.usernames[0] == target_user:
                        logger.info(f"Sesión encontrada para usuario: {target_user}")
                        break
                else:
                    logger.info(f"No hay sesión activa para el usuario: {target_user}")
                    return None
            else:
                # Tomar la primera sesión activa si no se puede determinar usuario
                session = sessions[0]
                logger.info(f"Usando primera sesión activa de: {session.usernames[0] if session.usernames else 'Unknown'}")
            
            return self._format_session_data(session)
            
        except PlexApiException as e:
            logger.error(f"Error obteniendo sesiones: {e}")
            return None
    
    def _format_session_data(self, session) -> Dict[str, Any]:
        """
        Formatea los datos de la sesión para uso interno
        
        Args:
            session: Objeto de sesión de PlexAPI
            
        Returns:
            Diccionario con datos formateados
        """
        try:
            # Información básica
            data = {
                'title': session.title,
                'type': session.type,  # movie, episode, track, etc.
                'state': session.player.state,  # playing, paused, stopped
                'user': session.usernames[0] if session.usernames else 'Unknown',
                'progress': 0,
                'duration': 0,
                'thumb': None,
                'art': None,
                'year': getattr(session, 'year', None),
                'summary': getattr(session, 'summary', ''),
            }
            
            # Progreso y duración
            if hasattr(session, 'duration') and session.duration:
                data['duration'] = session.duration // 1000  # Convertir a segundos
            
            if hasattr(session, 'viewOffset') and session.viewOffset:
                data['progress'] = session.viewOffset // 1000  # Convertir a segundos
            
            # URLs de imágenes
            if hasattr(session, 'thumb') and session.thumb:
                data['thumb'] = f"{self.base_url}{session.thumb}?X-Plex-Token={self.token}"
            
            if hasattr(session, 'art') and session.art:
                data['art'] = f"{self.base_url}{session.art}?X-Plex-Token={self.token}"
            
            # Información específica por tipo
            if session.type == 'episode':
                data.update({
                    'show_title': session.grandparentTitle,
                    'season': session.parentIndex,
                    'episode': session.index,
                    'episode_title': session.title,
                })
                
                # Intentar obtener el póster de la serie (grandparentThumb)
                if hasattr(session, 'grandparentThumb') and session.grandparentThumb:
                    data['thumb'] = f"{self.base_url}{session.grandparentThumb}?X-Plex-Token={self.token}"
                # Si no hay grandparentThumb, usar el thumb del episodio
                elif hasattr(session, 'thumb') and session.thumb and not data['thumb']:
                    data['thumb'] = f"{self.base_url}{session.thumb}?X-Plex-Token={self.token}"
            elif session.type == 'track':
                data.update({
                    'artist': session.grandparentTitle,
                    'album': session.parentTitle,
                    'track_title': session.title,
                })
            elif session.type == 'movie':
                data.update({
                    'movie_title': session.title,
                    'director': ', '.join([d.tag for d in session.directors]) if hasattr(session, 'directors') else '',
                })
            
            return data
            
        except Exception as e:
            logger.error(f"Error formateando datos de sesión: {e}")
            return {
                'title': 'Error obteniendo información',
                'type': 'unknown',
                'state': 'stopped',
                'user': 'Unknown',
                'progress': 0,
                'duration': 0,
            }
    
    def is_connected(self) -> bool:
        """
        Verifica si hay conexión activa con Plex
        
        Returns:
            True si está conectado, False en caso contrario
        """
        try:
            if self.plex:
                # Intenta hacer una petición simple para verificar conectividad
                self.plex.library
                return True
        except:
            pass
        return False
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        Obtiene información básica del servidor
        
        Returns:
            Diccionario con información del servidor
        """
        if not self.plex:
            return {'error': 'No conectado'}
        
        try:
            return {
                'name': self.plex.friendlyName,
                'version': self.plex.version,
                'platform': self.plex.platform,
                'sessions_count': len(self.plex.sessions()),
            }
        except Exception as e:
            logger.error(f"Error obteniendo info del servidor: {e}")
            return {'error': str(e)}


def create_plex_client(token: Optional[str] = None) -> Optional[PlexClient]:
    """
    Factory function para crear cliente de Plex
    
    Args:
        token: Token de Plex (opcional, si no se proporciona usa PLEX_TOKEN del entorno)
    
    Returns:
        Instancia de PlexClient o None si falta configuración
    """
    plex_token = token or os.getenv('PLEX_TOKEN')
    plex_url = os.getenv('PLEX_URL')  # Opcional, se puede obtener automáticamente
    
    if not plex_token:
        logger.error("Falta token de Plex (parámetro o variable de entorno PLEX_TOKEN)")
        return None
    
    return PlexClient(plex_token, plex_url)
