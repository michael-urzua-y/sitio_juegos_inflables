"""
SEO para buscadores, IAs y redes sociales.

Genera datos estructurados Schema.org (JSON-LD), que Google, Bing, ChatGPT,
Perplexity, Gemini, etc. usan para entender el negocio, sus productos y precios.
"""
from flask import url_for

from app.services.ajustes import obtener as ajustes


def _abs(path):
    """URL absoluta (las redes sociales y Schema.org requieren URLs completas)."""
    if path.startswith("http"):
        return path
    return ajustes()["url"] + path


def descripcion_negocio():
    n = ajustes()
    return n["seo_descripcion"] or f"{n['slogan']} en {n['zona']}."


def palabras_clave():
    return [p.strip() for p in (ajustes()["seo_palabras_clave"] or "").split(",") if p.strip()]


def negocio():
    n = ajustes()
    data = {
        "@type": ["LocalBusiness", "EntertainmentBusiness"],
        "@id": _abs("/#negocio"),
        "name": n["nombre"],
        "legalName": n["razon_social"] or None,
        "description": descripcion_negocio(),
        "slogan": n["slogan"] or None,
        "url": _abs("/"),
        "logo": _abs(url_for("static", filename="img/icon-512.png")),
        "image": _abs(url_for("static", filename="img/og-default.jpg")),
        "telephone": n["telefono"] or None,
        "email": n["email"] or None,
        "priceRange": "$$",
        "currenciesAccepted": "CLP",
        "areaServed": n["zona"] or None,
        "address": {"@type": "PostalAddress", "addressLocality": n["ciudad"] or None,
                    "addressRegion": n["region"] or None, "addressCountry": "CL"},
        "sameAs": [u for u in (n["instagram"], n["facebook"]) if u] or None,
        "knowsAbout": palabras_clave() or None,
        "keywords": n["seo_palabras_clave"] or None,
    }
    return _limpiar(data)


def sitio_web():
    return {
        "@type": "WebSite",
        "@id": _abs("/#web"),
        "url": _abs("/"),
        "name": ajustes()["nombre"],
        "inLanguage": "es-CL",
        "publisher": {"@id": _abs("/#negocio")},
        # Habilita el cuadro de búsqueda del sitio en Google
        "potentialAction": {
            "@type": "SearchAction",
            "target": _abs(url_for("public.catalogo_completo")) + "?q={search_term_string}",
            "query-input": "required name=search_term_string",
        },
    }


def producto(juego, imagen_url):
    return _limpiar({
        "@type": "Product",
        "@id": _abs(url_for("public.juego", slug=juego.slug)) + "#producto",
        "name": juego.nombre,
        "description": juego.descripcion or None,
        "image": _abs(imagen_url),
        "sku": juego.slug,
        "category": juego.categoria.nombre,
        "brand": {"@type": "Brand", "name": ajustes()["nombre"]},
        "additionalProperty": [
            {"@type": "PropertyValue", "name": nombre, "value": valor}
            for nombre, valor in (("Medidas", juego.medidas), ("Edad", juego.edad), ("Capacidad", juego.capacidad))
            if valor
        ] or None,
        "offers": {
            "@type": "Offer",
            "price": juego.precio,
            "priceCurrency": "CLP",
            "priceSpecification": {
                "@type": "UnitPriceSpecification", "price": juego.precio, "priceCurrency": "CLP",
                "valueAddedTaxIncluded": not (ajustes()["precio_sufijo"] or "").strip().startswith("+"),
            },
            "availability": "https://schema.org/InStock",
            "businessFunction": "http://purl.org/goodrelations/v1#LeaseOut",  # arriendo
            "url": _abs(url_for("public.juego", slug=juego.slug)),
            "seller": {"@id": _abs("/#negocio")},
        },
    })


def faq(preguntas):
    if not preguntas:
        return None
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": p.titulo,
             "acceptedAnswer": {"@type": "Answer", "text": p.texto}}
            for p in preguntas
        ],
    }


def migas(items):
    """items: [(nombre, url_relativa)] — el inicio se agrega solo."""
    todos = [("Inicio", "/")] + list(items)
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": nombre, "item": _abs(url)}
            for i, (nombre, url) in enumerate(todos, start=1)
        ],
    }


def lista(juegos, desde=0):
    return {
        "@type": "ItemList",
        "itemListElement": [
            {"@type": "ListItem", "position": desde + i, "url": _abs(url_for("public.juego", slug=j.slug)),
             "name": j.nombre}
            for i, j in enumerate(juegos, start=1)
        ],
    }


def grafo(*nodos):
    """Une varios nodos en un único bloque JSON-LD (@graph)."""
    return {"@context": "https://schema.org", "@graph": [negocio(), sitio_web()] + [n for n in nodos if n]}


def _limpiar(d):
    """Quita claves vacías para no publicar datos nulos."""
    if isinstance(d, dict):
        return {k: _limpiar(v) for k, v in d.items() if v not in (None, "", [], {})}
    if isinstance(d, list):
        return [_limpiar(v) for v in d]
    return d
