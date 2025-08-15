// Chart initialization
function initializeCharts() {
  const pathwayCtx = document.getElementById('pathwayChart')?.getContext('2d');
  if (pathwayCtx) {
    window._pathwayChart = new Chart(pathwayCtx, {
      type: 'doughnut',
      data: window.CHART_DATA.pathway,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 12,
              padding: 15,
              usePointStyle: true,
              font: { size: 11 }
            }
          }
        }
      }
    });
  }

  const levelCtx = document.getElementById('levelChart')?.getContext('2d');
  if (levelCtx) {
    window._levelChart = new Chart(levelCtx, {
      type: 'bar',
      data: window.CHART_DATA.level,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { 
          y: { 
            beginAtZero: true, 
            ticks: { stepSize: 1 }
          }
        }
      }
    });
  }
}