// This JS is used to handle dynamic updates of URL parameters based on user selections in a dropdown menu.
function setupSelectParamUpdater(selectId, paramName) {
  const select = document.querySelector(`#${selectId}`);
  if (!select) return;

  select.addEventListener("change", () => {
    const value = select.value;
    const params = new URLSearchParams(window.location.search);
    params.set(paramName, value);
    window.location.search = params.toString();
  });
}


// This JS is used to handle modal forms for confirmation before submitting actions like delete.
// It allows opening a modal with a form, closing it, and submitting the form when confirmed.
// It uses a global variable to keep track of the form to be submitted.
let modalFormToSubmit = null;

function openModalWithForm(form, modalId = 'confirm-modal') {
  modalFormToSubmit = form;
  document.getElementById(modalId).classList.add('is-active');
}

function closeModal(modalId = 'confirm-modal') {
  document.getElementById(modalId).classList.remove('is-active');
  modalFormToSubmit = null;
}

function submitModalForm(modalId = 'confirm-modal') {
  if (modalFormToSubmit) modalFormToSubmit.submit();
}

document.addEventListener('click', function (e) {
  if (
    e.target.matches('.modal-background') ||
    e.target.matches('.modal-close') ||
    e.target.matches('.jb-modal-close')
  ) {
    const modal = e.target.closest('.modal');
    if (modal) modal.classList.remove('is-active');
  }
});


/**
 * instance_status_checker.js
 * Recorre los elementos con data-instance y actualiza su estado vía /check-instance-status/<instanceName>/
 * Espera que cada fila tenga dentro un elemento con clase .status-tag donde mostrará el resultado.
 */
document.addEventListener("DOMContentLoaded", () => {
  const rows = document.querySelectorAll("[data-instance]");
  if (!rows.length) return;

  rows.forEach(row => {
    const instanceName = row.dataset.instance;
    const statusCell = row.querySelector(".status-tag");

    if (!instanceName || !statusCell) return;

    fetch(`/check-instance-status/${instanceName}/`)
      .then(res => res.json())
      .then(data => {
        const state = data?.instance?.state || "unknown";
        let html;
        switch (state) {
          case "open":
            html = `<span class="tag is-success">Working</span>`;
            break;
          case "close":
            html = `<span class="tag is-danger">Failed</span>`;
            break;
          default:
            html = `<span class="tag is-warning">${state}</span>`;
        }
        statusCell.innerHTML = html;
      })
      .catch(() => {
        if (statusCell) statusCell.innerHTML = `<span class="tag is-warning">error</span>`;
      });
  });
});