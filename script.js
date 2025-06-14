let formularioMostrado = false;
let nuevo = null;

function mostrarFormulario() {
  const formulario = document.getElementById("formularioBackup");
  if (!formularioMostrado) {
    formulario.style.display = "block";
    formularioMostrado = true;
  }
}

// Vacía campos
function nuevoDispositivo() {
  nuevo = true;
  document.getElementById("nombre").value = "";
  document.getElementById("ip").value = "";
  document.getElementById("tipo").value = "";
  document.getElementById("usuario").value = "";
  document.getElementById("contrasena").value = "";
  document.getElementById("ssh").value = "";
  document.getElementById("hora").value = "08:00";
  document.getElementById("carpeta").value = "C:/backups/";

  // Resetear checkboxes y opciones
  document
    .querySelectorAll('input[name="diasemana"]')
    .forEach((cb) => (cb.checked = false));
  document.querySelector(
    'input[name="periodicidad"][value="diario"]'
  ).checked = true;
  document.querySelector('input[name="diames"]').value = "1";

  mostrarFormulario();
}

let dispositivoSeleccionado = null;

function editarDispostivo() {
  mostrarFormulario();
  nuevo = false;
}

function seleccionarDispositivo(fila) {
  // Desmarcar otras filas
  const filas = document.querySelectorAll("tbody tr");
  filas.forEach((f) => f.classList.remove("seleccionado"));

  // Marcar esta fila
  fila.classList.add("seleccionado");

  // Obtener el ID del dataset
  const id = fila.dataset.id;

  // Hacer GET al backend para traer los datos completos
  fetch(`http://localhost:5000/dispositivos/${id}`)
    .then(response => response.json())
    .then(dispositivo => {
      document.getElementById("nombre").value = dispositivo.nombre;
      document.getElementById("ip").value = dispositivo.ip;
      document.getElementById("tipo").value = dispositivo.tipo;
      document.getElementById("usuario").value = dispositivo.usuario;
      document.getElementById("contrasena").value = dispositivo.contrasena;
      document.getElementById("ssh").value = dispositivo.puerto_ssh;
      // Aquí podrías guardar el ID para usarlo luego si implementás "Editar"
      dispositivoSeleccionado = dispositivo;
    })
    .catch(error => {
      console.error("Error al obtener dispositivo:", error);
      alert("No se pudo cargar la información del dispositivo");
    });
}

fetch("http://localhost:5000/dispositivos")
  .then((response) => response.json())
  .then((data) => {
    const tbody = document.getElementById("tablaDispositivos");
    data.forEach((dispositivo) => {
      const fila = document.createElement("tr");
      fila.onclick = function () {
        seleccionarDispositivo(fila);
      };
      fila.dataset.id = dispositivo.id; // Guarda el ID
      fila.innerHTML = `
        <td>${dispositivo.nombre}</td>
        <td>${dispositivo.ip}</td>
        <td>${dispositivo.tipo}</td>
      `;
      tbody.appendChild(fila);
    });
  })
  .catch(error => console.error('Error al cargar los dispositivos:', error));

document
  .querySelector("#formularioBackup form")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    const datos = {
      nombre: document.getElementById("nombre").value.trim(),
      ip: document.getElementById("ip").value.trim(),
      tipo: document.getElementById("tipo").value.trim(),
      usuario: document.getElementById("usuario").value.trim(),
      contrasena: document.getElementById("contrasena").value.trim(),
      ssh: document.getElementById("ssh").value.trim(),
      periodicidad: document.querySelector(
        'input[name="periodicidad"]:checked'
      )?.value,
      hora: document.getElementById("hora").value.trim(),
      diasemana: Array.from(
        document.querySelectorAll('input[name="diasemana"]:checked')
      ).map((cb) => cb.value.trim()),
      diames: document.querySelector('input[name="diames"]').value.trim(),
      carpeta: document.getElementById("carpeta").value.trim(),
    };

    if (nuevo) {
      const resp = await fetch("http://localhost:5000/dispositivo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(datos),
      });

      const data = await resp.json();
      if (data.success) {
        alert(data.message);
      } else {
        alert("Error al guardar el dispositivo");
      }
    } else {
      // Agregar el id del dispositivo seleccionado
      if (dispositivoSeleccionado && dispositivoSeleccionado.id) {
        datos.id = dispositivoSeleccionado.id;
      } else {
        alert("No hay dispositivo seleccionado para editar.");
        return;
      }

      const resp = await fetch("http://localhost:5000/Editar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(datos),
      });

      const data = await resp.json();
      if (data.success) {
        alert(data.message);
      } else {
        alert("Error al guardar el dispositivo");
      }
    }
  });

document.getElementById("btnEliminar").addEventListener("click", function () {
  if (!dispositivoSeleccionado) {
    alert("Selecciona un dispositivo primero.");
    return;
  }
  if (!confirm("¿Estás seguro de que deseas eliminar este dispositivo?")) {
    return;
  }
  fetch(`http://localhost:5000/dispositivos/${dispositivoSeleccionado.id}`, {
    method: "DELETE",
  })
    .then((res) => res.json())
    .then((data) => {
      alert(data.message);
      cargarDispositivos();
      dispositivoSeleccionado = null;
      // Quitar selección visual si tienes una clase .selected
      document
        .querySelectorAll("#tablaDispositivos tr.selected")
        .forEach((tr) => tr.classList.remove("selected"));
    });
});

document.getElementById("btnBackup").addEventListener("click", function () {
  if (!dispositivoSeleccionado || !dispositivoSeleccionado.id) {
    alert("Selecciona un dispositivo primero.");
    return;
  }
  if (!confirm("¿Deseas realizar el backup de este dispositivo?")) {
    return;
  }
  // Obtener la carpeta del input
  const carpeta = document.getElementById("carpeta").value.trim();

  fetch(`http://localhost:5000/backup/${dispositivoSeleccionado.id}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ carpeta: carpeta }),
  })
    .then((res) => res.json())
    .then((data) => {
      alert(data.message || data);
    })
    .catch((err) => {
      alert("Error al realizar el backup: " + err);
    });
});