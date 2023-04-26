// Submit AddProduct Form data with fetch
const addProductForm = document.getElementById('addProductForm');

function submitAddProductForm(e) {
  e.preventDefault();
  let formData = {};

  addProductForm.querySelectorAll('.inputToSend').forEach((inputBox) => {
    if (inputBox.name)
      formData[inputBox.name] = inputBox.value.trim();
  });
  let productPriceInfo = addProductForm.querySelector('#productPriceInfo').value.trim().replaceAll(', ', ',').replaceAll(' ,', ',');
  formData['productPriceInfo'] = productPriceInfo.split(',');

  fetch('/adminPanel/saveNewProduct/', {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Accept': 'application/json',
      'X-CSRFToken': document.getElementById('hiddenCsrfToken').value,
    },
    body: JSON.stringify(formData)
  }).then(res => {
    return res.json();
  }).then(data => {
    switch (data.status) {
      case 'failed':
        alert('Something went wrong! Please try again later...');
        break;
      default:
        addProductForm.reset();
        alert('Data saved succesfully.');
    }
  })
}