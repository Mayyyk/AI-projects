document.querySelector('.tasks button').addEventListener('click', () => {
  chrome.tabs.update({ url: 'https://tasks.com' });
});

document.querySelector('.youtube button').addEventListener('click', () => {
  chrome.tabs.update({ url: 'https://www.youtube.com?from=redirect' });
}); 