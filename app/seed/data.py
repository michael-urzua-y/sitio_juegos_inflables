"""
Datos iniciales. Se cargan en la base de datos SOLO la primera vez (o cuando
aparece una clave de ajuste nueva). Después todo se edita desde /admin.
"""

# Textos y datos de contacto (editables en /admin/ajustes)
AJUSTES = {
    "nombre": "Entretenciones Santos",
    "razon_social": "Entretenciones Santos SpA",
    "slogan": "Arriendo de juegos inflables para eventos",
    "hero_titulo": "Juegos inflables que hacen tu evento *inolvidable*",
    "hero_subtitulo": "Inflables, juegos mecánicos, de salón, típicos, de agua y mucho más. Despacho, "
                      "instalación y retiro incluidos. Arma tu cotización en segundos y recíbela por WhatsApp.",
    "whatsapp": "56912345678",
    "telefono": "+56 9 1234 5678",
    "email": "contacto@entretencionessantos.cl",
    "instagram": "https://instagram.com/",
    "facebook": "https://facebook.com/",
    "zona": "Santiago y alrededores",
    "horario": "Lunes a domingo, 9:00 a 21:00",
}

# Bloques de contenido de la portada (editables en /admin/contenido)
BLOQUES = [
    {"tipo": "stat", "titulo": "+500", "texto": "eventos realizados"},
    {"tipo": "stat", "titulo": "100%", "texto": "equipos sanitizados"},
    {"tipo": "stat", "titulo": "4.9★", "texto": "valoración clientes"},
    {"tipo": "beneficio", "icono": "truck", "titulo": "Despacho e instalación", "texto": "Llegamos, armamos y retiramos"},
    {"tipo": "beneficio", "icono": "shield", "titulo": "Seguridad garantizada", "texto": "Equipos certificados y anclados"},
    {"tipo": "beneficio", "icono": "clock", "titulo": "Puntualidad", "texto": "Llegamos antes de tu evento"},
    {"tipo": "beneficio", "icono": "sparkles", "titulo": "Limpieza total", "texto": "Sanitizados en cada arriendo"},
    {"tipo": "paso", "titulo": "Elige tus juegos", "texto": "Explora el catálogo y presiona «Cotizar» en los juegos que quieras para tu evento."},
    {"tipo": "paso", "titulo": "Completa los datos", "texto": "Abre «Mi cotización», ajusta cantidades e indica fecha, comuna y horario."},
    {"tipo": "paso", "titulo": "Envía por WhatsApp", "texto": "Te llega el detalle listo a nuestro WhatsApp y te respondemos con la confirmación."},
    {"tipo": "faq", "titulo": "¿El precio incluye instalación?", "texto": "Sí. Todos nuestros arriendos incluyen despacho, instalación y retiro dentro de nuestra zona de cobertura. Para comunas más lejanas puede aplicar un recargo."},
    {"tipo": "faq", "titulo": "¿Por cuántas horas es el arriendo?", "texto": "El arriendo estándar considera hasta 5 horas de uso. Si necesitas más tiempo, indícalo en tu cotización."},
    {"tipo": "faq", "titulo": "¿Qué necesito para instalar un inflable?", "texto": "Una superficie plana (pasto, cemento o baldosa) y un enchufe a menos de 20 metros. Nosotros llevamos todo lo demás."},
    {"tipo": "faq", "titulo": "¿Cómo reservo mi fecha?", "texto": "Envía tu cotización por WhatsApp. Confirmamos disponibilidad y reservas con un abono del 50%."},
    {"tipo": "faq", "titulo": "¿Qué pasa si llueve?", "texto": "Si el clima no permite el uso seguro de los juegos, reprogramamos tu evento sin costo."},
]

CATEGORIAS = [
    {"slug": "juegos-inflables", "nombre": "Inflables", "icono": "castle",
     "descripcion": "Castillos, toboganes, obstáculos y mucho más."},
    {"slug": "juegos-mecanicos", "nombre": "Mecánicos", "icono": "gear",
     "descripcion": "Toro mecánico, reloj derribador y desafíos."},
    {"slug": "juegos-interactivos", "nombre": "Interactivos", "icono": "target",
     "descripcion": "Juegos de habilidad, competencia y entretención."},
    {"slug": "zona-infantil", "nombre": "Zona Infantil", "icono": "smile",
     "descripcion": "Opciones pensadas especialmente para los más pequeños."},
    {"slug": "juegos-electronicos", "nombre": "Electrónicos", "icono": "gamepad",
     "descripcion": "Juegos electrónicos para grandes y chicos."},
    {"slug": "juegos-de-salon", "nombre": "Juegos de Salón", "icono": "ball8",
     "descripcion": "Pool, taca taca, ping pong, arcade y más."},
    {"slug": "juegos-tipicos", "nombre": "Juegos Típicos", "icono": "kite",
     "descripcion": "Tradición chilena para celebraciones y Fiestas Patrias."},
    {"slug": "juegos-de-agua", "nombre": "Juegos de Agua", "icono": "drop",
     "descripcion": "Diversión refrescante para disfrutar al máximo."},
]

