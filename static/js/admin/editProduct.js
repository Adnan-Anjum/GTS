const shopModal = document.getElementById('editProductForm');
const shopModalBackDrop = document.getElementById('shopModalBackDrop');
let currentBtn = '';

// Add data and toggle modal
function addProductData(e) {
  shopModal.reset();
  currentBtn = e.currentTarget;
  shopModal.querySelector('#modalProductImgInput').value = currentBtn.querySelector('.productImg').src;
  shopModal.querySelector('#modalProductImg').src = currentBtn.querySelector('.productImg').src;
  shopModal.querySelector('#modalProductImg').alt = currentBtn.querySelector('.productImg').alt;
  shopModal.querySelector('#modalProductTitle').value = currentBtn.querySelector('.productTitle').innerHTML.trim();
  shopModal.querySelector('#modalProductId').value = currentBtn.id;
  productPriceInfo = currentBtn.querySelectorAll('.productPrice').forEach( (priceElement) => {
    shopModal.querySelector('#modalProductPrice').value += `${priceElement.innerHTML.trim()},`;
  });
  shopModal.querySelector('#modalProductDescription').value = currentBtn.querySelector('.productDescription').innerHTML.trim();
  shopModal.querySelector('#modalProductWidth').value = currentBtn.querySelector('.productWidth').innerHTML.trim();
  shopModal.querySelector('#modalProductHeight').value = currentBtn.querySelector('.productHeight').innerHTML.trim();
  toggleShopModal();
}

// Submit update form
function submitEditProductForm(e) {
  e.preventDefault();
  // If any vaue is empty set a default one
  if (shopModal.querySelector('#modalProductTitle').value.trim() === '') {
    shopModal.querySelector('#modalProductTitle').value = currentBtn.querySelector('.productTitle').innerHTML.trim();
  }
  if (shopModal.querySelector('#modalProductDescription').value.trim() === '') {
    shopModal.querySelector('#modalProductDescription').value = currentBtn.querySelector('.productDescription').innerHTML.trim();
  }
  if (shopModal.querySelector('#modalProductWidth').value.trim() === '') {
    shopModal.querySelector('#modalProductWidth').value = currentBtn.querySelector('.productWidth').innerHTML.trim();
  }
  if (shopModal.querySelector('#modalProductHeight').value.trim() === '') {
    shopModal.querySelector('#modalProductHeight').value = currentBtn.querySelector('.productHeight').innerHTML.trim();
  }
  if (shopModal.querySelector('#modalProductPrice').value.trim() === '') {
    shopModal.querySelector('#modalProductPrice').value += `${priceElement.innerHTML.trim()},`;
  }
  let formData = {};
  shopModal.querySelectorAll('.inputToSend').forEach((inputBox) => {
    if (inputBox.name)
      formData[inputBox.name] = inputBox.value.trim();
  })
  let productPriceInfo = shopModal.querySelector('#modalProductPrice').value.trim().replaceAll(', ', ',').replaceAll(' ,', ',');
  formData['productPriceInfo'] = productPriceInfo.split(',');

  fetch('/adminPanel/updateProductData/', {
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
        currentBtn.querySelector('.productImg').src = data.data.productImage;
        currentBtn.querySelector('.productTitle').innerHTML = data.data.productName;
        currentBtn.querySelectorAll('.productPrice').forEach( (priceElement) => {
          priceElement.remove();
        });
        Array.from(data.data.productPriceInfo).forEach( (priceInfo) => {
          currentBtn.querySelector('#productPriceContainer').innerHTML += `<p class="productPrice">${priceInfo}</p>`;
        })
        currentBtn.querySelector('.productDescription').innerHTML = data.data.description;
        currentBtn.querySelector('.productWidth').innerHTML = data.data.width;
        currentBtn.querySelector('.productHeight').innerHTML = data.data.height;
        toggleShopModal();
    }
  })
}

// Toggle the shop modal
function toggleShopModal() {
  shopModalBackDrop.classList.toggle('show');
  shopModal.classList.toggle('show');
}