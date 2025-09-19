"""
Generador de SVG animados para Plex2Sign
"""
import os
import io
import logging
import requests
import base64
from typing import Dict, Any, Optional, List, Tuple
from datetime import timedelta
from colorthief import ColorThief
from PIL import Image

logger = logging.getLogger(__name__)


class SVGGenerator:
    """Generador de SVG animados para mostrar información de reproducción"""
    
    def __init__(self, width: int = 400, height: int = 90, theme: str = 'minimal'):
        """
        Inicializa el generador de SVG
        
        Args:
            width: Ancho del SVG en píxeles
            height: Alto del SVG en píxeles
            theme: Tema visual a usar
        """
        self.width = width
        self.height = height
        self.theme = theme
        self.themes = self._load_themes()
        
    def _load_themes(self) -> Dict[str, Dict[str, Any]]:
        """Carga los temas visuales disponibles"""
        return {
            'normal': {
                'bg_color': '#ffffff',
                'text_color': '#2d3748',
                'accent_color': '#3182ce',
                'progress_bg': 'transparent',
                'progress_fg': '#3182ce',
                'font_family': 'Arial, sans-serif',
                'font_size_title': '14px',
                'font_size_subtitle': '11px',
                'font_size_time': '10px',
            },
            'dark': {
                'bg_color': '#f8f9fa',
                'text_color': '#212529',
                'accent_color': '#343a40',  # Más oscuro que antes (#495057)
                'progress_bg': 'transparent',
                'progress_fg': '#343a40',   # Mismo gris más oscuro
                'font_family': 'Arial, sans-serif',
                'font_size_title': '14px',
                'font_size_subtitle': '11px',
                'font_size_time': '10px',
            },
            'default': {
                'bg_color': '#ffffff',
                'text_color': '#2d3748',
                'accent_color': '#3182ce',
                'progress_bg': 'transparent',
                'progress_fg': '#3182ce',
                'font_family': 'Arial, sans-serif',
                'font_size_title': '14px',
                'font_size_subtitle': '11px',
                'font_size_time': '10px',
            },
            # Alias para compatibilidad
            'minimal': {
                'bg_color': '#ffffff',
                'text_color': '#2d3748',
                'accent_color': '#3182ce',
                'progress_bg': 'transparent',
                'progress_fg': '#3182ce',
                'font_family': 'Arial, sans-serif',
                'font_size_title': '14px',
                'font_size_subtitle': '11px',
                'font_size_time': '10px',
            },
            'light': {
                'bg_color': '#f8f9fa',
                'text_color': '#212529',
                'accent_color': '#343a40',
                'progress_bg': 'transparent',
                'progress_fg': '#343a40',
                'font_family': 'Arial, sans-serif',
                'font_size_title': '14px',
                'font_size_subtitle': '11px',
                'font_size_time': '10px',
            },
            # Otros temas disponibles (comentados por ahora)
            # 'default': {
            #     'bg_color': '#1a1a1a',
            #     'text_color': '#ffffff',
            #     'accent_color': '#e5a00d',
            #     'progress_bg': '#333333',
            #     'progress_fg': '#e5a00d',
            #     'font_family': 'Arial, sans-serif',
            #     'font_size_title': '16px',
            #     'font_size_subtitle': '12px',
            #     'font_size_time': '10px',
            # },
            # 'dark': {
            #     'bg_color': '#0d1117',
            #     'text_color': '#f0f6fc',
            #     'accent_color': '#58a6ff',
            #     'progress_bg': '#21262d',
            #     'progress_fg': '#58a6ff',
            #     'font_family': 'Arial, sans-serif',
            #     'font_size_title': '16px',
            #     'font_size_subtitle': '12px',
            #     'font_size_time': '10px',
            # },
            # 'compact': {
            #     'bg_color': '#2d3748',
            #     'text_color': '#e2e8f0',
            #     'accent_color': '#68d391',
            #     'progress_bg': '#4a5568',
            #     'progress_fg': '#68d391',
            #     'font_family': 'Arial, sans-serif',
            #     'font_size_title': '14px',
            #     'font_size_subtitle': '11px',
            #     'font_size_time': '9px',
            # }
        }
    
    def generate_now_playing_svg(self, session_data: Optional[Dict[str, Any]]) -> str:
        """
        Genera SVG con información de reproducción actual
        
        Args:
            session_data: Datos de la sesión actual o None si no hay reproducción
            
        Returns:
            String con el SVG generado
        """
        if not session_data:
            logger.info("SVG: session_data es None, generando SVG idle")
            return self._generate_idle_svg()
        
        # Si es historial (state='stopped'), mostrarlo como música
        if session_data.get('state') == 'stopped' and session_data.get('type') == 'track':
            return self._generate_music_svg(session_data)
        
        # Generar SVG según el tipo de contenido
        if session_data['type'] == 'track':
            return self._generate_music_svg(session_data)
        elif session_data['type'] == 'episode':
            return self._generate_tv_svg(session_data)
        elif session_data['type'] == 'movie':
            return self._generate_movie_svg(session_data)
        else:
            return self._generate_generic_svg(session_data)
    
    def _generate_idle_svg(self) -> str:
        """Genera SVG cuando no hay reproducción activa"""
        theme = self.themes[self.theme]
        
        svg = f'''
        <svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <style>
                    .idle-text {{
                        font-family: {theme['font_family']};
                        fill: {theme['text_color']};
                        font-size: {theme['font_size_title']};
                        text-anchor: middle;
                        animation: pulse 2s ease-in-out infinite alternate;
                    }}
                    .idle-subtitle {{
                        font-family: {theme['font_family']};
                        fill: {theme['accent_color']};
                        font-size: {theme['font_size_subtitle']};
                        text-anchor: middle;
                        opacity: 0.8;
                    }}
                    @keyframes pulse {{
                        from {{ opacity: 0.6; }}
                        to {{ opacity: 1; }}
                    }}
                </style>
            </defs>
            
            <text x="{self.width//2}" y="{self.height//2 - 10}" class="idle-text">
                ⏸️ Sin contenido
            </text>
            <text x="{self.width//2}" y="{self.height//2 + 15}" class="idle-subtitle">
                Sin actividad
            </text>
        </svg>
        '''
        return svg.strip()
    
    def _generate_music_svg(self, data: Dict[str, Any]) -> str:
        """Genera SVG para música con animaciones"""
        theme = self.themes[self.theme]
        
        # Información de la canción
        track_title = data.get('track_title', data.get('title', 'Canción desconocida'))
        artist = data.get('artist', 'Artista desconocido')
        album = data.get('album', 'Álbum desconocido')
        
        # Calcular si necesita marquee según longitud
        artist_album_text = f"{artist} • {album}"
        max_chars_visible = 41  # Caracteres que caben sin scroll
        
        # Con 400px de ancho, podemos mostrar más texto sin marquee
        max_chars_visible = 41  # Límite ajustado para fuente de 14px
        
        # Barras ocupan TODO el ancho disponible (400px total)
        bar_area_width = 300  # 400px - 80px portada - 20px gap = 300px
        
        # Determinar si necesita animación marquee
        title_needs_marquee = len(track_title) > max_chars_visible
        artist_needs_marquee = len(artist_album_text) > max_chars_visible
        
        # Progreso
        progress = 0
        if data.get('duration', 0) > 0:
            progress = (data.get('progress', 0) / data['duration']) * 100
        
        # Tiempos
        current_time = self._format_duration(data.get('progress', 0))
        total_time = self._format_duration(data.get('duration', 0))
        
        # Thumbnail como base64 y extracción de colores
        thumbnail_data = ""
        extracted_colors = None
        if data.get('thumb'):
            thumbnail_data = self._get_thumbnail_base64(data['thumb'])
            extracted_colors = self._extract_colors_from_image(data['thumb'])
        
        # Estado
        is_playing = data.get('state') == 'playing'
        state_emoji = "▶️" if is_playing else "⏸️"
        
        # Las barras de ecualizador se generan directamente en el SVG
        
        svg = f'''
        <svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <style>
                    .song-title {{
                        font-family: {theme['font_family']};
                        fill: {theme['text_color']};
                        font-size: {theme['font_size_title']};
                        font-weight: bold;
                    }}
                    .song-info {{
                        font-family: {theme['font_family']};
                        fill: {theme['accent_color']};
                        font-size: {theme['font_size_subtitle']};
                    }}
                    .time-text {{
                        font-family: {theme['font_family']};
                        fill: {theme['text_color']};
                        font-size: {theme['font_size_time']};
                        opacity: 0.9;
                    }}
                    .progress-bg {{
                        fill: {theme['progress_bg']};
                        opacity: 0.3;
                    }}
                    .progress-fg {{
                        fill: {theme['progress_fg']};
                        animation: progress-glow 2s ease-in-out infinite alternate;
                    }}
                    .state-emoji {{
                        font-size: 16px;
                    }}
                    @keyframes progress-glow {{
                        from {{ opacity: 0.8; }}
                        to {{ opacity: 1; }}
                    }}
                    .fade-in {{
                        animation: fadeIn 1s ease-in;
                    }}
                    @keyframes fadeIn {{
                        from {{ opacity: 0; transform: translateY(10px); }}
                        to {{ opacity: 1; transform: translateY(0); }}
                    }}
                </style>
            </defs>
            
            <!-- Thumbnail placeholder o imagen -->
            <rect x="5" y="5" width="80" height="80" rx="8" fill="{theme['progress_bg']}" opacity="0.2"/>
            {f'<image x="5" y="5" width="80" height="80" href="{thumbnail_data}" />' if thumbnail_data else ''}
            {f'<text x="50" y="85" text-anchor="middle" style="font-size: 24px;">🎵</text>' if not thumbnail_data else ''}
            
            <!-- Área de recorte para texto (más ancha con 450px) -->
            <defs>
                <clipPath id="textClip">
                    <rect x="95" y="5" width="300" height="80"/>
                </clipPath>
            </defs>
            
            <!-- Información de la canción con marquee inteligente -->
            <g clip-path="url(#textClip)">
                <text x="95" y="16" class="song-title fade-in">
                    {self._escape_xml(track_title)}
                    {f'<animate attributeName="x" values="95;{95 - len(track_title) * 4 + 95};95" dur="12s" repeatCount="indefinite"/>' if title_needs_marquee else ''}
                </text>
                <text x="95" y="36" class="song-info fade-in">
                    {self._escape_xml(artist_album_text)}
                    {f'<animate attributeName="x" values="95;{95 - len(artist_album_text) * 4 + 95};95" dur="15s" repeatCount="indefinite"/>' if artist_needs_marquee else ''}
                </text>
            </g>
            
            <!-- Ecualizador estilo Spotify (solo cuando reproduce) -->
            {self._generate_enhanced_equalizer_bars(theme, is_playing, 95, 56, extracted_colors, 300)}
            
        </svg>
        '''
        return svg.strip()
    
    def _generate_tv_svg(self, data: Dict[str, Any]) -> str:
        """Genera SVG para series/episodios"""
        theme = self.themes[self.theme]
        
        # Información del episodio
        show_title = data.get('show_title', 'Serie desconocida')
        season = data.get('season', 0)
        episode = data.get('episode', 0)
        episode_title = data.get('episode_title', data.get('title', 'Episodio'))
        
        # Progreso
        progress = 0
        if data.get('duration', 0) > 0:
            progress = (data.get('progress', 0) / data['duration']) * 100
        
        # Tiempos
        current_time = self._format_duration(data.get('progress', 0))
        total_time = self._format_duration(data.get('duration', 0))
        
        # Thumbnail y extracción de colores para series
        thumbnail_data = ""
        extracted_colors = None
        if data.get('thumb'):
            thumbnail_data = self._get_thumbnail_base64(data['thumb'])
            extracted_colors = self._extract_colors_from_image(data['thumb'])
        
        # Estado
        is_playing = data.get('state') == 'playing'
        state_emoji = "▶️" if is_playing else "⏸️"
        
        svg = f'''
        <svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <style>
                    .show-title {{
                        font-family: {theme['font_family']};
                        fill: {theme['text_color']};
                        font-size: {theme['font_size_title']};
                        font-weight: bold;
                    }}
                    .episode-info {{
                        font-family: {theme['font_family']};
                        fill: {theme['accent_color']};
                        font-size: {theme['font_size_subtitle']};
                    }}
                    .time-text {{
                        font-family: {theme['font_family']};
                        fill: {theme['text_color']};
                        font-size: {theme['font_size_time']};
                        opacity: 0.9;
                    }}
                    .progress-bg {{
                        fill: {theme['progress_bg']};
                        opacity: 0.3;
                    }}
                    .progress-fg {{
                        fill: {theme['progress_fg']};
                        animation: progress-slide 3s ease-in-out infinite;
                    }}
                    .state-emoji {{
                        font-size: 16px;
                        animation: {'pulse 2s infinite' if is_playing else 'none'};
                    }}
                    @keyframes progress-slide {{
                        0% {{ opacity: 0.6; }}
                        50% {{ opacity: 1; }}
                        100% {{ opacity: 0.6; }}
                    }}
                    @keyframes pulse {{
                        0% {{ opacity: 1; transform: scale(1); }}
                        50% {{ opacity: 0.8; transform: scale(1.1); }}
                        100% {{ opacity: 1; transform: scale(1); }}
                    }}
                </style>
            </defs>
            
            <!-- Thumbnail placeholder o imagen -->
            <rect x="5" y="5" width="80" height="80" rx="8" fill="transparent" opacity="0.0"/>
            {f'<image x="5" y="5" width="80" height="80" href="{thumbnail_data}" />' if thumbnail_data else ''}
            {f'<text x="50" y="85" text-anchor="middle" style="font-size: 24px;">📺</text>' if not thumbnail_data else ''}
            
            <!-- Información del episodio -->
            <text x="95" y="50" class="show-title">
                {self._escape_xml(self._truncate_text(f"{show_title} • S{season:02d}E{episode:02d}", 55))}
            </text>
            <text x="95" y="70" class="episode-info">
                {self._escape_xml(self._truncate_text(episode_title, 30))}
            </text>
            
            <!-- Ecualizador estilo Spotify (solo cuando reproduce) -->
            {self._generate_enhanced_equalizer_bars(theme, is_playing, 95, 56, extracted_colors, 300)}
            
        </svg>
        '''
        return svg.strip()
    
    def _generate_movie_svg(self, data: Dict[str, Any]) -> str:
        """Genera SVG para películas"""
        # Por ahora usar el mismo layout que TV
        return self._generate_tv_svg(data)
    
    def _generate_generic_svg(self, data: Dict[str, Any]) -> str:
        """Genera SVG genérico"""
        return self._generate_tv_svg(data)
    
    def _generate_enhanced_equalizer_bars(self, theme: Dict[str, Any], is_playing: bool, start_x: int, start_y: int, extracted_colors: Optional[List[Tuple[int, int, int]]] = None, bar_area_width: float = 330) -> str:
        """Genera ecualizador estilo novatorem.svg"""
        # Siempre mostrar barras animadas, sin importar el estado
        # if not is_playing:
        #     return f'''
        #     <g opacity="0.3">
        #         <text x="{start_x}" y="{start_y + 15}" 
        #               style="font-family: {theme['font_family']}; font-size: 12px; fill: {theme['text_color']};">
        #             ⏸️ Pausado
        #         </text>
        #     </g>
        #     '''
        
        bars = []
        # Configuración para barras más gruesas
        bar_width = 2   # Más delgadas (2px)
        bar_spacing = 1 # Muy juntas
        base_y_fixed = start_y + 25  # LÍNEA BASE FIJA - todas parten de aquí
        
        # Calcular número de barras para ocupar exactamente 300px
        pixels_per_bar = bar_width + bar_spacing  # 2px + 1px = 3px por barra
        bar_count = int(300 // pixels_per_bar)  # 300px ÷ 3px = 100 barras
        
        # Crear degradado dinámico basado en colores de la carátula
        gradient_id = "barGradient"
        if extracted_colors:
            gradient_def = f'<defs>{self._create_dynamic_gradient(extracted_colors, gradient_id)}</defs>'
        else:
            # Fallback a colores por defecto
            fallback_colors = [
                (122, 216, 255),  # #7ad8ff
                (94, 255, 105),   # #5eff69
                (120, 255, 140),  # #78ff8c
                (122, 216, 255)   # #7ad8ff
            ]
            gradient_def = f'<defs>{self._create_dynamic_gradient(fallback_colors, gradient_id)}</defs>'
        
        # Generar barras con degradado animado
        for i in range(bar_count):
            x = start_x + i * (bar_width + bar_spacing)
            
            # Patrones de altura (pulse animation como en novatorem)
            if i % 7 == 0:  # Barras principales
                heights = "3;15;3;15;3;15;3"
            elif i % 5 == 0:  # Barras secundarias
                heights = "2;12;2;12;2;12;2"
            elif i % 3 == 0:  # Barras medias
                heights = "4;22;4;22;4;22;4"
            else:  # Barras normales
                heights = "2;10;2;10;2;10;2"
            
            # Timing más lento (mitad de velocidad)
            duration = 1.6 + (i % 4) * 0.4  # Entre 1.6s y 2.8s (mitad de velocidad)
            delay = (i * 0.05) % 1.0  # Desfase progresivo
            
            # Calcular Y dinámicamente para que crezca hacia arriba
            y_values = []
            height_list = heights.split(';')
            for h in height_list:
                y_values.append(str(base_y_fixed - int(h)))
            y_animation = ';'.join(y_values)
            
            bars.append(f'''
            <rect x="{x}" y="{base_y_fixed}" width="{bar_width}" height="3" 
                  fill="url(#{gradient_id})" opacity="0.95">
                <animate attributeName="height" 
                         values="{heights}" 
                         dur="{duration}s" 
                         begin="{delay}s"
                         repeatCount="indefinite"/>
                <animate attributeName="y" 
                         values="{y_animation}" 
                         dur="{duration}s" 
                         begin="{delay}s"
                         repeatCount="indefinite"/>
                <animate attributeName="opacity" 
                         values="0.35;0.95;0.35;0.95;0.35;0.95;0.35" 
                         dur="{duration}s" 
                         begin="{delay}s"
                         repeatCount="indefinite"/>
            </rect>
            ''')
        
        return f'{gradient_def}<g class="equalizer-container">{"".join(bars)}</g>'
    
    def _get_thumbnail_base64(self, url: str, target_size: tuple = (120, 120)) -> str:
        """Obtiene thumbnail, lo redimensiona y convierte a base64 para embeber en SVG"""
        try:
            from PIL import Image
            import io
            
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            # Abrir imagen con PIL
            image = Image.open(io.BytesIO(response.content))
            
            # Redimensionar manteniendo aspect ratio y centrando
            image.thumbnail(target_size, Image.Resampling.LANCZOS)
            
            # Crear imagen cuadrada con fondo transparente si es necesario
            if image.size != target_size:
                new_image = Image.new('RGBA', target_size, (255, 255, 255, 0))  # Transparente
                # Centrar la imagen redimensionada
                paste_x = (target_size[0] - image.size[0]) // 2
                paste_y = (target_size[1] - image.size[1]) // 2
                new_image.paste(image, (paste_x, paste_y))
                image = new_image
            
            # Procesar imagen para quitar fondo blanco
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Obtener datos de píxeles
            data = image.getdata()
            new_data = []
            
            # Procesar cada píxel
            for item in data:
                # Si el píxel es blanco o muy claro, hacerlo transparente
                if item[0] > 240 and item[1] > 240 and item[2] > 240:
                    new_data.append((255, 255, 255, 0))  # Transparente
                else:
                    new_data.append(item)
            
            # Aplicar los nuevos datos
            image.putdata(new_data)
            
            # Convertir a base64 con fondo transparente
            buffer = io.BytesIO()
            image.save(buffer, format='PNG', optimize=True)
            image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return f"data:image/png;base64,{image_data}"
        except Exception as e:
            logger.warning(f"Error procesando thumbnail para SVG: {e}")
            return ""
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Trunca texto si es muy largo"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def _escape_xml(self, text: str) -> str:
        """Escapa caracteres especiales para XML"""
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')
    
    def _format_duration(self, seconds: int) -> str:
        """Formatea duración en segundos a MM:SS o HH:MM:SS"""
        if seconds < 3600:  # Menos de 1 hora
            return str(timedelta(seconds=seconds))[2:7]  # MM:SS
        else:  # 1 hora o más
            return str(timedelta(seconds=seconds))[0:7]  # H:MM:SS
    
    def _extract_colors_from_image(self, image_url: str) -> List[Tuple[int, int, int]]:
        """Extrae colores dominantes de la carátula como hace novatorem"""
        try:
            # Descargar imagen
            response = requests.get(image_url, timeout=5)
            response.raise_for_status()
            
            # Convertir a PIL Image
            image = Image.open(io.BytesIO(response.content))
            
            # Redimensionar para acelerar procesamiento
            image = image.resize((150, 150), Image.Resampling.LANCZOS)
            
            # Guardar temporalmente para ColorThief
            temp_buffer = io.BytesIO()
            image.save(temp_buffer, format='PNG')
            temp_buffer.seek(0)
            
            # Extraer paleta de colores
            color_thief = ColorThief(temp_buffer)
            
            # Obtener 4 colores dominantes (como en novatorem)
            palette = color_thief.get_palette(color_count=4, quality=10)
            
            logger.info(f"Colores extraídos: {palette}")
            return palette
            
        except Exception as e:
            logger.warning(f"Error extrayendo colores: {e}")
            # Fallback a colores por defecto estilo novatorem
            return [
                (122, 216, 255),  # #7ad8ff - azul claro
                (94, 255, 105),   # #5eff69 - verde
                (120, 255, 140),  # #78ff8c - verde claro
                (122, 216, 255)   # #7ad8ff - azul claro
            ]
    
    def _create_dynamic_gradient(self, colors: List[Tuple[int, int, int]], gradient_id: str) -> str:
        """Crea degradado dinámico basado en colores extraídos"""
        gradient_def = f'''
        <linearGradient id="{gradient_id}" x1="0%" y1="0%" x2="100%" y2="0%">
        '''
        
        # Crear stops del degradado con los colores extraídos
        for i, color in enumerate(colors):
            offset = (i * 100) // (len(colors) - 1) if len(colors) > 1 else 0
            rgb = f"rgb({color[0]}, {color[1]}, {color[2]})"
            
            # Crear animación de colores que rota entre todos los colores
            color_values = []
            for j in range(len(colors)):
                next_color = colors[(i + j) % len(colors)]
                color_values.append(f"rgb({next_color[0]}, {next_color[1]}, {next_color[2]})")
            color_values.append(color_values[0])  # Volver al inicio
            
            gradient_def += f'''
            <stop offset="{offset}%" style="stop-color:{rgb};stop-opacity:1">
                <animate attributeName="stop-color" 
                         values="{';'.join(color_values)}" 
                         dur="15s" 
                         repeatCount="indefinite"/>
            </stop>
            '''
        
        gradient_def += '''
        </linearGradient>
        '''
        
        return gradient_def
