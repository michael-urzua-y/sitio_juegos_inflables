import re
import unicodedata


def slugify(texto):
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-") or "item"


def slug_unico(modelo, texto, excluir_id=None):
    """Genera un slug que no exista en la tabla del modelo."""
    base = slugify(texto)
    slug, n = base, 2
    while True:
        q = modelo.query.filter_by(slug=slug)
        if excluir_id:
            q = q.filter(modelo.id != excluir_id)
        if not q.first():
            return slug
        slug, n = f"{base}-{n}", n + 1


def a_entero(valor, defecto=0):
    """'45.000' / '$45000' / 45000 -> 45000"""
    try:
        return int(re.sub(r"[^\d-]", "", str(valor)))
    except (TypeError, ValueError):
        return defecto


def solo_digitos(valor):
    return re.sub(r"\D", "", valor or "")


def formato_clp(valor):
    return "$" + f"{int(valor or 0):,}".replace(",", ".")


def recortar(valor, maximo):
    """Limpia espacios y limita el largo (evita errores de BD y payloads gigantes)."""
    return (valor or "").strip()[:maximo]


def url_segura(valor):
    """Solo acepta http(s). Bloquea 'javascript:' y otros esquemas peligrosos en href."""
    valor = (valor or "").strip()
    return valor if re.match(r"^https?://[^\s<>\"']+$", valor, re.I) else ""


def email_valido(valor):
    valor = (valor or "").strip()
    return valor if re.match(r"^[^@\s<>\"']+@[^@\s<>\"']+\.[a-z]{2,}$", valor, re.I) else ""


def resaltar(texto):
    """Escapa el texto y convierte *palabras* en <span class="hl"> (texto con degradado)."""
    from markupsafe import Markup, escape
    return Markup(re.sub(r"\*([^*]{1,80})\*", r'<span class="hl">\1</span>', str(escape(texto or ""))))
