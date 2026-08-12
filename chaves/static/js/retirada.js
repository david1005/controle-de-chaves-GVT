document.addEventListener("DOMContentLoaded", () => {

  const campoData = document.getElementById("data");
  const hoje = new Date();
  const dataFormatada = hoje.toISOString().split("T")[0];
  campoData.value = dataFormatada;

  
  const campoHorario = document.getElementById("horario");
  const horas = String(hoje.getHours()).padStart(2, "0");
  const minutos = String(hoje.getMinutes()).padStart(2, "0");
  campoHorario.value = `${horas}:${minutos}`;

  
  const selectChave = document.getElementById("chave");
  const resumoChave = document.getElementById("resumo-chave");
  const resumoLocal = document.getElementById("resumo-local");
  const resumoStatus = document.getElementById("resumo-status");

  selectChave.addEventListener("change", () => {
    const opt = selectChave.options[selectChave.selectedIndex];
    const local = opt.dataset.local;
    const status = opt.dataset.status;

    resumoLocal.textContent = local;
    resumoStatus.textContent = status === "ativa" ? "Ativa" : "Inativa";
    resumoStatus.className = `badge-chave badge-chave-${status}`;
    resumoChave.classList.remove("d-none");
  });


    const selectPessoa = document.getElementById("pessoa");
    const resumoCargo = document.getElementById("resumo-cargo");
    const previewFotoBox = document.getElementById("preview-foto-pessoa");

    selectPessoa.addEventListener("change", () => {
    const opt = selectPessoa.options[selectPessoa.selectedIndex];
    const foto = opt.dataset.foto;
    const cargo = opt.dataset.cargo;

    resumoCargo.textContent = cargo ? `Cargo: ${cargo}` : "";

    if (foto) {
        previewFotoBox.innerHTML = `<img src="${foto}" alt="Foto de ${opt.textContent.trim()}">`;
    } else {
        previewFotoBox.innerHTML = `<i class="fa-solid fa-user"></i>`;
    }
    });
});