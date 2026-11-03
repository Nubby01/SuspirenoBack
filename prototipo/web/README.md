# Suspiro Sureño (Django)

Pastelería por encargo en Punta Arenas: catálogo público, cotización por WhatsApp y panel interno.

## Derechos de uso

Código académico con **todos los derechos reservados** ([`LICENSE`](../../LICENSE)).

Permitido: evaluarlo y demostrarlo. No permitido sin permiso: plagiarlo, venderlo, redistribuirlo como propio ni usarlo con fines ilícitos. Las claves de abajo son solo de prueba.

## Cómo correrlo

```bash
cd prototipo/web
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py poblar
python manage.py runserver
```

Abrir http://127.0.0.1:8000/

| Usuario | Clave | Rol |
| --- | --- | --- |
| `admin` | `CambiarEstaClave2026` (o `SEED_PASSWORD` del `.env`) | Administradora |
| `ayudante` | `Ayudante2026` | Ayudante |

Copiar `.env.example` a `.env` antes de publicar.

## Subir a GitHub

Desde la carpeta `ProyectoIntegrado2`:

```bash
git init
git add .
git commit -m "Suspiro Sureño: prototipo Django listo para publicar"
```

Crea un repo vacío en GitHub y luego:

```bash
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

## Publicar (recomendado: Render)

La app es Django con panel, sesiones y fotos. **Render** es lo más estable para esto (ya hay `render.yaml`).

1. En [render.com](https://render.com): New → Web Service → conecta el repo de GitHub.
2. Root Directory: `prototipo/web`
3. Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
4. Start: `python manage.py migrate && python manage.py poblar && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
5. Variables: `DEBUG=False`, `SECRET_KEY` (generada), `ALLOWED_HOSTS=.onrender.com`, `DATABASE_URL` (Postgres de Render o Neon), `WHATSAPP_NUMERO`, `SEED_PASSWORD`, `MEDIA_ROOT=/var/media`
6. Disco persistente montado en `/var/media` si van a subir fotos.

## Publicar en Vercel (alternativa)

Vercel también puede servir Django, pero el disco de fotos no es persistente como en Render. Si el profesor pide Vercel:

1. En [vercel.com](https://vercel.com): Add New Project → importa el repo.
2. Root Directory: `prototipo/web`
3. Framework: Other / Django (detecta `manage.py`).
4. Variables de entorno (Production):
   - `DEBUG=False`
   - `SECRET_KEY` (cadena larga al azar)
   - `ALLOWED_HOSTS=.vercel.app`
   - `CSRF_TRUSTED_ORIGINS=https://TU-PROYECTO.vercel.app`
   - `DATABASE_URL` (Postgres en Neon u otro; no uses SQLite en la nube)
   - `WHATSAPP_NUMERO`, `SEED_PASSWORD`, `AYUDANTE_PASSWORD`
5. Deploy. La URL queda tipo `https://….vercel.app`.
