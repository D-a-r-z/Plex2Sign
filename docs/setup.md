# Guía de Configuración de Plex2Sign

## 📋 Requisitos Previos

1. **Servidor Plex Media Server** funcionando y accesible
2. **Token de autenticación de Plex**
3. **Cuenta en Imgur** para obtener Client ID
4. **Cuenta en Vercel** (opcional, para deployment en la nube)

## 🔑 Obtener Token de Plex

### Método 1: Desde la interfaz web
1. Ve a tu servidor Plex: `http://TU_SERVIDOR:32400/web`
2. Abre las herramientas de desarrollador (F12)
3. Ve a la pestaña "Network"
4. Recarga la página
5. Busca cualquier petición y mira los headers
6. Copia el valor del header `X-Plex-Token`

### Método 2: Desde la URL
1. Ve a: `http://TU_SERVIDOR:32400/web/index.html#!/settings/account`
2. En la URL verás algo como: `...&X-Plex-Token=AQUI_ESTA_TU_TOKEN`

### Método 3: Usando curl (Linux/Mac)
```bash
curl -X POST 'https://plex.tv/users/sign_in.xml' \
  -H 'X-Plex-Client-Identifier: Plex2Sign' \
  -d 'user[login]=TU_EMAIL&user[password]=TU_PASSWORD'
```

## 🖼️ Configurar Imgur

1. Ve a [Imgur API](https://api.imgur.com/oauth2/addclient)
2. Registra una nueva aplicación:
   - **Application name**: Plex2Sign
   - **Authorization type**: Anonymous usage without user authorization
   - **Authorization callback URL**: (deja en blanco)
   - **Application website**: (opcional)
   - **Email**: tu email
   - **Description**: Plex2Sign image hosting
3. Copia el **Client ID** generado

## ⚙️ Configuración Local

### 1. Clonar y configurar
```bash
git clone https://github.com/tu-usuario/plex2sign.git
cd plex2sign
cp .env.example .env
```

### 2. Editar .env
```bash
# Configuración del servidor Plex
PLEX_URL=http://192.168.1.100:32400  # Cambia por tu IP/URL
PLEX_TOKEN=tu-token-de-plex-aqui

# Configuración de Imgur
IMGUR_CLIENT_ID=tu-client-id-de-imgur

# Configuración opcional
CACHE_DURATION=60
IMAGE_WIDTH=400
IMAGE_HEIGHT=150
DEFAULT_THEME=default

# Para desarrollo local
DEBUG=true
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Probar localmente
```bash
python app.py
```

Ve a `http://localhost:5000` para verificar que todo funciona.

## 🚀 Deployment en Vercel

### 1. Instalar Vercel CLI
```bash
npm i -g vercel
```

### 2. Login en Vercel
```bash
vercel login
```

### 3. Configurar variables de entorno
```bash
vercel env add PLEX_URL
vercel env add PLEX_TOKEN
vercel env add IMGUR_CLIENT_ID
```

### 4. Hacer deployment
```bash
vercel --prod
```

## 🔧 Configuración Avanzada

### Variables de entorno disponibles

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `PLEX_URL` | URL del servidor Plex | Requerido |
| `PLEX_TOKEN` | Token de autenticación | Requerido |
| `IMGUR_CLIENT_ID` | Client ID de Imgur | Requerido |
| `CACHE_DURATION` | Duración del cache en segundos | 60 |
| `IMAGE_WIDTH` | Ancho de la imagen | 400 |
| `IMAGE_HEIGHT` | Alto de la imagen | 150 |
| `DEFAULT_THEME` | Tema por defecto | default |
| `DEBUG` | Modo debug | false |
| `PORT` | Puerto para desarrollo local | 5000 |

### Temas disponibles
- `default` - Tema clásico con fondo oscuro
- `dark` - Tema GitHub dark
- `compact` - Versión más compacta
- `minimal` - Diseño minimalista claro

## 🐛 Resolución de Problemas

### Error: "No se pudo conectar a Plex"
- Verifica que `PLEX_URL` sea correcta
- Asegúrate de que el servidor Plex esté funcionando
- Verifica que el token sea válido

### Error: "Imgur no configurado"
- Verifica que `IMGUR_CLIENT_ID` esté configurado
- Las imágenes se servirán directamente si Imgur falla

### La imagen no se actualiza
- Usa `?refresh=true` para forzar actualización
- Verifica el valor de `CACHE_DURATION`
- Ve a `/api/cache/clear` para limpiar cache

### Problemas de fuentes en la imagen
- En algunos sistemas puede fallar la carga de fuentes
- El sistema automáticamente usa fuentes por defecto como fallback

## 🔒 Seguridad

- **Nunca** pongas credenciales en repositorios públicos
- Usa variables de entorno para toda información sensible
- El token de Plex da acceso completo a tu servidor
- Considera usar un usuario dedicado con permisos limitados

## 📱 Uso en GitHub

Una vez desplegado, añade esto a tu `README.md` del perfil:

```markdown
![Plex2Sign](https://tu-deployment.vercel.app/api/now-playing)
```

### Con parámetros personalizados:
```markdown
![Plex2Sign](https://tu-deployment.vercel.app/api/now-playing?theme=dark&width=500)
```
