# Entretenciones Santos en el VPS de serviciohyh.cl (inflables.serviciohyh.cl)

Instancia de **prueba** en el VPS donde corre el sitio `taller` (serviciohyh.cl), para ver cómo se ve antes de
pasarlo a su propio dominio. Se monta sin tocar ese sitio: solo usa su carpeta (`/opt/inflables`), un archivo
propio en el nginx existente (`inflables.conf`) y un registro DNS. Responde con `X-Robots-Tag: noindex` para que
Google no lo indexe en este subdominio.

| Pieza              | Dónde                                                       |
| ------------------ | ----------------------------------------------------------- |
| Código y `.env`    | `/opt/inflables`                                            |
| Contenedores       | `inflables-db`, `inflables-web`                             |
| Entrada web        | `/opt/taller/nginx/conf.d/inflables.conf` → `inflables-web` |
| Memoria aproximada | ~200 MB                                                     |

## 1. DNS en Cloudflare

Registro `A` · nombre `inflables` · IPv4 `198.89.96.183` · proxy activado (nube naranja). El certificado de
origen actual ya cubre `*.serviciohyh.cl`.

## 2. Instalar (en el VPS)

```bash
git clone https://github.com/michael-urzua-y/sitio_juegos_inflables.git /opt/inflables
cd /opt/inflables

sh deploy/serviciohyh/crear-env.sh                # crea .env con claves aleatorias (las muestra una vez)
docker compose -f deploy/serviciohyh/docker-compose.yml up -d --build
docker compose -f deploy/serviciohyh/docker-compose.yml ps        # ambos "healthy"
```

## 3. Conectar al nginx existente (sin cortar el servicio)

```bash
cp /opt/inflables/deploy/serviciohyh/inflables.conf /opt/taller/nginx/conf.d/
docker exec hyh-nginx nginx -t && docker exec hyh-nginx nginx -s reload
```

Si `nginx -t` falla, no se recarga nada y el sitio sigue igual.

## Operación

```bash
cd /opt/inflables
git pull && docker compose -f deploy/serviciohyh/docker-compose.yml up -d --build   # actualizar
docker compose -f deploy/serviciohyh/docker-compose.yml stop                        # apagar (conserva datos)
docker compose -f deploy/serviciohyh/docker-compose.yml up -d                       # encender
```

Al apagarlo, desactiva también su entrada en nginx para que el subdominio no responda 502:

```bash
mv /opt/taller/nginx/conf.d/inflables.conf /opt/taller/nginx/conf.d/inflables.conf.off
docker exec hyh-nginx nginx -t && docker exec hyh-nginx nginx -s reload
```

Para quitarlo por completo: `docker compose -f deploy/serviciohyh/docker-compose.yml down -v` (borra la base y
las fotos), borra `inflables.conf` de `conf.d`, recarga nginx y elimina el registro DNS en Cloudflare.
