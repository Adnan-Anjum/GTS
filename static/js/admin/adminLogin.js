// Send Login form data
const adminLoginForm = document.getElementById('adminLoginForm');
function submitAdminLoginForm(e) {
  e.preventDefault();
  let formData = {};
  adminLoginForm.querySelectorAll('.inputToSend').forEach( (inputBox) => {
    if (inputBox.name)
      formData[inputBox.name] = inputBox.value.trim();
  })

  fetch('/adminPanel/loginAdmin/', {
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
        alert('Please check the mail you entered!');
        break;
      case 'wrongPass':
        alert('The password you entered was incorrect!');
        break;
      default:
        document.getElementById('redirectName').value = data.adminName;
        alert('Logged in Succesfully.');
        document.getElementById('redirectForm').submit();
    }
  })
}