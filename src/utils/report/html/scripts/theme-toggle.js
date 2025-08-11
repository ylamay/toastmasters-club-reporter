// Theme system using CSS custom properties
const THEME_KEY = 'tm-theme';

const themeConfig = {
  light: {
    chart: {
      doughnut: ['#2563EB','#7C3AED','#059669','#F59E0B','#EF4444','#8B5CF6','#06B6D4','#84CC16'],
      bar: { background: '#059669', border: '#047857' }
    }
  },
  dark: {
    chart: {
      doughnut: ['#60A5FA','#A78BFA','#10B981','#FBBF24','#F87171','#C4B5FD','#22D3EE','#A3E635'],
      bar: { background: '#10B981', border: '#34D399' }
    }
  }
};

function applyTheme(themeName) {
  const config = themeConfig[themeName] || themeConfig.light;
  
  // Update data-theme attribute for CSS custom properties
  document.documentElement.setAttribute('data-theme', themeName);
  
  // Store preference
  localStorage.setItem(THEME_KEY, themeName);
  
  // Update toggle button
  const btn = document.getElementById('themeToggle');
  if (btn) btn.textContent = (themeName === 'dark') ? '☀️' : '🌙';
  
  // Update charts if available
  updateChartColors(config.chart);
}

function updateChartColors(chartConfig) {
  if (window._pathwayChart) {
    const ds = window._pathwayChart.data.datasets[0];
    ds.backgroundColor = chartConfig.doughnut.slice(0, ds.data.length);
    window._pathwayChart.update('none'); // No animation for smoother experience
  }
  
  if (window._levelChart) {
    const ds = window._levelChart.data.datasets[0];
    ds.backgroundColor = chartConfig.bar.background;
    ds.borderColor = chartConfig.bar.border;
    window._levelChart.update('none');
  }
}

// Initialize theme on load
function initTheme() {
  const savedTheme = localStorage.getItem(THEME_KEY) || 
    (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  applyTheme(savedTheme);
}

// Setup theme toggle
function setupThemeToggle() {
  const toggleBtn = document.getElementById('themeToggle');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
      const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
      applyTheme(nextTheme);
    });
  }
}

// Auto-initialize
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    setupThemeToggle();
  });
} else {
  initTheme();
  setupThemeToggle();
}
