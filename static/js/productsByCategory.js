const shopModal = document.getElementById('shopModal');
const shopModalBackDrop = document.getElementById('shopModalBackDrop');

let unit=''
// Add data to shop modal
function addShopData(e) {
  console.log('hi')
  if (shopModal.querySelector('.cartQuantity'))
    shopModal.querySelector('.cartQuantity').innerHTML = 0;
  shopModal.querySelector('#modalProductPrice').innerHTML = '';
  shopModal.querySelector('#modalProductImg').src = e.currentTarget.querySelector('.productImg').src;
  shopModal.querySelector('#modalProductImg').alt = e.currentTarget.querySelector('.productImg').alt;
  shopModal.querySelector('#modalProductTitle').innerHTML = e.currentTarget.querySelector('.productTitle').innerHTML.trim();
  productPriceInfo = e.currentTarget.querySelectorAll('.productPrice').forEach( (priceElement) => {
    shopModal.querySelector('#modalProductPrice').innerHTML += `${priceElement.innerHTML.trim()}<br>`;
  });
  shopModal.querySelector('.modalProductDescription').innerHTML = e.currentTarget.querySelector('.productDescription').innerHTML.trim();
  if (e.currentTarget.querySelector('.productWidth').innerHTML.trim() !== '') {
    shopModal.querySelector('.modalProductDimensions').innerHTML = e.currentTarget.querySelector('.productWidth').innerHTML.trim() +' inches X '+ e.currentTarget.querySelector('.productHeight').innerHTML.trim() +' inches';
  }
  // =? MY
  // shopModal.querySelector('.modalProductunit').innerHTML = 
  // if(e.currentTarget.querySelector('.productUnit').innerHTML!='ml'){
  //   if(e.currentTarget.querySelector('.productUnit').innerHTML=='of'){
  //     shopModal.querySelector('.modalProductunit').innerHTML = 'set'  
  //   }
  //   else{
    // if(e.currentTarget.querySelector('.productUnit').innerHTML==''){
    if(e.currentTarget.querySelector('.productUnit').innerHTML==='inch'){
      let select_tag=shopModal.querySelector('.modalInch')
      select_tag.classList.remove('d-none')
      unit='inch'
      shopModal.querySelector('.modalProductunit').innerHTML = e.currentTarget.querySelector('.productUnit').innerHTML
    }
    else{
      let select_tag=shopModal.querySelector('.modalInch')
      select_tag.classList.add('d-none')
      unit=''
      shopModal.querySelector('.modalProductunit').innerHTML = e.currentTarget.querySelector('.productUnit').innerHTML
    }
    // }
    // else{
    //   shopModal.querySelector('.modalProductunit').innerHTML = e.currentTarget.querySelector('.productUnit').innerHTML
    // }
  // }
  // }
  // else{
  //   let select_tag=document.createElement('select')
  //   let option_tag1=document.createElement('option')
  //   let option_tag2=document.createElement('option')
  //   option_tag1.innerHTML='ml'
  //   option_tag2.innerHTML='l'
  //   select_tag.appendChild(option_tag1)
  //   select_tag.appendChild(option_tag2)
  //   shopModal.querySelector('.modalProductunit').innerHTML=''
  //   shopModal.querySelector('.modalProductunit').appendChild(select_tag)
  // }
  if (shopModal.querySelector('#modalCartBtn')) {
    shopModal.querySelector('#modalCartBtn').setAttribute('onclick', `addToCart("${e.currentTarget.id}")`);
  }
  toggleShopModal();
}

// Toggle the shop modal
function toggleShopModal() {
  shopModalBackDrop.classList.toggle('show');
  shopModal.classList.toggle('show');
}

// Add to cart logic
function addToCart(productId) {
  console.log(unit)
  console.log(shopModal.querySelector('.cartQuantity').value);
  console.log(shopModal.querySelector('.modalInch').value);
  if (Number(shopModal.querySelector('.cartQuantity').value) > 0) {
    let dataToSend={}
    if(unit==''){
      dataToSend = {
        'customerId':document.getElementById('customerLoginId').value.trim(),
        'cartQuantity':shopModal.querySelector('.cartQuantity').value.trim(),
        'inch_input':'not inch',
        'productId':productId
      }
    }
    else{
      dataToSend = {
        'customerId':document.getElementById('customerLoginId').value.trim(),
        'cartQuantity':shopModal.querySelector('.cartQuantity').value.trim(),
        'inch_input':shopModal.querySelector('.modalInch').value.trim(),
        'productId':productId
      }
    }
    console.log(dataToSend)
    fetch('/addToCart/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Accept': 'application/json',
        'X-CSRFToken': document.getElementById('hiddenCsrfToken').value,
      },
      body: JSON.stringify(dataToSend)
    }).then(res => {
      return res.json();
    }).then(data => {
      switch (data.status) {
        case 'failed':
          alert('Something went wrong! Please try again later...');
          break;
        default:
          alert('product added to Cart!');
          toggleShopModal();
      }
    })
  }
}