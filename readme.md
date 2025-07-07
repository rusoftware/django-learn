# ✅ ¿Qué necesitás versionar en Git?


**Subí:**
```
django_project/
├── app/                    ✅ Tu código Django
├── Dockerfile              ✅
├── docker-compose.yml      ✅
├── requirements.txt        ✅
```

**No subas:**
```
bash
Copy
Edit
__pycache__/
*.pyc
env/ o venv/
mariadb_data/ (volúmenes de datos)
``` 

**Agregalo a .gitignore:**
.gitignore
```
__pycache__/
*.pyc
venv/
env/
mariadb_data/
core/migrations/__pycache__/
```

---

# ✅ Cómo levantarlo en otra máquina
Cloná el repo:
```
git clone <tu-repo>
cd django_project
```

Construí y levantá todo:
```
docker-compose up -d --build
``` 

Migrá y creá superusuario:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

Listo. Tenés el entorno 100% funcional en otra máquina.