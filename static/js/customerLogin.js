// Toggle Register and login forms
function toggleRegisterForm() {
  document.querySelectorAll('section.adminForm').forEach((formSection) => {
    formSection.classList.toggle('d-none');
  })
  document.querySelectorAll('h1 span').forEach((h1Span) => {
    h1Span.classList.toggle('d-none');
  })
}

// Send Login form data
const customerLoginForm = document.getElementById('customerLoginForm');
function submitCustomerLoginForm(e) {
  e.preventDefault();
  let formData = {};
  customerLoginForm.querySelectorAll('.inputToSend').forEach((inputBox) => {
    if (inputBox.name)
      formData[inputBox.name] = inputBox.value.trim();
  })

  fetch('/loginUser/', {
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
      case 'notFound':
        alert('No user found with that email!');
        break;
      case 'wrongPass':
        alert('The password you entered was incorrect!');
        break;
      default:
        window.location.href = '/';
        alert('Loggin you in. Please Wait...');
    }
  })
}

// Send Register form data
const customerRegisterForm = document.getElementById('customerRegisterForm');
function submitCustomerRegisterForm(e) {
  e.preventDefault();
  if (document.getElementById('customerPassword').value.trim() === document.getElementById('customerPasswordConfirm').value.trim()) {
    customerRegisterForm.querySelector('#contactNumber').value = customerRegisterForm.querySelector('#customerContactCode').value.trim() +' '+ customerRegisterForm.querySelector('#customerNumber').value.trim()
    customerRegisterForm.submit();
  } else {
    alert('Passswords don\'t match;')
  }
}