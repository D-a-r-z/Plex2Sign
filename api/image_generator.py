"""
Generador de imágenes PNG renderizando desde SVG
"""
import os
import io
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ImageGenerator:
    """Generador de imágenes PNG renderizando desde SVG"""
    
    def __init__(self, theme: str = 'normal', width: int = 400, height: int = 90):
        """
        Inicializa el generador de imágenes
        
        Args:
            theme: Tema visual a usar
            width: Ancho de la imagen
            height: Alto de la imagen
        """
        self.theme = theme
        self.width = width
        self.height = height
    
    def generate_now_playing_image(self, session_data: Optional[Dict[str, Any]]) -> io.BytesIO:
        """
        Genera imagen PNG renderizando el SVG correspondiente
        
        Args:
            session_data: Datos de la sesión actual o None si no hay reproducción
            
        Returns:
            BytesIO con la imagen PNG generada
        """
        try:
            # Importar SVGGenerator
            from api.svg_generator import SVGGenerator
            
            # Generar SVG
            svg_generator = SVGGenerator(theme=self.theme)
            svg_content = svg_generator.generate_now_playing_svg(session_data)
            
            # Generar PNG manualmente (cairosvg no funciona en Vercel)
            logger.info("🎨 Generando PNG manualmente (igual que SVG)")
            return self._generate_manual_png_from_svg(session_data)
                    
        except Exception as e:
            logger.warning(f"Error renderizando SVG como PNG: {e}")
            return self._generate_manual_png_from_svg(session_data)
    
    def _generate_manual_png_from_svg(self, session_data: Optional[Dict[str, Any]]) -> io.BytesIO:
        """
        Genera PNG manualmente copiando exactamente el SVG (sin animaciones)
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            import requests
            
            # Crear imagen con fondo transparente
            img = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            # Si es historial (state='stopped'), mostrarlo como música
            if session_data and session_data.get('state') == 'stopped' and session_data.get('type') == 'track':
                # Continuar con la generación normal (es música del historial)
                pass
            elif not session_data:
                logger.info("PNG: session_data es None, generando PNG idle")
                return self._generate_idle_png(draw)
            
            # Obtener tema
            from api.svg_generator import SVGGenerator
            svg_gen = SVGGenerator(theme=self.theme)
            themes = svg_gen._load_themes()
            theme = themes[self.theme]
            
            # Posiciones exactas del SVG (actualizadas para coincidir)
            thumb_size = 80
            thumb_x = 5   # Igual que SVG: x="5"
            thumb_y = 5   # Igual que SVG: y="5" 
            text_x = 95   # Igual que SVG: x="95" (gap de 10px como en SVG)
            
            # Descargar y procesar thumbnail
            thumbnail = None
            if session_data.get('thumb'):
                thumbnail = self._download_thumbnail(session_data['thumb'])
            
            # Dibujar thumbnail
            if thumbnail:
                thumbnail = thumbnail.resize((thumb_size, thumb_size), Image.Resampling.LANCZOS)
                img.paste(thumbnail, (thumb_x, thumb_y))
            else:
                # Placeholder - sin fondo para series/películas
                if session_data['type'] == 'track':
                    # Solo música tiene fondo sutil
                    placeholder_color = self._hex_to_rgb(theme['progress_bg'])
                    placeholder_color = tuple(list(placeholder_color) + [180])  # Semi-transparente
                    placeholder_img = Image.new('RGBA', (thumb_size, thumb_size), placeholder_color)
                    img.paste(placeholder_img, (thumb_x, thumb_y), placeholder_img)
                # Para series/películas no se dibuja fondo
                
                # Emoji placeholder
                try:
                    font = ImageFont.truetype("arial.ttf", 40)
                except:
                    font = ImageFont.load_default()
                
                emoji = "⏸️" if session_data['type'] == 'track' else "📺"
                bbox = draw.textbbox((0, 0), emoji, font=font)
                emoji_width = bbox[2] - bbox[0]
                emoji_height = bbox[3] - bbox[1]
                emoji_x = thumb_x + (thumb_size - emoji_width) // 2
                emoji_y = thumb_y + (thumb_size - emoji_height) // 2
                draw.text((emoji_x, emoji_y), emoji, fill=theme['accent_color'], font=font)
            
            # Texto (fuentes desde archivo + baseline correcto)
            try:
                # Arial: Bold para títulos, Normal para subtítulos
                font_bold_path = os.path.join(os.path.dirname(__file__), "../assets/fonts/ARIALBD.TTF")
                font_normal_path = os.path.join(os.path.dirname(__file__), "../assets/fonts/ARIAL.TTF")
                font_title = ImageFont.truetype(font_bold_path, 14)  # SVG: 15px -> PNG: 14px (BOLD)
                font_subtitle = ImageFont.truetype(font_normal_path, 11)  # SVG: 12px -> PNG: 11px (NORMAL)
            except:
                try:
                    # Fallback a Arial del sistema
                    font_title = ImageFont.truetype("arial.ttf", 14)
                    font_subtitle = ImageFont.truetype("arial.ttf", 11)
                except:
                    try:
                        # Fallback a fuentes del sistema Windows
                        font_title = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
                        font_subtitle = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 11)
                    except:
                        # Último fallback
                        font_title = ImageFont.load_default()
                        font_subtitle = ImageFont.load_default()
            
            # Generar texto según tipo
            if session_data['type'] == 'track':
                # Música
                track_title = session_data.get('track_title', session_data.get('title', 'Canción desconocida'))
                artist = session_data.get('artist', 'Artista desconocido')
                album = session_data.get('album', 'Álbum desconocido')
                
                # Truncar si es muy largo
                max_width = self.width - text_x - 10
                track_title = self._truncate_text(draw, track_title, font_title, max_width)
                artist_album = self._truncate_text(draw, f"{artist} • {album}", font_subtitle, max_width)
                
                # Dibujar texto (baseline correcto, igual que SVG)
                # SVG: y="16" y y="36" (baseline) -> PNG: calcular top desde baseline
                ascent_title, descent_title = font_title.getmetrics()
                y_baseline_title = 16  # Igual que SVG
                y_top_title = y_baseline_title - ascent_title
                draw.text((text_x, y_top_title), track_title, fill=theme['text_color'], font=font_title)
                
                ascent_sub, descent_sub = font_subtitle.getmetrics()
                y_baseline_sub = 36  # Igual que SVG
                y_top_sub = y_baseline_sub - ascent_sub
                draw.text((text_x, y_top_sub), artist_album, fill=theme['accent_color'], font=font_subtitle)
                
                # Barras estáticas (igual que dinámicas pero sin movimiento)
                # Posición ajustada: más arriba para que se vean mejor (height=90, posición en 82)
                # Alineadas con el texto (mismo text_x y mismo ancho que el texto)
                # Con fondo blur de la portada del álbum
                self._generate_static_bars(draw, img, text_x + 2, 82, max_width, theme, thumbnail)
                
            elif session_data['type'] == 'episode':
                # Serie
                show_title = session_data.get('show_title', 'Serie desconocida')
                season = session_data.get('season', 0)
                episode = session_data.get('episode', 0)
                episode_title = session_data.get('episode_title', session_data.get('title', 'Episodio'))
                
                max_width = self.width - text_x - 10
                show_info = self._truncate_text(draw, f"{show_title} • S{season:02d}E{episode:02d}", font_title, max_width)
                episode_info = self._truncate_text(draw, episode_title, font_subtitle, max_width)
                
                # Baseline correcto para series (igual que SVG)
                ascent_title, descent_title = font_title.getmetrics()
                y_baseline_title = 16  # Igual que SVG
                y_top_title = y_baseline_title - ascent_title
                draw.text((text_x, y_top_title), show_info, fill=theme['text_color'], font=font_title)
                
                ascent_sub, descent_sub = font_subtitle.getmetrics()
                y_baseline_sub = 36  # Igual que SVG
                y_top_sub = y_baseline_sub - ascent_sub
                draw.text((text_x, y_top_sub), episode_info, fill=theme['accent_color'], font=font_subtitle)
                
            else:
                # Película u otros
                title = session_data.get('title', 'Título desconocido')
                year = session_data.get('year', '')
                
                max_width = self.width - text_x - 10
                title_text = self._truncate_text(draw, title, font_title, max_width)
                
                # Baseline correcto para películas (igual que SVG)
                ascent_title, descent_title = font_title.getmetrics()
                y_baseline_title = 16  # Actualizado para coincidir con SVG
                y_top_title = y_baseline_title - ascent_title
                draw.text((text_x, y_top_title), title_text, fill=theme['text_color'], font=font_title)
                
                if year:
                    ascent_sub, descent_sub = font_subtitle.getmetrics()
                    y_baseline_sub = 36  # Actualizado para coincidir con SVG
                    y_top_sub = y_baseline_sub - ascent_sub
                    draw.text((text_x, y_top_sub), str(year), fill=theme['accent_color'], font=font_subtitle)
            
            # Convertir a BytesIO
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG', optimize=True)
            img_buffer.seek(0)
            return img_buffer
            
        except Exception as e:
            logger.error(f"Error generando PNG manual: {e}")
            return self._generate_error_png(session_data)
    
    def _generate_idle_png(self, draw) -> io.BytesIO:
        """Genera PNG cuando no hay reproducción"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Crear imagen
            img = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            text = "⏸️ Sin actividad"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (self.width - text_width) // 2
            y = (self.height - text_height) // 2
            
            draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
            
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG', optimize=True)
            img_buffer.seek(0)
            return img_buffer
            
        except Exception as e:
            logger.error(f"Error generando PNG idle: {e}")
            return self._generate_error_png(None)
    
    def _download_thumbnail(self, url: str, target_size: tuple = (120, 120)):
        """Descarga thumbnail desde URL y lo redimensiona"""
        try:
            import requests
            from PIL import Image
            
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            image = Image.open(io.BytesIO(response.content))
            image.thumbnail(target_size, Image.Resampling.LANCZOS)
            
            if image.size != target_size:
                new_image = Image.new('RGBA', target_size, (255, 255, 255, 0))
                paste_x = (target_size[0] - image.size[0]) // 2
                paste_y = (target_size[1] - image.size[1]) // 2
                new_image.paste(image, (paste_x, paste_y))
                image = new_image
            
            return image
        except Exception as e:
            logger.warning(f"Error descargando thumbnail: {e}")
            return None
    
    def _truncate_text(self, draw, text: str, font, max_width: int) -> str:
        """Trunca texto si excede el ancho máximo"""
        if draw.textlength(text, font=font) <= max_width:
            return text
        
        while len(text) > 3 and draw.textlength(text + "...", font=font) > max_width:
            text = text[:-1]
        
        return text + "..." if len(text) > 3 else text
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convierte color hexadecimal a RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _generate_static_bars(self, draw, img, start_x: int, start_y: int, width: int, theme: dict, thumbnail=None) -> None:
        """Genera barras de ecualizador estáticas con fondo del color dominante del álbum"""
        # Parámetros ajustados para mejor visualización
        bar_width = 2   # Ancho reducido a 2px para barras más finas
        bar_spacing = 1 # Separación de 1px
        
        # Usar el ancho que se pasa como parámetro (mismo que el texto)
        max_total_width = width
        
        # Calcular cuántas barras caben en el ancho disponible
        # Cada barra ocupa: bar_width + bar_spacing, excepto la última que no tiene spacing
        bar_count = (max_total_width + bar_spacing) // (bar_width + bar_spacing)
        # Añadir 2 barras más para ocupar mejor el espacio
        bar_count += 2
        total_bar_width = bar_count * (bar_width + bar_spacing) - bar_spacing
        
        # Centrar las barras en el ancho disponible
        bars_start_x = start_x + (width - total_bar_width) // 2
        
        # Generar alturas aleatorias pero consistentes (mismo seed para consistencia)
        import random
        random.seed(42)  # Seed fijo para que siempre sean las mismas alturas
        bar_heights = [random.randint(3, 22) for _ in range(bar_count)]
        
        # Crear fondo blur de la portada para las barras
        background_blur = None
        if thumbnail:
            try:
                from PIL import ImageFilter, Image
                
                # Crear una versión estirada y con blur de la portada
                # Redimensionar para cubrir toda el área de las barras
                bg_width = total_bar_width
                bg_height = max(bar_heights)
                
                # Estirar la imagen para cubrir el área de las barras
                # Asegurarse de que la orientación sea correcta
                background = thumbnail.copy()
                background = background.resize((bg_width, bg_height), Image.Resampling.LANCZOS)
                
                # Aplicar blur/bloom effect más sutil
                background_blur = background.filter(ImageFilter.GaussianBlur(radius=3))
                
                # Reducir opacidad para que no sea muy intenso
                background_blur = background_blur.convert('RGBA')
                # Ajustar la opacidad de toda la imagen
                alpha_data = []
                for pixel in background_blur.getdata():
                    # Mantener RGB pero reducir alpha a 150 (60% opacidad)
                    alpha_data.append((pixel[0], pixel[1], pixel[2], 150))
                background_blur.putdata(alpha_data)
                
                logger.info(f"Fondo blur creado: {bg_width}x{bg_height}")
                
            except Exception as e:
                logger.warning(f"Error creando fondo blur: {e}")
                background_blur = None
        
        # Dibujar cada barra individual con fondo blur como máscara
        for i in range(bar_count):
            bar_x = bars_start_x + i * (bar_width + bar_spacing)
            bar_height = bar_heights[i]
            bar_y = start_y - bar_height  # Crecer hacia arriba desde la base
            
            if background_blur:
                # Recortar la parte del fondo blur que corresponde a esta barra
                crop_x = bar_x - bars_start_x
                crop_y = 0  # Empezar desde arriba del fondo blur
                crop_box = (crop_x, crop_y, crop_x + bar_width, bar_height)
                
                try:
                    # Recortar la porción del fondo blur para esta barra
                    bar_bg = background_blur.crop(crop_box)
                    # Pegar solo esta porción en la posición de la barra
                    img.paste(bar_bg, (bar_x, bar_y), bar_bg)
                    logger.info(f"Barra {i}: pegando blur en ({bar_x}, {bar_y})")
                except Exception as e:
                    logger.warning(f"Error aplicando blur a barra {i}: {e}")
                    # Fallback: dibujar barra normal
                    bar_color = self._hex_to_rgb(theme['accent_color'])
                    draw.rectangle(
                        [bar_x, bar_y, bar_x + bar_width, start_y],
                        fill=bar_color
                    )
            else:
                # Fallback al color del tema si no hay fondo blur
                bar_color = self._hex_to_rgb(theme['accent_color'])
                draw.rectangle(
                    [bar_x, bar_y, bar_x + bar_width, start_y],
                    fill=bar_color
                )
    
    def _generate_error_png(self, session_data: Optional[Dict[str, Any]]) -> io.BytesIO:
        """
        Genera PNG básico de error si no se puede renderizar SVG
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Crear imagen básica con fondo transparente
            img = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            # Texto de error simple
            try:
                font = ImageFont.truetype("arial.ttf", 14)
            except:
                font = ImageFont.load_default()
            
            # Información básica
            if session_data:
                title = session_data.get('title', 'Unknown')
                artist = session_data.get('artist', '')
                if artist:
                    text = f"⏸️ {title}\n👤 {artist}"
                else:
                    text = f"📺 {title}"
            else:
                text = "⏸️ Sin actividad"
            
            # Centrar texto
            lines = text.split('\n')
            y_start = (self.height - len(lines) * 20) // 2
            
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (self.width - text_width) // 2
                y = y_start + i * 20
                
                # Fondo semi-transparente para el texto
                padding = 4
                draw.rectangle(
                    [x - padding, y - padding, x + text_width + padding, y + 16 + padding],
                    fill=(0, 0, 0, 128)
                )
                
                # Texto blanco
                draw.text((x, y), line, fill=(255, 255, 255, 255), font=font)
            
            # Convertir a BytesIO
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG', optimize=True)
            img_buffer.seek(0)
            return img_buffer
            
        except Exception as e:
            logger.error(f"Error generando PNG de fallback: {e}")
            # Retornar imagen vacía como último recurso
            try:
                from PIL import Image
                empty_img = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 255))
                img_buffer = io.BytesIO()
                empty_img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                return img_buffer
            except:
                # Último recurso: imagen mínima
                return io.BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01\x90\x00\x00\x00\x96\x08\x06\x00\x00\x00\x00\x00\x00\x00IEND\xaeB`\x82')
