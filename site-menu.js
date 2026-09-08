document.addEventListener('DOMContentLoaded', () => {
  const appLink = document.getElementById('openAppLink');
  if (appLink) {
    appLink.addEventListener('click', (event) => {
      event.preventDefault();
      window.location.href = 'converse.html';
    });
  }
});
