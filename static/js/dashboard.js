document.addEventListener('DOMContentLoaded', () => {
  const chartEl = document.getElementById('occupancyChart');
  if (!chartEl || !window.dashboardConfig) return;
  const apiUrl = window.dashboardConfig.occupancyApiUrl;
  let chart;

  const render = (labels, data) => {
    if (chart) {
      chart.data.labels = labels;
      chart.data.datasets[0].data = data;
      chart.update();
      return;
    }
    chart = new Chart(chartEl, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Occupancy %',
          data,
          backgroundColor: 'rgba(13,110,253,.5)',
          borderColor: '#0d6efd',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        scales: { y: { beginAtZero: true, max: 100 } }
      }
    });
  };

  const fetchData = () => {
    fetch(apiUrl, { credentials: 'same-origin' })
      .then(r => r.json())
      .then(json => render(json.labels, json.data))
      .catch(() => {});
  };

  fetchData();
  setInterval(fetchData, 5000);
});
