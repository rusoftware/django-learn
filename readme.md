# 📦 Proyecto Django + EvolutionAPI

Sistema para gestionar campañas de envío de mensajes (texto, imagen, video, PDF) vía WhatsApp usando EvolutionAPI.

Incluye:
- Carga de contactos (manual o CSV)
- Agrupación por grupos (`ContactGroup`)
- Gestión de instancias de envío (`Instance`)
- Creación de campañas (`MessageCampaign`)
- Envío masivo con rotación de instancias activas
- Registro de historial (`MessageHistory`)

---


## 🚀 Cómo levantar el entorno

### Cloná el repo:

```bash
git clone <tu-repo>
cd django_project
````

### Construí y levantá todo:
````
docker-compose up -d --build
````

### Aplicá migraciones y creá superusuario:
````
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
````


---

# ✅ ¿Qué necesitás versionar en Git?


**:arrow_up: Subí:**
````
django_project/
├── core/                  ✅ Código de la app Django
├── Dockerfile             ✅ Imagen personalizada
├── docker-compose.yml     ✅ Servicios: web y db
├── requirements.txt       ✅ Dependencias
├── core/migrations/*.py   ✅ Migraciones versionadas
├── media/ (vacío o solo structure) ⚠️ Solo si querés versionar estructura
````

**🚫 Agregá esto a .gitignore:**
````
__pycache__/
*.pyc
venv/
env/
mariadb_data/
media/  # ⚠️ solo si no versionás imágenes subidas
core/migrations/__pycache__/
````

---

## 📁 Carpeta de archivos multimedia
- Imágenes subidas se guardan en: media/campaign_images/
- media_url se genera automáticamente si se sube un archivo
- Asegurate de servir /media/ si desplegás en producción
---

## 🧠 Consideraciones importantes
- El modelo MessageCampaign reemplaza a MessageSend
- El campo send fue renombrado a campaign en MessageHistory
- Las migraciones correspondientes están versionadas
- Se usa mimetypes para detección de tipo de archivo
- Compatible con EvolutionAPI para envíos de texto y media

---

## 📍 Rutas útiles
- `/contacts/` → gestión de contactos
- `/instances/` → gestión de instancias
- `/send-messages/?group=ID&campaign=ID` → ejecución de una campaña determinada para un grupo definido
- `/admin/` → panel de administración

---

## 📡 Integración con EvolutionAPI

Este proyecto se conecta con [EvolutionAPI](https://evolutionapi.com) para enviar mensajes de WhatsApp, tanto de texto como multimedia.

### ✉️ Endpoints utilizados

#### 1. Enviar mensaje de texto

**POST** `{api_url}/message/sendText/{instance_name}`

**Headers:**
````json
headers = {
  "Content-Type": "application/json",
  "apikey": "<api_key>"
}
````

**Body:**
````json
payload = {
  "number": contact.phone,
  "text": message_text
}
````

#### 2. Enviar mensaje con media (imagen, video, audio, documento)
**POST** `{api_url}/message/sendMedia/{instance_name}`

**Headers:**
````json
headers = {
  "Content-Type": "application/json",
  "apikey": "<api_key>"
}
````

**Body:**
````json
payload = {
  "number": "5493412345678",
  "mediatype": "image",           // image | video | audio | document
  "mimetype": "image/jpeg",       // Detectado automáticamente
  "caption": "Texto opcional (se usa el mensaje como caption)",
  "media": "https://tuservidor.com/media/archivo.jpg",
  "fileName": "archivo.jpg"
}
````

### ⚙️ Detalles técnicos
- `instance_name`: identificador configurado en EvolutionAPI por cada conexión/número.
- `apikey`: clave privada para autenticar la petición (por instancia).
- `media`: debe ser una URL accesible públicamente; se construye desde media_file o manualmente con media_url.
- `fileName`: requerido para medios (se deriva automáticamente si no se define).
- `mimetype` y `mediatype` se calculan con `mimetypes.guess_type()`.


### 🧾 Tipos de archivo soportados
- Texto plano
- Imagen: image/jpeg, image/png, image/webp
- Video: video/mp4
- Audio: audio/mpeg
- Documento: application/pdf, etc.
---

## ✅ Estado actual
- Proyecto funcional con campañas dinámicas, historial de mensajes y soporte para envíos multimedia.
- Listo para extender con reporting, programación de campañas o autenticación.