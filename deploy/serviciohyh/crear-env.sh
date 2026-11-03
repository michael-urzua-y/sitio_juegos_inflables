#!/bin/sh
# Crea el .env del sitio para este servidor con claves aleatorias.
# No sobrescribe un .env existente. Uso (desde la raíz del repo):
#   sh deploy/serviciohyh/crear-env.sh [dominio]      # por defecto inflables.serviciohyh.cl
set -eu

DOMAIN="${1:-inflables.serviciohyh.cl}"
cd "$(dirname "$0")/../.."

secret() { openssl rand -base64 48 | tr -d '/+=\n' | cut -c1-"$1"; }

if [ -e .env ]; then
  echo "Ya existe .env: no se toca nada. Bórralo a mano si quieres regenerarlo." >&2
  exit 1
fi

umask 077 # solo el dueño puede leer los secretos

DB_PASSWORD="$(secret 40)"
ADMIN_PASSWORD="$(secret 14)"
SUPERADMIN_PASSWORD="$(secret 16)"

cat > .env <<EOF
APP_ENV=production
SECRET_KEY=$(secret 64)

# Dueño del negocio y equipo de desarrollo (se crean solo la primera vez)
ADMIN_USER=admin
ADMIN_PASSWORD=$ADMIN_PASSWORD
SUPERADMIN_USER=superadmin
SUPERADMIN_PASSWORD=$SUPERADMIN_PASSWORD

# Cloudflare → hyh-nginx → este contenedor, siempre por HTTPS
COOKIE_SECURE=1
TRUST_PROXY=1
SESION_ATADA_IP=1

POSTGRES_USER=inflables
POSTGRES_PASSWORD=$DB_PASSWORD
POSTGRES_DB=inflables
DATABASE_URL=postgresql://inflables:$DB_PASSWORD@inflables-db:5432/inflables

SITIO_URL=https://$DOMAIN
CREDITOS_URL=#
PORT=8000
# 2 procesos en vez de 3: el VPS es compartido
WEB_CONCURRENCY=2

GOOGLE_VERIFICACION=
BING_VERIFICACION=
FACEBOOK_VERIFICACION=
EOF

echo "Archivo .env creado para https://$DOMAIN (solo su dueño puede leerlo)."
echo
echo "  Admin (dueño)     → usuario: admin      · clave: $ADMIN_PASSWORD"
echo "  Super admin (tú)  → usuario: superadmin · clave: $SUPERADMIN_PASSWORD"
echo "  Guárdalas ahora: no se vuelven a mostrar (quedan en .env)."
