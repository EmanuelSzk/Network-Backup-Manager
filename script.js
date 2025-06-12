function mostrarFormulario() {
  const formulario = document.getElementById("formularioBackup");
  if (formulario.style.display === "block") {
    formulario.style.display = "none";
  } else {
    formulario.style.display = "block";
  }
}

function ocultarFormulario() {
  const formulario = document.getElementById("formularioBackup");
  formulario.style.display = "none";
}

let dispositivoSeleccionado = null;

function seleccionarDispositivo(fila) {
  // Desmarcar otras filas
  const filas = document.querySelectorAll("tbody tr");
  filas.forEach(f => f.classList.remove("seleccionado"));

  // Marcar esta fila
  fila.classList.add("seleccionado");

  // Guardar referencia o datos
  const celdas = fila.querySelectorAll("td");
  dispositivoSeleccionado = {
    nombre: celdas[0].textContent,
    ip: celdas[1].textContent,
    tipo: celdas[2].textContent,
  };

  console.log("Seleccionado:", dispositivoSeleccionado);
}

fetch('http://localhost:5000/dispositivos')
  .then(response => response.json())
  .then(data => {
    const tbody = document.getElementById("tablaDispositivos");
    data.forEach(dispositivos => {
      const fila = document.createElement("tr");
      fila.onclick = function () { seleccionarDispositivo(fila); };
      fila.innerHTML = `
      <td>${dispositivos.nombre}</td>
      <td>${dispositivos.ip}</td>
      <td>${dispositivos.tipo}</td>
      `;
      tbody.appendChild(fila);
    });
  })
  .catch(error => console.error('Error al cargar los dispositivos:', error));