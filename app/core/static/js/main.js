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

// Ejemplo de uso:
// setupSelectParamUpdater("groupSelector", "group");