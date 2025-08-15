// Table expansion functionality
function setupTableExpansion() {
  const table = document.getElementById('membersTable');
  if (!table) return;
  
  table.querySelectorAll('.expand-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-target');
      const row = document.getElementById(id);
      if (!row) return;
      
      row.classList.toggle('open');
      const expanded = row.classList.contains('open');
      btn.setAttribute('aria-expanded', expanded);
      btn.textContent = expanded ? 'Hide' : 'Details';
    });
  });
}