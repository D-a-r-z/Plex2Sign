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

    def _extract_colors_from_image(self, image_url: str, num_colors: int = 4) -> Optional[List[Tuple[int, int, int]]]:
        """Extrae los colores dominantes de una imagen usando ColorThief."""
        try:
            response = requests.get(image_url, timeout=5)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content))
            img = img.convert('RGB')
            with io.BytesIO() as buf:
                img.save(buf, format='PNG')
                buf.seek(0)
                ct = ColorThief(buf)
                palette = ct.get_palette(color_count=num_colors)
            return palette
        except Exception as e:
            logger.warning(f"No se pudieron extraer colores de la imagen: {e}")
            return None

    def _create_dynamic_gradient(self, colors: List[Tuple[int, int, int]], gradient_id: str = "barGradient") -> str:
        """Crea un gradiente SVG <linearGradient> a partir de una lista de colores RGB."""
        if not colors:
            colors = [(122, 216, 255), (94, 255, 105), (120, 255, 140), (122, 216, 255)]
        stops = []
        n = len(colors)
        for i, color in enumerate(colors):
            offset = int(i * 100 / (n - 1)) if n > 1 else 0
            stops.append(f'<stop offset="{offset}%" stop-color="rgb{color}" />')
        return f'<linearGradient id="{gradient_id}" x1="0%" y1="0%" x2="100%" y2="0%">{"".join(stops)}</linearGradient>'

    def _escape_xml(self, text: str) -> str:
        """Escapa caracteres especiales para uso seguro en XML/SVG."""
        if not isinstance(text, str):
            text = str(text)
        return (
            text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&apos;')
        )

    def _format_duration(self, seconds: int) -> str:
        """Convierte segundos en una cadena hh:mm:ss o mm:ss"""
        if seconds is None or seconds <= 0:
            return "0:00"
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
    def _load_themes(self) -> Dict[str, Dict[str, Any]]:
        """Devuelve un diccionario con temas por defecto usados por el generador.

        Cada tema incluye las claves que el resto del código espera:
        `font_family`, `text_color`, `accent_color`, `progress_bg`,
        `progress_fg`, `font_size_title`, `font_size_subtitle`, `font_size_time`.
        """
        base = {
            'font_family': 'Arial, Helvetica, sans-serif',
            'font_size_title': '15px',
            'font_size_subtitle': '12px',
            'font_size_time': '11px',
        }
        themes = {
            'normal': {
                **base,
                'text_color': '#FFFFFF',
                'accent_color': '#7ad8ff',
                'progress_bg': '#000000',
                'progress_fg': '#7ad8ff'
            },
            'dark': {
                **base,
                'text_color': '#E6E6E6',
                'accent_color': '#78ff8c',
                'progress_bg': '#0F1720',
                'progress_fg': '#78ff8c'
            },
            'minimal': {
                **base,
                'text_color': '#FFFFFF',
                'accent_color': '#5eff69',
                'progress_bg': '#111827',
                'progress_fg': '#5eff69'
            }
        }
        return themes

    def __init__(self, width: int = 400, height: int = 90, theme: str = 'minimal'):
        self.width = width
        self.height = height
        self.theme = theme
        self.themes = self._load_themes()
    
    def _generate_tv_svg(self, data: Dict[str, Any]) -> str:
        """Genera SVG para series/episodios"""
        theme = self.themes[self.theme]
        show_title = data.get('show_title', data.get('title', 'Serie desconocida'))
        season = data.get('season', 1)
        episode = data.get('episode', 1)
        episode_title = data.get('episode_title', data.get('title', 'Episodio desconocido'))
        
        # Información del episodio
        
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
            
            <!-- Área de recorte para texto (igual que música) -->
            <defs>
                <clipPath id="textClipTV">
                    <rect x="95" y="5" width="300" height="80"/>
                </clipPath>
            </defs>
            
            <!-- Información del episodio con posiciones iguales a música -->
            <g clip-path="url(#textClipTV)">
                <text x="95" y="16" class="show-title">
                    {self._escape_xml(self._truncate_text(f"{show_title} • S{season:02d}E{episode:02d}", 55))}
                </text>
                <text x="95" y="36" class="episode-info">
                    {self._escape_xml(self._truncate_text(episode_title, 30))}
                </text>
            </g>
            
            <!-- Ecualizador estilo Spotify (solo cuando reproduce) -->
            {self._generate_enhanced_equalizer_bars(theme, is_playing, 95, 56, extracted_colors, 300)}
            
        </svg>
        '''
        return svg.strip()

    def generate_now_playing_svg(self, data: Optional[Dict[str, Any]]) -> str:
        """Public API: genera el SVG apropiado según el tipo de contenido.

        - Si `data` es None o no contiene `type`, devuelve un SVG 'idle'.
        - Si `type` es 'track' -> música, 'episode' -> TV, 'movie' -> película.
        """
        try:
            if not data:
                # Simple idle SVG
                theme = self._load_themes().get(self.theme, self._load_themes()['minimal'])
                return f"<svg width=\"{self.width}\" height=\"{self.height}\" xmlns=\"http://www.w3.org/2000/svg\"><rect width=\"100%\" height=\"100%\" fill=\"{theme['progress_bg']}\"/><text x=\"50%\" y=\"50%\" dominant-baseline=\"middle\" text-anchor=\"middle\" fill=\"{theme['text_color']}\">⏸️ Sin actividad</text></svg>"

            content_type = data.get('type', 'track')
            if content_type == 'track':
                return self._generate_music_svg(data)
            elif content_type == 'episode':
                return self._generate_tv_svg(data)
            elif content_type == 'movie':
                return self._generate_movie_svg(data)
            else:
                return self._generate_generic_svg(data)
        except Exception as e:
            logger.error(f"Error generando SVG en dispatcher: {e}")
            # Fallback simple
            return f"<svg width=\"{self.width}\" height=\"{self.height}\" xmlns=\"http://www.w3.org/2000/svg\"><text x=\"10\" y=\"20\">Error generando SVG</text></svg>"
    
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
            
            # Redimensionar manteniendo aspect ratio y centrando (método original)
            image.thumbnail(target_size, Image.Resampling.LANCZOS)
            
            # Crear imagen cuadrada con fondo transparente si es necesario
            if image.size != target_size:
                new_image = Image.new('RGBA', target_size, (255, 255, 255, 0))  # Transparente
                # Centrar la imagen redimensionada
                paste_x = (target_size[0] - image.size[0]) // 2
                paste_y = (target_size[1] - image.size[1]) // 2
                new_image.paste(image, (paste_x, paste_y))
                image = new_image
            
            # Procesar imagen para quitar fondo blanco de forma inteligente
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Solo procesar si la imagen es más grande que el tamaño objetivo (tiene padding)
            # Para imágenes 80x80 (música) no procesar, para imágenes más grandes (películas/series) sí
            if image.size[0] > target_size[0] or image.size[1] > target_size[1]:
                # Obtener datos de píxeles
                data = image.getdata()
                new_data = []
                
                # Calcular área central que debe preservarse
                width, height = image.size
                center_x = width // 2
                center_y = height // 2
                preserve_radius = min(width, height) // 3  # Radio de área a preservar
                
                # Procesar cada píxel
                for y in range(height):
                    for x in range(width):
                        item = data[y * width + x]
                        
                        # Calcular distancia al centro
                        distance_to_center = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                        
                        # Si está en el área central, preservar siempre
                        if distance_to_center <= preserve_radius:
                            new_data.append(item)
                        # Si está fuera del área central y es blanco, hacer transparente
                        elif item[0] > 240 and item[1] > 240 and item[2] > 240:
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
        # Thumbnail: usar solo la URL de Plex
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
    
    def _interpolate_color(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], ratio: float) -> Tuple[int, int, int]:
        """Interpola entre dos colores RGB"""
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        return (r, g, b)
