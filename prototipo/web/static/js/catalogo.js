/* Catálogo: formatos, carrusel, modal y carrito por AJAX. */
(() => {
  const formatos = (raiz = document) => {
    raiz.querySelectorAll("[data-formatos]").forEach((select) => {
      if (select.dataset.listo) return;
      select.dataset.listo = "1";
      const precio = select.closest("form, .cuerpo, .producto-modal-cuerpo")?.querySelector("[data-precio-visible]");
      const pintar = () => {
        const opcion = select.selectedOptions[0];
        if (precio && opcion) precio.textContent = opcion.dataset.texto;
      };
      select.addEventListener("change", pintar);
    });
  };

  const carruseles = (raiz = document) => {
    raiz.querySelectorAll("[data-carrusel]").forEach((caja) => {
      if (caja.dataset.listo) return;
      caja.dataset.listo = "1";
      const fotos = [...caja.querySelectorAll(":scope > img")];
      const puntos = [...caja.querySelectorAll("[data-punto]")];
      let actual = 0;
      const mostrar = (indice) => {
        actual = (indice + fotos.length) % fotos.length;
        fotos.forEach((foto, i) => { foto.hidden = i !== actual; });
        puntos.forEach((punto, i) => punto.toggleAttribute("aria-current", i === actual));
      };
      caja.querySelector("[data-prev]")?.addEventListener("click", (evento) => {
        evento.preventDefault();
        evento.stopPropagation();
        mostrar(actual - 1);
      });
      caja.querySelector("[data-next]")?.addEventListener("click", (evento) => {
        evento.preventDefault();
        evento.stopPropagation();
        mostrar(actual + 1);
      });
      puntos.forEach((punto, i) => punto.addEventListener("click", (evento) => {
        evento.stopPropagation();
        mostrar(i);
      }));
    });
  };

  const banner = () => {
    const caja = document.querySelector("[data-banner]");
    if (!caja) return;
    const fotos = [...caja.querySelectorAll(".portada-foto")];
    if (fotos.length < 2) return;
    let actual = 0;
    setInterval(() => {
      fotos[actual].hidden = true;
      actual = (actual + 1) % fotos.length;
      fotos[actual].hidden = false;
    }, 4500);
  };

  const toast = (mensaje, ok = true) => {
    let caja = document.querySelector("[data-toast]");
    if (!caja) {
      caja = document.createElement("div");
      caja.className = "toast-carrito";
      caja.dataset.toast = "";
      document.body.appendChild(caja);
    }
    caja.textContent = mensaje;
    caja.classList.toggle("error", !ok);
    caja.hidden = false;
    clearTimeout(caja._timer);
    caja._timer = setTimeout(() => { caja.hidden = true; }, 2800);
  };

  const actualizarCotizacion = (cantidad) => {
    const enlace = document.querySelector("[data-carrito-cantidad]");
    if (!enlace) return;
    enlace.dataset.carritoCantidad = String(cantidad);
    enlace.textContent = `Cotización (${cantidad})`;
  };

  const enviarCarrito = async (form) => {
    const boton = form.querySelector("[type='submit']");
    if (boton) boton.disabled = true;
    try {
      const respuesta = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          Accept: "application/json",
        },
        credentials: "same-origin",
      });
      const datos = await respuesta.json();
      toast(datos.mensaje || (datos.ok ? "Agregado a la cotización." : "No se pudo agregar."), Boolean(datos.ok));
      if (datos.ok) {
        if (typeof datos.carrito_cantidad === "number") actualizarCotizacion(datos.carrito_cantidad);
        const dialogo = form.closest("dialog");
        if (dialogo?.open) dialogo.close();
      }
    } catch (_error) {
      toast("No se pudo agregar. Inténtalo de nuevo.", false);
    } finally {
      if (boton) boton.disabled = false;
    }
  };

  const modal = document.querySelector("[data-modal]");
  const cuerpo = modal?.querySelector("[data-modal-cuerpo]");

  const abrir = (tarjeta) => {
    if (!modal || !cuerpo) return;
    const fotos = tarjeta.querySelector("[data-fotos]");
    const formTpl = tarjeta.querySelector("[data-form-modal]");
    const nombre = tarjeta.dataset.nombre || "";
    const descripcion = tarjeta.dataset.descripcion || "";
    cuerpo.innerHTML = `
      <div class="modal-marco">
        <div class="modal-galeria" data-modal-galeria></div>
        <div class="modal-info">
          <p class="rubro modal-rubro">Detalle</p>
          <h2></h2>
          <p class="modal-desc"></p>
          <div data-modal-form></div>
          <p class="modal-aviso" data-aviso hidden>Para agregar debes marcar una opción en Personalizar producto.</p>
        </div>
      </div>
    `;
    cuerpo.querySelector("h2").textContent = nombre;
    cuerpo.querySelector(".modal-desc").textContent = descripcion;
    const galeria = cuerpo.querySelector("[data-modal-galeria]");
    if (tarjeta.dataset.retrato === "1") galeria.classList.add("retrato");
    if (fotos) {
      galeria.innerHTML = fotos.innerHTML;
      if (galeria.querySelectorAll("img").length > 1) {
        galeria.classList.add("carrusel");
        galeria.dataset.carrusel = "";
        galeria.insertAdjacentHTML("beforeend", `
          <button type="button" class="flecha prev" data-prev aria-label="Anterior">‹</button>
          <button type="button" class="flecha next" data-next aria-label="Siguiente">›</button>
        `);
      }
    }
    const formHost = cuerpo.querySelector("[data-modal-form]");
    if (formTpl) formHost.appendChild(formTpl.content.cloneNode(true));
    formatos(cuerpo);
    carruseles(cuerpo);
    modal.showModal();
  };

  document.addEventListener("submit", (evento) => {
    const form = evento.target.closest("form[data-compra], form.modal-compra");
    if (!form) return;
    evento.preventDefault();
    const radios = form.querySelectorAll("input[name='opcion']");
    if (radios.length && ![...radios].some((radio) => radio.checked)) {
      const aviso = form.closest(".modal-info, [data-modal-cuerpo]")?.querySelector("[data-aviso]")
        || document.querySelector("[data-aviso]");
      if (aviso) aviso.hidden = false;
      else toast("Marca una opción para personalizar el producto.", false);
      return;
    }
    enviarCarrito(form);
  });

  document.addEventListener("click", (evento) => {
    if (evento.target.closest("[data-prev], [data-next], [data-punto]")) return;
    const requiere = evento.target.closest("[data-requiere-opcion]");
    if (requiere) {
      evento.preventDefault();
      const tarjeta = requiere.closest("[data-producto]");
      if (tarjeta) abrir(tarjeta);
      return;
    }
    const boton = evento.target.closest("[data-abrir]");
    if (!boton) return;
    const tarjeta = boton.closest("[data-producto]");
    if (tarjeta) abrir(tarjeta);
  });

  modal?.querySelector("[data-cerrar]")?.addEventListener("click", () => modal.close());
  modal?.addEventListener("click", (evento) => {
    if (evento.target === modal) modal.close();
  });

  formatos();
  carruseles();
  banner();
})();
