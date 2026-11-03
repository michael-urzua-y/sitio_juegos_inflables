# Entretenciones Santos — Sitio web

Sitio web de **Entretenciones Santos SpA** para el arriendo de juegos inflables. Tiene catálogo por categorías, cotizador que envía el detalle por WhatsApp y un panel de administración para editar todo el contenido sin tocar código.

> Desarrollado por **Monay Solutions**.

---

## Funcionalidades

**Sitio público**
- Portada con hero, cinta animada de categorías, beneficios, los juegos más pedidos, pasos y preguntas frecuentes.
- **Catálogo paginado** (`/catalogo`, 12 por página) con filtro por categoría y buscador que ignora tildes. Escala a cientos de juegos.
- Menú con desplegable de categorías, página por categoría y página de detalle por juego.
- **Cotizador**: el cliente agrega juegos, ajusta cantidades, completa fecha, comuna y horario, y envía todo armado por **WhatsApp**.
- Botón flotante de WhatsApp, footer con Instagram y Facebook.
- Diseño responsive (móvil, tablet y escritorio), accesible y con animaciones que respetan `prefers-reduced-motion`.
- **SEO completo** para Google, IAs y redes sociales (ver la sección [SEO](#seo-google-ias-y-redes-sociales)).

**Panel admin (`/admin`)**: dos roles, mismo login.

| Sección | Admin (dueño) | Super admin (desarrollo) |
|---|:---:|:---:|
| **Juegos**: crear, editar, ocultar, eliminar, destacar, ordenar, fotos. Paginado (10) y con buscador. Desde el select de categoría se puede **crear una nueva o quitar la seleccionada** (si no tiene juegos). | ✅ | ✅ |
| **Contacto y redes**: WhatsApp, teléfono, email, zona, horario, Instagram, Facebook | ✅ | ✅ |
| **Mi contraseña** | ✅ | ✅ |
| **Contenido portada**: cifras, beneficios, pasos, preguntas frecuentes | — | ✅ |
| **Textos del sitio**: nombre, razón social, slogan, título y subtítulo de portada | — | ✅ |
| **Categorías**: ordenar con flechas, cambiar ícono y descripción | — | ✅ |
| **Usuarios**: restablecer la contraseña del admin y desbloquearlo | — | ✅ |

Las secciones del super admin están protegidas en el servidor (no solo ocultas en el menú). Ambos usuarios se crean la primera vez con `ADMIN_USER/ADMIN_PASSWORD` y `SUPERADMIN_USER/SUPERADMIN_PASSWORD` del `.env`.

Nada del contenido está escrito en el código: todo vive en la base de datos. `app/seed/data.py` solo carga los datos de ejemplo la primera vez.

---

## Inicio rápido con Docker (recomendado)

Requisitos: Docker y Docker Compose.

```bash
cp .env.example .env
# Edita .env y completa al menos: SECRET_KEY, ADMIN_PASSWORD y POSTGRES_PASSWORD
python3 -c "import secrets; print(secrets.token_hex(32))"   # genera un SECRET_KEY

docker compose up -d --build
```

- Sitio: http://localhost:8000
- Admin: http://localhost:8000/admin (usuario y clave definidos en `.env`)

Comandos útiles:

```bash
docker compose logs -f web          # ver logs
docker compose down                 # detener (los datos se conservan)
docker compose up -d --build        # aplicar cambios de código
docker compose exec web flask --app wsgi recargar-catalogo   # reemplaza categorías y juegos por los de ejemplo (¡borra los actuales!)
```

Los datos quedan en dos volúmenes: `pgdata` (base de datos PostgreSQL) y `uploads` (fotos).

### Respaldo

```bash
docker compose exec db pg_dump -U inflables inflables > respaldo.sql
docker run --rm -v sitio_juegos_inflables_uploads:/data -v "$PWD":/backup alpine tar czf /backup/fotos.tgz -C /data .
```

---

## Desarrollo local (sin Docker)

Requiere Python 3.9 o superior. Sin `DATABASE_URL` se usa SQLite en `instance/sitio.db`.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python wsgi.py               # http://localhost:8000 (modo debug)
```

Usuarios iniciales en desarrollo: `admin` / `admin123` y `superadmin` / `superadmin123`. Cámbialos en `/admin/password`.

---

## Estructura del proyecto

```
.
├── app/
│   ├── __init__.py            # create_app(): arma la aplicación (app factory)
│   ├── config.py              # configuración (solo infraestructura, vía variables de entorno)
│   ├── extensions.py          # db, login, CSRF, compresión
│   ├── security.py            # headers de seguridad, CSP, validaciones de producción
│   ├── seo_config.py          # SEO interno: título, palabras clave, descripción, ciudad
│   ├── marca.py               # identidad: archivos del logo y color de tema
│   ├── models/                # un archivo por modelo
│   │   ├── juego.py  categoria.py  bloque.py  ajuste.py  usuario.py
│   ├── services/              # lógica de consulta reutilizable
│   │   ├── catalogo.py        # juegos y categorías
│   │   ├── contenido.py       # bloques de portada
│   │   ├── ajustes.py         # textos/contacto editables
│   │   ├── seo.py             # datos estructurados Schema.org (JSON-LD)
│   │   └── tarjetas.py        # tarjetas 1200x630 para compartir en redes
│   ├── blueprints/
│   │   ├── public/            # sitio público
│   │   └── admin/             # panel: auth, juegos, categorias, contenido, ajustes
│   ├── utils/                 # helpers: imágenes, texto, formularios, plantillas, db
│   ├── seed/                  # datos iniciales (solo la primera vez)
│   ├── templates/
│   │   ├── macros/            # componentes Jinja reutilizables (ui.html, forms.html)
│   │   ├── partials/          # head, iconos, tarjeta de juego
│   │   ├── public/            # páginas públicas + partials (header, footer, cotizador)
│   │   └── admin/             # páginas del panel
│   └── static/
│       ├── css/  core.css (compartido) · site.css · admin.css
│       ├── js/   app.js (sitio) · admin.js (panel)
│       ├── fonts/ Fredoka y Plus Jakarta Sans (licencia OFL, para las tarjetas)
│       └── img/  logo-128/320.webp · favicon · íconos PWA · og-default.jpg · placeholders/
├── marca/logo-original.png    # logo fuente (no se publica; de aquí salen todos los íconos)
├── scripts/generar_marca.py   # genera logo, favicon, íconos y tarjeta de redes desde el logo
├── wsgi.py                    # punto de entrada (gunicorn wsgi:app)
├── Dockerfile
├── docker-compose.yml         # web + PostgreSQL
└── .env.example
```

### Cómo extender

- **Nueva página pública**: agrega una ruta en `app/blueprints/public/routes.py` y una plantilla que extienda `public/base.html`.
- **Nueva sección del admin**: crea un módulo en `app/blueprints/admin/` e impórtalo en su `__init__.py`. Ya queda protegida por login, porque la verificación se aplica a todo el blueprint.
- **Nuevo tipo de contenido de portada**: agrégalo en `TIPOS` (`app/models/bloque.py`) y úsalo en la plantilla con `bloques.<tipo>`.
- **Ajustar SEO**: edita `app/seo_config.py` (interno, no visible en el admin).
- **Nuevo texto editable**: agrega la clave en `GRUPOS` (`app/services/ajustes.py`) y su valor inicial en `AJUSTES` (`app/seed/data.py`). Se crea solo al reiniciar.
- **Componentes de UI**: reutiliza los macros de `templates/macros/ui.html` (`icon`, `wa_button`, `add_button`, `img_juego`, `section_head`, `grid`…) y `forms.html` (`field`, `select`, `check`, `csrf`, `post_button`).

---

## Imágenes

- Sube las fotos desde el admin (JPG, PNG o WebP, máx. 10 MB).
- Cada foto se convierte automáticamente a **AVIF** (el formato más liviano) y a **WebP** como respaldo, en 3 tamaños (480, 960 y 1400 px). El navegador descarga solo la versión que necesita.
- Se corrige la orientación de fotos de celular y se eliminan los metadatos (GPS/EXIF).
- Los juegos sin foto muestran una ilustración referencial de su categoría.
- Recomendado: fotos horizontales 4:3, bien iluminadas.

---

## SEO: Google, IAs y redes sociales

**Qué incluye el sitio**

| Para | Qué se hizo |
|---|---|
| Google / Bing | Títulos con palabras clave ("Arriendo de {categoría} en {ciudad}"), meta descripción, URL canónica, `sitemap.xml` con fechas e imágenes, `robots.txt`, búsquedas internas con `noindex`, sitio rápido (AVIF, compresión, caché). |
| Resultados enriquecidos | Datos estructurados Schema.org: **LocalBusiness** (nombre, teléfono, zona, redes), **Product + Offer** por juego (precio en CLP), **FAQPage**, **BreadcrumbList**, **ItemList** y cuadro de búsqueda del sitio. |
| IAs (ChatGPT, Claude, Gemini, Perplexity) | `robots.txt` permite explícitamente a sus rastreadores (GPTBot, OAI-SearchBot, ClaudeBot, Google-Extended, PerplexityBot…). `/llms.txt` resume el negocio, los servicios, los juegos con precios y las FAQ en un formato pensado para IAs. |
| WhatsApp, Facebook, Instagram, X, LinkedIn | Open Graph y Twitter Cards. **Cada juego y cada categoría tiene su propia tarjeta de marca** (1200×630, ~80 KB) con logo, nombre, precio y foto, generada automáticamente. Se regenera sola si cambias el precio, el nombre o la foto. |

**El SEO es configuración interna** (no lo edita el cliente desde el admin):
- Título, palabras clave (juegos inflables, juegos acuáticos, juegos mecanizados, toro mecánico…), descripción, ciudad y región: [`app/seo_config.py`](app/seo_config.py). Después de editarlo, ejecuta `docker compose up -d --build`.
- Códigos de verificación de Google, Bing y Meta: variables `GOOGLE_VERIFICACION`, `BING_VERIFICACION` y `FACEBOOK_VERIFICACION` en `.env`.

**Pasos después de publicar (con el dominio real y HTTPS)**

1. Define `SITIO_URL=https://tudominio.cl` en `.env` (las tarjetas y el sitemap usan esta URL).
2. **Google Search Console** (https://search.google.com/search-console): agrega el dominio, copia el código de la etiqueta HTML en `GOOGLE_VERIFICACION` del `.env`, reinicia y envía `https://tudominio.cl/sitemap.xml`.
3. **Bing Webmaster Tools** (https://www.bing.com/webmasters): lo mismo, con `BING_VERIFICACION`. Bing también alimenta a ChatGPT y Copilot.
4. **Perfil de Empresa en Google** (https://business.google.com): es lo que más ayuda a aparecer en Google Maps y en búsquedas como "juegos inflables cerca de mí". Usa el mismo nombre, teléfono y la URL del sitio.
5. Pon el link del sitio en la biografía de Instagram, Facebook y WhatsApp Business.
6. Revisa cómo se ven las tarjetas: https://developers.facebook.com/tools/debug/ (botón "Volver a extraer" si cambiaste algo) y https://cards-dev.twitter.com/validator. Valida los datos estructurados en https://search.google.com/test/rich-results.
7. Con fotos reales y descripciones propias de cada juego, el posicionamiento mejora mucho.

---

## Seguridad

| Riesgo | Medida |
|---|---|
| Inyección SQL | Todas las consultas usan el ORM de SQLAlchemy (parametrizadas). |
| XSS | Autoescape de Jinja, CSP estricta sin scripts inline, el carrito arma el DOM con `textContent` y las URLs de redes solo aceptan `http(s)://`. |
| CSRF | Token CSRF en todos los formularios y acciones POST (Flask-WTF). |
| Roles | Admin y super admin; las secciones restringidas se validan en el servidor (decorador `@solo_superadmin`). |
| Login | Hash scrypt/PBKDF2, bloqueo de 15 min tras 5 intentos fallidos por usuario y tras 10 por IP, mensajes genéricos, protección contra fijación de sesión y sesiones de 8 h. |
| Sesión única | Cada usuario tiene **una sola sesión activa**: al entrar desde otro equipo, la anterior se cierra con un aviso. El token es aleatorio y también cambia al cerrar sesión o cambiar la contraseña (invalida la cookie "recordarme"). |
| Sesión atada al equipo | La sesión solo vale desde la IP y el navegador donde se inició; una cookie robada no sirve desde otro equipo. No se confía en `X-Forwarded-For` salvo con `TRUST_PROXY=1`. Se desactiva con `SESION_ATADA_IP=0`. |
| Cookies | `HttpOnly`, `SameSite=Lax` y `Secure` con `COOKIE_SECURE=1`. |
| Clickjacking / sniffing | `X-Frame-Options: DENY`, `frame-ancestors 'none'`, `nosniff`, `Referrer-Policy`, `Permissions-Policy`, HSTS en HTTPS. |
| CORS | No hay API pública ni cabeceras CORS, así que el navegador bloquea las lecturas desde otros dominios por defecto. |
| Subida de archivos | Se valida el contenido real de la imagen (no solo la extensión), hay límite de tamaño y de píxeles, se re-codifica y el nombre es aleatorio. |
| Configuración | En producción (`APP_ENV=production`) la app **no arranca** con `SECRET_KEY` o `ADMIN_PASSWORD` débiles. |
| Contenedor | Corre con usuario sin privilegios y PostgreSQL no se expone fuera de la red de Docker. |

**Para publicar en internet**: usa HTTPS (Nginx, Traefik, Caddy o Cloudflare) y define `COOKIE_SECURE=1`, `TRUST_PROXY=1` y `SITIO_URL=https://tudominio.cl`.

---

## Variables de entorno

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave para firmar sesiones (mín. 32 caracteres aleatorios). |
| `ADMIN_USER` / `ADMIN_PASSWORD` | Admin inicial, dueño del negocio (se crea solo la primera vez). |
| `SUPERADMIN_USER` / `SUPERADMIN_PASSWORD` | Super admin inicial, equipo de desarrollo (se crea solo la primera vez). |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Credenciales de la base de datos. |
| `DATABASE_URL` | Opcional; docker-compose la arma automáticamente. |
| `COOKIE_SECURE` | `1` cuando el sitio use HTTPS. |
| `TRUST_PROXY` | `1` si hay un proxy inverso delante. |
| `SITIO_URL` | URL pública (para sitemap y Open Graph). |
| `CREDITOS_URL` | Enlace de "Sitio creado por Monay Solutions". |
| `SESION_ATADA_IP` | `1` (por defecto): la sesión del admin solo vale desde la IP y navegador donde se inició. `0` si la IP de quien administra cambia seguido. |
| `WEB_CONCURRENCY` | Número de workers de gunicorn (por defecto 3). |
| `GOOGLE_VERIFICACION` / `BING_VERIFICACION` / `FACEBOOK_VERIFICACION` | Códigos de verificación de propiedad (SEO). |

---

## Personalización rápida

- **Logo**: reemplaza `marca/logo-original.png` (cuadrado, ideal ≥1000 px, fondo negro o transparente) y ejecuta `python scripts/generar_marca.py`. Genera el logo con fondo transparente para header/footer/admin, `favicon.ico`, ícono de iPhone, íconos PWA (incluido *maskable*) y la tarjeta `og-default.jpg` para redes.
- **Colores**: la paleta sale del logo (azul rey, rojo, amarillo y naranja sobre noche de feria). Se edita en las variables al inicio de `app/static/css/core.css` (`--primary`, `--accent`, `--red`, `--gold`, `--night`…); el color de la barra del navegador está en `app/marca.py`. Si cambias el diseño de las tarjetas de redes, sube `VERSION` en `app/services/tarjetas.py`.
- **Destacar una palabra del título**: en *Textos y contacto*, enciérrala entre asteriscos: `Juegos que hacen tu evento *inolvidable*`.
