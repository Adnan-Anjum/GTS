const ctx = document.getElementById("dashboardGraph").getContext("2d");

// Getting this month daterange
let date = new Date();
let startDate = new Date(date.getFullYear(), date.getMonth(), 1);
let endDate = new Date(date.getFullYear(), date.getMonth() + 1, 0);
let dateRangeStart = startDate.getDate() +'/'+ startDate.getMonth() + 1 +'/'+ startDate.getFullYear();
let dateRangeEnd = endDate.getDate() +'/'+ endDate.getMonth() + 1 +'/'+ endDate.getFullYear();
$('input#dateRange').val(dateRangeStart +' - '+ dateRangeEnd);
fetchGraphData(startDate.getTime(), endDate.getTime());
// On button click filter information
function applyFilter() {
  disableFilterBtn();
  let startDate = document.getElementById('dateRange').value.split('-')[0].trim();
  let endDate = document.getElementById('dateRange').value.split('-')[1].trim();
  startDate = new Date(startDate.split('/')[2], (Number(startDate.split('/')[0]) - 1), startDate.split('/')[1], '00', '00', '00').getTime();
  endDate = new Date(endDate.split('/')[2], (Number(endDate.split('/')[0]) - 1), endDate.split('/')[1], '23', '59', '59').getTime();
  fetchGraphData(startDate, endDate, document.getElementById('filterSelect').value.trim());
}
// Get data to make a graph
function fetchGraphData(startTimestamp, endTimestamp, filterBy='ordersPlaced') {
  let dataToSend = {
    'startTimestamp':startTimestamp,
    'endTimestamp':endTimestamp,
    'filterBy':filterBy
  }
  fetch('/adminPanel/adminDashboardGraph/', {
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
        if (data.ordersList.length === 0) {
          alert('No data found! Please try to expand your filter...');
          makeGraph([{
            'xValue':date.getDate() +'-'+ (date.getMonth()+1) +'-'+ date.getFullYear(),
            'yValue':0
          }])
        } else {
          let graphData = [];
          let dateList = [];
          // Get datelist only
          data.ordersList.forEach( (orderData) => {
            dateList.push(orderData['orderDate']);
          })
          // Logic to get the unique dates
          function onlyUnique(value, index, self) {
            return self.indexOf(value) === index;
          }
          uniqueDateList = dateList.filter(onlyUnique);
          for (let i=0; i<uniqueDateList.length; i++) {
            orderValue = 0;
            data.ordersList.forEach( (orderData) => {
              if (orderData.orderDate == uniqueDateList[i]) {
                orderValue += Number(orderData.orderAmount);
              }
            })
            graphData.push({
              'xValue':uniqueDateList[i],
              'yValue':orderValue
            })
          }
  
          makeGraph(graphData);
        }
    }
  })
}

function makeGraph(graphlist, productName='Orders') {

  // Calculating labels from graphlist
  var iterator = 0;
  var data = [];
  var labels = [];

  graphlist.forEach((ele) => {
    data[iterator] = ele.yValue;
    labels[iterator] = ele.xValue;
    iterator++;
  })

  var data = {
    labels: labels,
    datasets: [{
      label: productName,
      backgroundColor: "#695877",
      data: data
    }]
  };

  var myBarChart = new Chart(ctx, {
    type: 'bar',
    data: data,
    options: {
      barValueSpacing: 20,
      scales: {
        yAxes: [{
          ticks: {
            min: 0,
          }
        }]
      }
    }
  });
}

// Enable and disable filter button
const filterBtn = document.getElementById('filterBtn');

function enableFilterBtn() {
  if (filterBtn.hasAttribute('disabled')) {
    filterBtn.removeAttribute('disabled');
  }
}
function disableFilterBtn() {
  if (!(filterBtn.hasAttribute('disabled'))) {
    filterBtn.setAttribute('disabled','');  
  }
}