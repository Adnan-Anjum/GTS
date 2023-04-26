// Show/Hide to top button
const backToTop = document.getElementById('backToTop');

window.onscroll = function () {
  if (window.scrollY > 100) {
    backToTop.style.display = 'block';
  } else {
    backToTop.style.display = '';
  }
}

// Date range picker inputs
$('input#dateRange').daterangepicker();

// Increment and Decrement button
function decrementBtn(e) {
  if (Number(e.currentTarget.nextElementSibling.value) <= 0) {
    e.currentTarget.nextElementSibling.value = 0;
  } else {
    e.currentTarget.nextElementSibling.value = Number(e.currentTarget.nextElementSibling.value) - 1;
  }
}
function incrementBtn(e) {
  e.currentTarget.previousElementSibling.value = Number(e.currentTarget.previousElementSibling.value) + 1;
}


function user_profile(x){
  console.log(x)
  window.location.href=`/userprofile/${x}`;
}
// Logout the customer  
function customerLogout() {
  if (confirm('Do you want to logout?')) {
    fetch('/logoutUser/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Accept': 'application/json',
        'X-CSRFToken': document.getElementById('hiddenCsrfToken').value,
      },
    }).then(res => {
      return res.json();
    }).then(data => {
      switch (data.status) {
        case 'failed':
          alert('Something went wrong! Please try again after some time...');
          break;
        default:
          window.location.href = '/';
      }
    })
  }
}

// Limit number inputs on text inputs
function isNumberKey(evt) {
  var charCode = (evt.which) ? evt.which : evt.keyCode
  if (charCode > 31 && (charCode < 48 || charCode > 57))
    return false;
  return true;
}

// Set input values to uppercase if necessary
function inputUpper(e) {
  e.currentTarget.value = e.currentTarget.value.toUpperCase().trim();
}

// Add Photo in string
function phototoString(e) {
  if (e.target.files[0].size > 150000) {
    alert("File shouldn't be bigger than 150 KB");
    e.currentTarget.value = "";
    return false;
  };
  const attachedFile = e.target.files[0];
  const reader = new FileReader();
  const stringInput = e.currentTarget.nextElementSibling;
  reader.readAsBinaryString(attachedFile);

  reader.onload = function (event) {
    stringInput.value = `data:${attachedFile.type};base64,${btoa(event.target.result)}`;
    alert('Image Saved Succesfully');
  }
}

// Infinite Carousel Logic
$('.carouselBtn.carouselLeft').click(function () {
  console.log('move left');
})
$('.carouselBtn.carouselRight').click(function () {
  console.log('move right');
})