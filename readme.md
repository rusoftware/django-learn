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
- `/send-messages/?group=ID` → ejecución de una campaña
- `/admin/` → panel de administración

---

## 📬 Envíos de prueba
- `/test-send/` → envía un texto de prueba
- `/test-send-media/` → envía una imagen pública de prueba

---

## ✅ Estado actual
- Proyecto funcional con campañas dinámicas, historial de mensajes y soporte para envíos multimedia.
- Listo para extender con reporting, programación de campañas o autenticación.