# Juegos de ejemplo (valores referenciales). Se reemplazan desde /admin.
JUEGOS = [
    # --- Inflables ---
    {"slug": "castillo-princesas", "nombre": "Castillo Inflable Princesas", "categoria": "juegos-inflables",
     "precio": 45000, "medidas": "4 x 4 m", "edad": "2 a 8 años", "capacidad": "6 niños", "destacado": True,
     "descripcion": "Castillo con torres, colores pastel y amplia zona de salto. Ideal para cumpleaños infantiles."},
    {"slug": "castillo-superheroes", "nombre": "Castillo Inflable Superhéroes", "categoria": "juegos-inflables",
     "precio": 45000, "medidas": "4 x 4 m", "edad": "2 a 8 años", "capacidad": "6 niños", "destacado": False,
     "descripcion": "Saltarín temático con colores vibrantes para pequeños héroes llenos de energía."},
    {"slug": "tobogan-gigante-selva", "nombre": "Tobogán Inflable Gigante Selva", "categoria": "juegos-inflables",
     "precio": 90000, "medidas": "9 x 4 x 6 m", "edad": "5 a 15 años", "capacidad": "8 niños", "destacado": True,
     "descripcion": "Seis metros de altura con escalada y bajada rápida. Diseño selva con animales."},
    {"slug": "pista-obstaculos", "nombre": "Pista de Obstáculos Inflable", "categoria": "juegos-inflables",
     "precio": 95000, "medidas": "12 x 3 m", "edad": "5 años a adultos", "capacidad": "6 personas", "destacado": False,
     "descripcion": "Circuito de obstáculos para competir en parejas. Ideal para colegios y empresas."},

    # --- Mecánicos ---
    {"slug": "toro-mecanico", "nombre": "Toro Mecánico", "categoria": "juegos-mecanicos",
     "precio": 110000, "medidas": "5 x 5 m", "edad": "6 años a adultos", "capacidad": "1 persona", "destacado": True,
     "descripcion": "El clásico desafío con velocidades regulables y colchón inflable de seguridad. Incluye operador."},
    {"slug": "reloj-derribador", "nombre": "Reloj Derribador", "categoria": "juegos-mecanicos",
     "precio": 120000, "medidas": "Ø 7 m", "edad": "8 años a adultos", "capacidad": "6 personas", "destacado": True,
     "descripcion": "Brazos giratorios que hay que saltar o esquivar. El último en pie gana. Incluye operador."},
    {"slug": "surf-mecanico", "nombre": "Surf Mecánico", "categoria": "juegos-mecanicos",
     "precio": 115000, "medidas": "5 x 5 m", "edad": "8 años a adultos", "capacidad": "1 persona", "destacado": False,
     "descripcion": "Simulador de tabla de surf con movimiento real sobre colchón inflable. Incluye operador."},

    # --- Interactivos ---
    {"slug": "futbolito-humano", "nombre": "Futbolito Humano", "categoria": "juegos-interactivos",
     "precio": 100000, "medidas": "12 x 6 m", "edad": "8 años a adultos", "capacidad": "10 personas", "destacado": True,
     "descripcion": "Cancha inflable donde los jugadores son las figuras del taca taca. Risas aseguradas."},
    {"slug": "muro-reaccion", "nombre": "Muro de Reacción", "categoria": "juegos-interactivos",
     "precio": 85000, "medidas": "2 x 2 m", "edad": "6 años a adultos", "capacidad": "2 personas", "destacado": False,
     "descripcion": "Botones luminosos que hay que apagar lo más rápido posible. Compite por el mejor tiempo."},
    {"slug": "tiro-al-arco-inflable", "nombre": "Tiro al Arco Inflable", "categoria": "juegos-interactivos",
     "precio": 60000, "medidas": "5 x 3 m", "edad": "5 años a adultos", "capacidad": "2 personas", "destacado": False,
     "descripcion": "Arco con portero inflable y marcador. Perfecto para torneos de penales."},

    # --- Zona Infantil ---
    {"slug": "piscina-pelotas", "nombre": "Piscina de Pelotas", "categoria": "zona-infantil",
     "precio": 35000, "medidas": "3 x 3 m", "edad": "1 a 5 años", "capacidad": "6 niños", "destacado": False,
     "descripcion": "Piscina acolchada con pelotas de colores sanitizadas. Segura para los más pequeños."},
    {"slug": "mini-saltarin-baby", "nombre": "Mini Saltarín Baby", "categoria": "zona-infantil",
     "precio": 35000, "medidas": "3 x 3 m", "edad": "1 a 4 años", "capacidad": "4 niños", "destacado": False,
     "descripcion": "Paredes bajas, entrada fácil y máxima seguridad para guaguas y niños pequeños."},
    {"slug": "set-mesas-sillas", "nombre": "Set Mesas y Sillas Infantiles", "categoria": "zona-infantil",
     "precio": 25000, "medidas": "4 mesas + 24 sillas", "edad": "Infantil", "capacidad": "24 niños", "destacado": False,
     "descripcion": "Mobiliario infantil colorido para la hora de la torta y la once."},

    # --- Electrónicos ---
    {"slug": "simulador-carreras", "nombre": "Simulador de Carreras", "categoria": "juegos-electronicos",
     "precio": 90000, "medidas": "2 x 1,5 m", "edad": "7 años a adultos", "capacidad": "2 personas", "destacado": True,
     "descripcion": "Dos asientos con volante y pedales para competir en carreras en pantalla grande."},
    {"slug": "maquina-de-baile", "nombre": "Máquina de Baile", "categoria": "juegos-electronicos",
     "precio": 80000, "medidas": "2 x 2 m", "edad": "6 años a adultos", "capacidad": "2 personas", "destacado": False,
     "descripcion": "Pista con flechas luminosas para bailar al ritmo de la música. Ideal para fiestas."},
    {"slug": "estacion-gamer", "nombre": "Estación Gamer", "categoria": "juegos-electronicos",
     "precio": 70000, "medidas": "Pantalla 65\"", "edad": "6 años a adultos", "capacidad": "4 personas", "destacado": False,
     "descripcion": "Consola de última generación con pantalla gigante y juegos multijugador."},

    # --- Juegos de Salón ---
    {"slug": "mesa-de-pool", "nombre": "Mesa de Pool", "categoria": "juegos-de-salon",
     "precio": 50000, "medidas": "2,1 x 1,2 m", "edad": "10 años a adultos", "capacidad": "4 personas", "destacado": False,
     "descripcion": "Mesa profesional con tacos, bolas y triángulo. Infaltable en eventos de empresa."},
    {"slug": "taca-taca", "nombre": "Taca Taca", "categoria": "juegos-de-salon",
     "precio": 35000, "medidas": "1,4 x 0,8 m", "edad": "6 años a adultos", "capacidad": "4 personas", "destacado": True,
     "descripcion": "El clásico taca taca de madera para competir en parejas."},
    {"slug": "mesa-ping-pong", "nombre": "Mesa de Ping Pong", "categoria": "juegos-de-salon",
     "precio": 35000, "medidas": "2,7 x 1,5 m", "edad": "7 años a adultos", "capacidad": "4 personas", "destacado": False,
     "descripcion": "Mesa plegable con paletas y pelotas incluidas."},
    {"slug": "arcade-retro", "nombre": "Arcade Retro Multijuegos", "categoria": "juegos-de-salon",
     "precio": 45000, "medidas": "0,7 x 0,8 m", "edad": "6 años a adultos", "capacidad": "2 personas", "destacado": False,
     "descripcion": "Máquina arcade con cientos de juegos clásicos para dos jugadores."},

    # --- Juegos Típicos ---
    {"slug": "rayuela", "nombre": "Rayuela", "categoria": "juegos-tipicos",
     "precio": 25000, "medidas": "Cancha 6 m", "edad": "8 años a adultos", "capacidad": "4 personas", "destacado": False,
     "descripcion": "El juego típico chileno con tejos y lienza. Perfecto para Fiestas Patrias."},
    {"slug": "juego-del-sapo", "nombre": "Juego del Sapo", "categoria": "juegos-tipicos",
     "precio": 25000, "medidas": "0,6 x 0,6 m", "edad": "6 años a adultos", "capacidad": "4 personas", "destacado": False,
     "descripcion": "Lanza las fichas a la boca del sapo y suma puntos. Tradición de fondas y ramadas."},
    {"slug": "kit-juegos-criollos", "nombre": "Kit Juegos Criollos", "categoria": "juegos-tipicos",
     "precio": 40000, "medidas": "Kit completo", "edad": "Todo público", "capacidad": "20 personas", "destacado": False,
     "descripcion": "Carrera de sacos, emboque, trompo y cuerda para tirar. Celebra el 18 a lo grande."},

    # --- Juegos de Agua ---
    {"slug": "tobogan-acuatico-tropical", "nombre": "Tobogán Acuático Tropical", "categoria": "juegos-de-agua",
     "precio": 85000, "medidas": "8 x 4 x 5 m", "edad": "5 a 14 años", "capacidad": "8 niños", "destacado": True,
     "descripcion": "Tobogán con piscina de llegada y temática tropical. El favorito del verano."},
    {"slug": "piscina-splash", "nombre": "Piscina Splash", "categoria": "juegos-de-agua",
     "precio": 55000, "medidas": "5 x 4 m", "edad": "3 a 10 años", "capacidad": "6 niños", "destacado": False,
     "descripcion": "Piscina inflable con rociadores y obstáculos para refrescarse jugando."},
    {"slug": "doble-carril-agua", "nombre": "Doble Carril de Agua", "categoria": "juegos-de-agua",
     "precio": 95000, "medidas": "10 x 4 x 5 m", "edad": "6 a 16 años", "capacidad": "10 niños", "destacado": False,
     "descripcion": "Dos carriles para competir quién llega primero a la piscina."},
]
