// Minimal client helpers for Printer Management System.
// (Toast/active-nav logic is inlined in base.html; add general helpers here.)

// Auto-dismiss any lingering .toast after 5s (defensive).
setTimeout(() => {
  document.querySelectorAll('.toast').forEach((t) => {
    t.classList.remove('show');
    setTimeout(() => t.remove(), 300);
  });
}, 5000);

// Confirm-on-navigation for destructive links marked data-confirm.
document.addEventListener('click', (e) => {
  const a = e.target.closest('[data-confirm]');
  if (a && !confirm(a.dataset.confirm)) e.preventDefault();
});
