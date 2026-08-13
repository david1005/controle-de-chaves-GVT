document.addEventListener('DOMContentLoaded', function () {

  
  const tabChave = document.getElementById('tab-chave');
  const tabPessoa = document.getElementById('tab-pessoa');
  const tipoInput = document.getElementById('tipo_cadastro');

  tabChave.addEventListener('shown.bs.tab', function () {
    tipoInput.value = 'chave';
  });

  tabPessoa.addEventListener('shown.bs.tab', function () {
    tipoInput.value = 'pessoa';
  });

  
  const inputFoto = document.getElementById('foto');
  const previewImg = document.getElementById('preview-img');
  const previewIcon = document.getElementById('preview-icon');

  inputFoto.addEventListener('change', function (event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (e) {
      previewImg.src = e.target.result;
      previewImg.classList.remove('d-none');
      previewIcon.classList.add('d-none');
    };
    reader.readAsDataURL(file);
  });

  
  const form = document.getElementById('form-cadastro');
  form.addEventListener('submit', function () {
    const tipo = tipoInput.value;
    form.action = tipo === 'pessoa'
      ? form.dataset.urlPessoa
      : form.dataset.urlChave;
    
  });

});