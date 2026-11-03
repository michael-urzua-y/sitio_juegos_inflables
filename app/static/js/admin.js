/* Panel admin: confirmaciones, menú móvil y vista previa de imagen (sin JS inline por CSP) */
(function () {
  "use strict";

  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!window.confirm(form.dataset.confirm)) e.preventDefault();
    });
  });

  document.querySelectorAll("[data-confirm-click]").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      if (!window.confirm(btn.dataset.confirmClick)) e.preventDefault();
    });
  });

  document.querySelectorAll("[data-toggle-side]").forEach(function (el) {
    el.addEventListener("click", function () { document.body.classList.toggle("side-open"); });
  });

  // Filtros que se aplican al cambiar el select (sin botón)
  document.querySelectorAll("form[data-autosubmit] select").forEach(function (sel) {
    sel.addEventListener("change", function () { sel.form.submit(); });
  });

  // ---------- Categorías desde el select del formulario de juegos ----------
  var gestor = document.querySelector("[data-cat-manager]");
  if (gestor) {
    var select = gestor.querySelector("select");
    var form = gestor.querySelector("[data-cat-form]");
    var nombre = gestor.querySelector("[data-cat-nombre]");
    var msg = gestor.querySelector("[data-cat-msg]");
    var token = document.querySelector('meta[name="csrf-token"]').content;

    var aviso = function (texto, tipo) {
      msg.textContent = texto;
      msg.className = "cat-select__msg cat-select__msg--" + tipo;
      msg.hidden = false;
    };
    var enviar = function (url, datos) {
      return fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": token },
        body: JSON.stringify(datos || {}),
        credentials: "same-origin"
      }).then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (j) {
          if (!r.ok) throw new Error(j.error || "No se pudo completar la acción.");
          return j;
        });
      });
    };
    var abrir = function (abierto) {
      form.hidden = !abierto;
      if (abierto) { nombre.value = ""; nombre.focus(); }
    };

    gestor.querySelector("[data-cat-nueva]").addEventListener("click", function () { abrir(form.hidden); });
    gestor.querySelector("[data-cat-cancelar]").addEventListener("click", function () { abrir(false); });

    var crear = function () {
      var valor = nombre.value.trim();
      if (!valor) { nombre.focus(); return; }
      enviar(gestor.dataset.urlCrear, { nombre: valor }).then(function (cat) {
        var opt = new Option(cat.nombre, cat.id, true, true);
        select.add(opt);
        abrir(false);
        aviso("Categoría “" + cat.nombre + "” creada y seleccionada.", "ok");
      }).catch(function (e) { aviso(e.message, "error"); });
    };
    gestor.querySelector("[data-cat-crear]").addEventListener("click", crear);
    nombre.addEventListener("keydown", function (e) {
      if (e.key === "Enter") { e.preventDefault(); crear(); }   // no envía el formulario del juego
      if (e.key === "Escape") abrir(false);
    });

    gestor.querySelector("[data-cat-quitar]").addEventListener("click", function () {
      var opt = select.options[select.selectedIndex];
      if (!opt) return;
      if (!window.confirm("¿Quitar la categoría “" + opt.text + "”?")) return;
      var url = gestor.dataset.urlQuitar.replace("/0/quitar", "/" + encodeURIComponent(opt.value) + "/quitar");
      enviar(url).then(function () {
        select.remove(select.selectedIndex);
        aviso("Categoría “" + opt.text + "” eliminada.", "ok");
      }).catch(function (e) { aviso(e.message, "error"); });
    });
  }

  // ---------- Foto del juego: vista previa y validación de tamaño ----------
  var file = document.querySelector("[data-file]");
  var preview = document.querySelector("[data-preview]");
  var fileMsg = document.querySelector("[data-file-msg]");
  if (file && preview) {
    var textoAyuda = fileMsg ? fileMsg.textContent : "";
    var mensaje = function (texto, tipo) {
      if (!fileMsg) return;
      fileMsg.textContent = texto;
      fileMsg.className = "muted small upload-help" + (tipo ? " upload-help--" + tipo : "");
    };
    file.addEventListener("change", function () {
      var f = file.files && file.files[0];
      if (!f) { mensaje(textoAyuda); return; }
      var maxMb = Number(file.dataset.maxMb) || 25;
      if (f.size > maxMb * 1024 * 1024) {
        file.value = "";
        mensaje("La foto pesa " + (f.size / 1048576).toFixed(1) + " MB y el máximo es " + maxMb + " MB. Elige otra o envíatela comprimida (por ejemplo por WhatsApp).", "error");
        return;
      }
      var esHeic = /\.(heic|heif)$/i.test(f.name) || /heic|heif/i.test(f.type);
      if (esHeic) {
        // Los navegadores no muestran HEIC: se convierte al guardar
        mensaje("Foto de iPhone (HEIC) lista: se convertirá automáticamente al guardar. La vista previa aparecerá después de guardar.", "ok");
        return;
      }
      var url = URL.createObjectURL(f);
      preview.onerror = function () { mensaje("No se puede previsualizar este formato, pero se convertirá al guardar.", "ok"); };
      preview.src = url;
      mensaje("“" + f.name + "” lista. Se ajustará y optimizará al guardar.", "ok");
    });
  }
})();
