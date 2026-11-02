/* =========================================================
   Sitio público: menú, filtros del catálogo y cotizador WhatsApp
   ========================================================= */
(function () {
  "use strict";

  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };
  var SITE = { whatsapp: document.body.dataset.whatsapp, nombre: document.body.dataset.negocio };
  var STORAGE_KEY = "cotizacion_v1";
  var clp = function (n) { return "$" + Math.round(n).toLocaleString("es-CL"); };

  /* ---------- Header / navegación ---------- */
  var header = $("#header");
  var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 8); };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  var nav = $("#nav");
  var burger = $("[data-burger]");
  var setMenu = function (open) {
    nav.classList.toggle("is-open", open);
    burger.setAttribute("aria-expanded", String(open));
    document.body.classList.toggle("no-scroll", open);
  };
  burger.addEventListener("click", function () { setMenu(!nav.classList.contains("is-open")); });
  $$(".nav a").forEach(function (a) { a.addEventListener("click", function () { setMenu(false); }); });

  $$("[data-drop]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var parent = btn.parentElement;
      var open = !parent.classList.contains("is-open");
      parent.classList.toggle("is-open", open);
      btn.setAttribute("aria-expanded", String(open));
    });
  });

  /* ---------- Animación al hacer scroll ---------- */
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -40px 0px" });
    $$(".reveal").forEach(function (el) { io.observe(el); });
  } else {
    $$(".reveal").forEach(function (el) { el.classList.add("is-in"); });
  }

  /* ---------- Cotizador (carrito en localStorage) ---------- */
  var Cart = {
    items: {},
    load: function () {
      try { this.items = JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; } catch (e) { this.items = {}; }
    },
    save: function () {
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(this.items)); } catch (e) { /* modo privado */ }
      render();
    },
    add: function (d) {
      var it = this.items[d.slug];
      if (it) it.qty += 1;
      else this.items[d.slug] = { slug: d.slug, nombre: d.nombre, precio: Number(d.precio) || 0, cat: d.cat, qty: 1 };
      this.save();
    },
    setQty: function (slug, qty) {
      if (!this.items[slug]) return;
      if (qty <= 0) delete this.items[slug];
      else this.items[slug].qty = Math.min(qty, 20);
      this.save();
    },
    clear: function () { this.items = {}; this.save(); },
    list: function () { var it = this.items; return Object.keys(it).map(function (k) { return it[k]; }); },
    count: function () { return this.list().reduce(function (a, i) { return a + i.qty; }, 0); },
    total: function () { return this.list().reduce(function (a, i) { return a + i.qty * i.precio; }, 0); }
  };

  var cart = $("#cart");
  var overlay = $("[data-overlay]");
  var listEl = $("[data-list]");
  var form = $("[data-form]");
  var toastEl = $("[data-toast]");
  var toastTimer;

  var openCart = function () {
    toastEl.classList.remove("is-visible");
    overlay.hidden = false;
    requestAnimationFrame(function () { overlay.classList.add("is-visible"); });
    cart.classList.add("is-open");
    cart.setAttribute("aria-hidden", "false");
    document.body.classList.add("no-scroll");
    setMenu(false);
    $("[data-close-cart]", cart).focus();
  };
  var closeCart = function () {
    overlay.classList.remove("is-visible");
    cart.classList.remove("is-open");
    cart.setAttribute("aria-hidden", "true");
    document.body.classList.remove("no-scroll");
    setTimeout(function () { overlay.hidden = true; }, 300);
  };

  var toast = function (msg, accion) {
    toastEl.textContent = msg;
    if (accion) {
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = accion;
      b.addEventListener("click", function () { openCart(); toastEl.classList.remove("is-visible"); });
      toastEl.appendChild(b);
    }
    toastEl.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove("is-visible"); }, 3200);
  };

  // Construye cada fila con DOM (textContent) para evitar inyección de HTML
  var el = function (tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  };
  var iconBtn = function (icon, label, action, slug) {
    var b = el("button");
    b.type = "button";
    b.setAttribute("aria-label", label);
    b.dataset.action = action;
    b.dataset.slug = slug;
    b.innerHTML = '<svg class="ic"><use href="#i-' + icon + '"/></svg>';
    return b;
  };

  function render() {
    var items = Cart.list();
    var n = Cart.count();

    $$("[data-count]").forEach(function (c) {
      c.hidden = n === 0;
      if (c.textContent !== String(n)) { c.textContent = n; c.classList.remove("bump"); void c.offsetWidth; c.classList.add("bump"); }
    });
    $("[data-cart-sub]").textContent = n ? n + (n === 1 ? " juego seleccionado" : " juegos seleccionados") : "Agrega juegos para cotizar";
    $("[data-empty]").hidden = items.length > 0;
    form.hidden = items.length === 0;
    $("[data-foot]").hidden = items.length === 0;
    $("[data-total]").textContent = clp(Cart.total());
    if (typeof validar === "function" && form.elements.nombre) validar();

    listEl.textContent = "";
    items.forEach(function (it) {
      var li = el("li", "ci");
      var name = el("div", "ci__name", it.nombre);
      name.appendChild(el("span", "ci__cat", it.cat));
      li.appendChild(name);
      li.appendChild(el("div", "ci__price", clp(it.precio * it.qty)));

      var row = el("div", "ci__row");
      var qty = el("div", "qty");
      qty.appendChild(iconBtn("minus", "Quitar uno", "dec", it.slug));
      qty.appendChild(el("span", null, it.qty));
      qty.appendChild(iconBtn("plus", "Agregar uno", "inc", it.slug));
      row.appendChild(qty);
      var del = iconBtn("trash", "Eliminar " + it.nombre, "del", it.slug);
      del.className = "ci__del";
      del.appendChild(document.createTextNode(" Quitar"));
      row.appendChild(del);
      li.appendChild(row);
      listEl.appendChild(li);
    });

    $$("[data-add]").forEach(function (b) {
      var added = !!Cart.items[b.dataset.slug];
      b.classList.toggle("is-added", added);
      var span = $("span", b);
      if (!b.dataset.label) b.dataset.label = span.textContent;
      span.textContent = added ? "Agregado" : b.dataset.label;
      $("use", b).setAttribute("href", added ? "#i-check" : "#i-plus");
    });
  }

  listEl.addEventListener("click", function (e) {
    var b = e.target.closest("button[data-action]");
    if (!b) return;
    var it = Cart.items[b.dataset.slug];
    if (!it) return;
    if (b.dataset.action === "inc") Cart.setQty(it.slug, it.qty + 1);
    if (b.dataset.action === "dec") Cart.setQty(it.slug, it.qty - 1);
    if (b.dataset.action === "del") Cart.setQty(it.slug, 0);
  });

  document.addEventListener("click", function (e) {
    var add = e.target.closest("[data-add]");
    if (add) {
      if (Cart.items[add.dataset.slug]) { openCart(); return; }
      Cart.add(add.dataset);
      toast("“" + add.dataset.nombre + "” agregado a tu cotización", "Ver cotización");
      return;
    }
    if (e.target.closest("[data-open-cart]")) { e.preventDefault(); openCart(); return; }
    if (e.target.closest("[data-close-cart]") || e.target === overlay) closeCart();
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && cart.classList.contains("is-open")) closeCart(); });

  $("[data-clear]").addEventListener("click", function () {
    if (window.confirm("¿Vaciar tu cotización?")) Cart.clear();
  });

  /* ---------- Datos del evento: validación (todos obligatorios) ---------- */
  var DATOS_KEY = "cotizacion_datos_v1";
  var sendBtn = $("[data-send]");
  var faltanEl = $("[data-faltan]");
  var tocados = {};
  var campo = function (n) { return form.elements[n]; };
  var valor = function (n) { return (campo(n).value || "").trim(); };
  var hoyISO = function () {
    var d = new Date();
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  };
  campo("fecha").min = hoyISO();

  // Reglas: devuelven un mensaje de error o "" si el campo es válido
  var REGLAS = {
    nombre: function (v) { return v.length < 2 ? "Escribe tu nombre." : ""; },
    fecha: function (v) { return !v ? "Elige la fecha del evento." : (v < hoyISO() ? "La fecha no puede ser anterior a hoy." : ""); },
    comuna: function (v) { return v.length < 2 ? "Indica la comuna." : ""; },
    hora_inicio: function (v) { return !v ? "Indica la hora de inicio." : ""; },
    hora_fin: function (v) {
      if (!v) return "Indica la hora de término.";
      var ini = valor("hora_inicio");
      return ini && v <= ini ? "Debe ser posterior a la hora de inicio." : "";
    },
    detalles: function (v) { return v.length < 5 ? "Cuéntanos un poco del evento." : ""; }
  };
  var NOMBRES = { nombre: "nombre", fecha: "fecha", comuna: "comuna", hora_inicio: "hora de inicio",
                  hora_fin: "hora de término", detalles: "detalles del evento" };

  var mostrarError = function (n, msg) {
    var input = campo(n), label = input.closest(".field");
    var el = label.querySelector(".field__error");
    if (!el) { el = document.createElement("small"); el.className = "field__error"; label.appendChild(el); }
    var visible = !!msg && tocados[n];
    el.textContent = visible ? msg : "";
    input.setAttribute("aria-invalid", visible ? "true" : "false");
    label.classList.toggle("is-invalid", visible);
  };

  function validar() {
    var faltan = [];
    Object.keys(REGLAS).forEach(function (n) {
      var msg = REGLAS[n](valor(n));
      mostrarError(n, msg);
      if (msg) faltan.push(NOMBRES[n]);
    });
    var listo = Cart.count() > 0 && faltan.length === 0;
    sendBtn.disabled = !listo;
    if (!Cart.count()) faltanEl.textContent = "";
    else if (faltan.length) {
      var lista = faltan.length > 1 ? faltan.slice(0, -1).join(", ") + " y " + faltan[faltan.length - 1] : faltan[0];
      faltanEl.textContent = "Para enviar, completa: " + lista + ".";
    } else faltanEl.textContent = "¡Todo listo! Envía tu cotización.";
    faltanEl.classList.toggle("is-ok", listo);
    return listo;
  }

  // Guarda los datos en el navegador para no perderlos al cerrar el panel o recargar
  var guardarDatos = function () {
    var d = {};
    Object.keys(REGLAS).forEach(function (n) { d[n] = campo(n).value; });
    try { localStorage.setItem(DATOS_KEY, JSON.stringify(d)); } catch (e) { /* modo privado */ }
  };
  var cargarDatos = function () {
    var d;
    try { d = JSON.parse(localStorage.getItem(DATOS_KEY)) || {}; } catch (e) { d = {}; }
    Object.keys(REGLAS).forEach(function (n) {
      if (typeof d[n] === "string" && !(n === "fecha" && d[n] < hoyISO())) campo(n).value = d[n];
    });
  };

  form.addEventListener("input", function (e) {
    if (e.target.name === "hora_inicio" && valor("hora_fin")) tocados.hora_fin = true;
    guardarDatos(); validar();
  });
  form.addEventListener("focusout", function (e) {
    if (e.target.name && REGLAS[e.target.name]) { tocados[e.target.name] = true; validar(); }
  });
  form.addEventListener("submit", function (e) { e.preventDefault(); });

  /* ---------- Mensaje de WhatsApp (redactado con los datos del cliente) ---------- */
  var DIAS = ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"];
  var MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
               "septiembre", "octubre", "noviembre", "diciembre"];
  var fechaEnPalabras = function (iso) {
    var p = iso.split("-").map(Number);
    var d = new Date(p[0], p[1] - 1, p[2]);  // fecha local (sin desfase de zona horaria)
    return DIAS[d.getDay()] + " " + p[2] + " de " + MESES[p[1] - 1] + " de " + p[0];
  };
  // Código corto para identificar la cotización (sin caracteres confusos como 0/O, 1/I)
  var codigoReferencia = function () {
    var abc = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789", out = "", rnd = new Uint8Array(5);
    (window.crypto || window.msCrypto).getRandomValues(rnd);
    for (var i = 0; i < rnd.length; i++) out += abc[rnd[i] % abc.length];
    return "WEB-" + out;
  };
  var limpio = function (n, max) { return valor(n).replace(/\s+/g, " ").slice(0, max || 120); };

  var construirMensaje = function (ref) {
    var items = Cart.list();
    var varios = items.length > 1 || (items[0] && items[0].qty > 1);
    var lineas = [
      "🌐 *COTIZACIÓN WEB* · Ref. " + ref,
      "",
      "¡Hola " + SITE.nombre + "! 👋",
      "Mi nombre es *" + limpio("nombre", 60) + "* y quiero cotizar para el *" + fechaEnPalabras(valor("fecha")) +
        "*, en la comuna de *" + limpio("comuna", 40) + "*, entre las *" + valor("hora_inicio") + " y las " +
        valor("hora_fin") + " hrs*, " + (varios ? "los siguientes juegos:" : "el siguiente juego:"),
      ""
    ];
    items.forEach(function (it) {
      lineas.push("• " + it.qty + " × " + it.nombre + " — " + clp(it.precio * it.qty));
    });
    lineas.push(
      "",
      "💰 Total referencial: *" + clp(Cart.total()) + "*",
      "",
      "📝 Detalles del evento: " + limpio("detalles", 300),
      "",
      "¿Tienen disponibilidad? ¡Muchas gracias!",
      "_Enviado desde " + window.location.hostname + "_"
    );
    return lineas.join("\n");
  };

  sendBtn.addEventListener("click", function () {
    Object.keys(REGLAS).forEach(function (n) { tocados[n] = true; });
    if (!validar()) return;
    var url = "https://wa.me/" + encodeURIComponent(SITE.whatsapp) + "?text=" + encodeURIComponent(construirMensaje(codigoReferencia()));
    window.open(url, "_blank", "noopener");
  });

  // Sincroniza entre pestañas
  window.addEventListener("storage", function (e) { if (e.key === STORAGE_KEY) { Cart.load(); render(); } });

  cargarDatos();
  Cart.load();
  render();
})();
