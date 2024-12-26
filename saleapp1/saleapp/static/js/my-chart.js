function drawRoute_count_Flight(labels, data){
    const ctx = document.getElementById('flightStats');

  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: labels,
      datasets: [{
        label: 'Count',
        data: data,
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}
function drawRoute_amount_Flight(labels, data){
    const ctx = document.getElementById('flightStats1');

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Tổng tiền',
        data: data,
        borderWidth: 1,
          backgroundColor: [
      'rgba(255, 99, 132, 0.2)',
      'rgba(255, 205, 86, 0.2)',
      'rgba(75, 192, 192, 0.2)',
      'rgba(54, 162, 235, 0.2)',
      'rgba(153, 102, 255, 0.2)',
      'rgba(201, 203, 207, 0.2)'
    ],
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}
function drawRoute_percent_amount(labels, data){
    const ctx = document.getElementById('flightStats2');

  new Chart(ctx, {
    type: 'polarArea',
    data: {
      labels: labels,
      datasets: [{
        label: 'Percent',
        data: data,
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}
function drawRoute_count_turn(labels, data){
    const ctx = document.getElementById('flightStats3');

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Percent',
        data: data,
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}

