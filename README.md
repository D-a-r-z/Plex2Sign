# 🎵 Plex2Sign

**[Español](#español)** | **[English](#english)**

---

## 🚀 Demo en Vivo

**Deploy en Vercel**: https://plex2-sign.vercel.app/

![Plex Now Playing](https://plex2-sign.vercel.app/api/now-playing-svg?theme=normal)

---

# Español

## 📋 Descripción

Plex2Sign es un generador de firmas dinámicas que muestra el contenido multimedia que estás reproduciendo actualmente desde tu servidor Plex Media Server. Similar al popular [spotify-github-profile](https://github.com/kittinan/spotify-github-profile), pero diseñado específicamente para usuarios de Plex.

Perfecto para:
- 🐙 **README del Perfil de GitHub**
- 💬 **Firmas de Foros**
- 📱 **Integración en Redes Sociales**
- 🎯 **Marca Personal**

---

## ✨ Características

### 🎨 Múltiples Formatos
- **SVG (Animado)**: Barras de ecualizador dinámicas con animaciones suaves
- **PNG (Estático)**: Imágenes limpias y estáticas con visualización de ecualizador

### 🌓 Soporte de Temas
- **Normal**: Fondo blanco limpio con acentos azules
- **Oscuro**: Fondo claro con texto oscuro para compatibilidad universal

### 🎵 Tipos de Media
- **Música**: Información de artista, álbum y canción con ecualizador animado
- **Series de TV**: Título de la serie, temporada, episodio con ecualizador estático
- **Películas**: Título de la película e información

### 🔧 Características Técnicas
- **Detección Automática del Servidor**: Usa la API de Plex Account para descubrir automáticamente el servidor externo
- **Extracción Dinámica de Colores**: Extrae colores de las portadas de álbumes para barras de ecualizador personalizadas
- **Manejo Inteligente de Texto**: Desplazamiento horizontal (marquee) para títulos largos
- **Imágenes de Alta Calidad**: Procesamiento a 120x120px para visualización nítida a 80x80px
- **Caché**: Caché eficiente de imágenes para reducir la carga del servidor

---

## 🛠️ Instalación

### Requisitos
- Token de Plex (obtenido desde https://support.plex.tv/articles/204059436/)
- Client ID de Imgur (opcional, para hosting de imágenes)

### Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/D-a-r-z/Plex2Sign.git
cd Plex2Sign
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**
Crear un archivo `.env`:
```env
PLEX_TOKEN=tu_token_de_plex_aqui
IMGUR_CLIENT_ID=tu_client_id_de_imgur_aqui
```

**📝 Filtrado automático de usuario:**
La aplicación filtra automáticamente el contenido por el usuario asociado a tu token de Plex. Cada usuario solo verá su propio contenido por defecto.

4. **Ejecutar localmente**
```bash
python app.py
```

Visita `http://localhost:5000` para ver el dashboard.

---

## 🌐 Despliegue

### Vercel (Recomendado)

1. **Hacer fork de este repositorio**
2. **Conectar a Vercel**
3. **Configurar variables de entorno**:
   - `PLEX_TOKEN`: Tu token de Plex
   - `IMGUR_CLIENT_ID`: Tu client ID de Imgur

**🔒 Filtrado automático de usuario:**
La aplicación filtra automáticamente el contenido por el usuario asociado a tu token de Plex. No se necesita configuración adicional.

La aplicación detectará automáticamente la URL externa de tu servidor Plex usando la API de Plex Account.

---

## 📖 Uso

### Perfil de GitHub

Añade esto a tu README del perfil de GitHub:

```markdown
![Plex Now Playing](https://tu-url-vercel.vercel.app/api/now-playing-svg?theme=normal)
```

### Firmas de Foro

Para fondos claros:
```markdown
![Plex Now Playing](https://tu-url-vercel.vercel.app/api/now-playing-svg?theme=dark)
```

### Endpoints Disponibles

- **SVG (Animado)**:
  - Normal: `/api/now-playing-svg?theme=normal`
  - Oscuro: `/api/now-playing-svg?theme=dark`

- **PNG (Estático)**:
  - Normal: `/api/now-playing-png?theme=normal`
  - Oscuro: `/api/now-playing-png?theme=dark`

### Soporte Multi-Usuario

Para deployments compartidos o filtrado de usuario específico:

- **Con token específico**: `?token=tu_token_de_plex`
- **Con usuario específico**: `?user=nombre_de_usuario`
- **Combinado**: `?token=tu_token_de_plex&user=nombre_de_usuario`

Ejemplo:
```markdown
![Plex Now Playing](https://tu-url-vercel.vercel.app/api/now-playing-svg?token=tu_token&user=tu_usuario)
```

---

## 🤝 Agradecimientos

- [kittinan/spotify-github-profile](https://github.com/kittinan/spotify-github-profile) - Inspiración y base del concepto
- [novatorem.svg](https://github.com/kittinan/spotify-github-profile/blob/master/img/novatorem.svg) - Estilo de barras de ecualizador animadas
- [PlexAPI](https://github.com/pkkid/python-plexapi) - Biblioteca Python para la API de Plex

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 🔗 Enlaces

- **GitHub**: https://github.com/D-a-r-z/Plex2Sign
- **Demo en Vivo**: https://plex2-sign.vercel.app/
- **Vercel Deploy**: [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/D-a-r-z/Plex2Sign)

---

# English

## 📋 Description

Plex2Sign is a dynamic signature generator that displays your currently playing media from Plex Media Server. Similar to the popular [spotify-github-profile](https://github.com/kittinan/spotify-github-profile), but designed specifically for Plex users.

Perfect for:
- 🐙 **GitHub Profile README**
- 💬 **Forum Signatures**
- 📱 **Social Media Integration**
- 🎯 **Personal Branding**

---

## ✨ Features

### 🎨 Multiple Formats
- **SVG (Animated)**: Dynamic equalizer bars with smooth animations
- **PNG (Static)**: Clean, static images with equalizer visualization

### 🌓 Theme Support
- **Normal**: Clean white background with blue accents
- **Dark**: Light background with dark text for universal compatibility

### 🎵 Media Types
- **Music**: Artist, album, and track information with animated equalizer
- **TV Shows**: Show title, season, episode with static equalizer
- **Movies**: Movie title and information

### 🔧 Technical Features
- **Auto Server Detection**: Uses Plex Account API for automatic external server discovery
- **Dynamic Color Extraction**: Extracts colors from album art for personalized equalizer bars
- **Smart Text Handling**: Horizontal scrolling (marquee) for long titles
- **High-Quality Images**: 120x120px processing for sharp 80x80px display
- **Caching**: Efficient image caching to reduce server load

---

## 🛠️ Setup

### Requirements
- Plex token (obtained from https://support.plex.tv/articles/204059436/)
- Imgur Client ID (optional, for image hosting)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/D-a-r-z/Plex2Sign.git
cd Plex2Sign
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
Create a `.env` file:
```env
PLEX_TOKEN=your_plex_token_here
IMGUR_CLIENT_ID=your_imgur_client_id_here
```

**📝 Automatic user filtering:**
The app automatically filters content by the user associated with your Plex token. Each user will only see their own content by default.

4. **Run locally**
```bash
python app.py
```

Visit `http://localhost:5000` to see the dashboard.

---

## 🌐 Deployment

### Vercel (Recommended)

1. **Fork this repository**
2. **Connect to Vercel**
3. **Set environment variables**:
   - `PLEX_TOKEN`: Your Plex token
   - `IMGUR_CLIENT_ID`: Your Imgur client ID

**🔒 Automatic user filtering:**
The app automatically filters content by the user associated with your Plex token. No additional configuration needed.

The app will automatically detect your Plex server's external URL using the Plex Account API.

---

## 📖 Usage

### GitHub Profile

Add this to your GitHub profile README:

```markdown
![Plex Now Playing](https://your-vercel-url.vercel.app/api/now-playing-svg?theme=normal)
```

### Forum Signatures

For light backgrounds:
```markdown
![Plex Now Playing](https://your-vercel-url.vercel.app/api/now-playing-svg?theme=dark)
```

### Available Endpoints

- **SVG (Animated)**:
  - Normal: `/api/now-playing-svg?theme=normal`
  - Dark: `/api/now-playing-svg?theme=dark`

- **PNG (Static)**:
  - Normal: `/api/now-playing-png?theme=normal`
  - Dark: `/api/now-playing-png?theme=dark`

### Multi-User Support

For shared deployments or specific user filtering:

- **With specific token**: `?token=your_plex_token`
- **With specific user**: `?user=username`
- **Combined**: `?token=your_plex_token&user=username`

Example:
```markdown
![Plex Now Playing](https://your-vercel-url.vercel.app/api/now-playing-svg?token=your_token&user=your_username)
```

---

## 🤝 Acknowledgments

- [kittinan/spotify-github-profile](https://github.com/kittinan/spotify-github-profile) - Inspiration and base concept
- [novatorem.svg](https://github.com/kittinan/spotify-github-profile/blob/master/img/novatorem.svg) - Animated equalizer bars style
- [PlexAPI](https://github.com/pkkid/python-plexapi) - Python library for Plex API

---

## 📄 License

This project is under the MIT License. See [LICENSE](LICENSE) for more details.

---

## 🔗 Links

- **GitHub**: https://github.com/D-a-r-z/Plex2Sign
- **Live Demo**: https://plex2-sign.vercel.app/
- **Vercel Deploy**: [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/D-a-r-z/Plex2Sign)