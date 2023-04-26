// Checkout cart items
function checkoutCartItems(customerId) {
  // let containerCart=undefined
  // if(document.getElementById('containerProducts')){
  //   containerCart=document.getElementById('containerProducts').value
  // }
  // console.log(containerCart)
  // let inchesCart=''
  // if(document.getElementById('inchesProduct')){
  //   inchesCart=document.getElementById('inchesProduct').value
  // }
  // console.log(containerCart)
  // console.log(inchesCart)
  console.log('hii')
  let currentDate = new Date();
  let minuteZero = '';
  let dateZero = '';
  let monthZero = '';
  if (currentDate.getMinutes() <= 9) {
    minuteZero = '0';
  }
  let orderTime = currentDate.getHours() +'.'+ minuteZero + currentDate.getMinutes();
  if (currentDate.getDate() <= 9) {
      dateZero = '0';
  }
  if (currentDate.getMonth() <= 8) {
      monthZero = '0';
  }
  let orderDate = dateZero + currentDate.getDate() +'-'+ monthZero + (currentDate.getMonth() + 1) +'-'+ currentDate.getFullYear()

  // Calculating cart value adding individual prices
  // let temp= document.getElementById('product_price')
  // console.log(temp.innerHTML)
  let cartTotal = 0;
  document.querySelectorAll('.productFinalPrice').forEach((priceElement) => {
    cartTotal += Number(priceElement.innerHTML);
  })
  console.log(typeof document.getElementById('cartItemId').value.trim())
  console.log(cartTotal)
  let dataToSend = {
    'customerId': customerId,
    // 'cartItemId': document.getElementById('cartItemId').value.trim(),
    'orderTimestamp':currentDate.getTime(),
    'orderDate':orderDate,
    'orderTime':Number(orderTime),
    'orderStatus':'pending',
    'orderAmount':cartTotal,
    // 'containerCart':containerCart,
    // 'inchesCart':String(inchesCart),
  }

  // console.log(inchesCart)
  // console.log(dataToSend)
  fetch('/checkoutCartItems/', {
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
        document.getElementById('checkoutBtn').remove();
        document.getElementById('cartWrapper').classList.add('text-center');
        document.getElementById('cartWrapper').innerHTML = '<h2>No Items in your cart</h2>';
        // alert('We have received your order! Thanks for shopping with us...');
        document.getElementById('finalAmountInp').value=data.orderAmount
        let form =document.getElementById('finalAmount')
        form.submit()
        // location.assign(`/afterCheckout/`)
    }
  })
}