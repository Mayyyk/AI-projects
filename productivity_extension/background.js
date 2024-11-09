let allowedTabId = null;

chrome.webNavigation.onBeforeNavigate.addListener((details) => {
  // If this is our intentional redirect to YouTube, mark this tab as allowed
  if (details.url.includes("youtube.com") && details.url.includes("from=redirect")) {
    allowedTabId = details.tabId;
    return;
  }

  // If this is a YouTube navigation and not our redirect page
  if (details.url.includes("youtube.com") && !details.url.includes("redirect.html")) {
    // Only redirect if this tab isn't marked as allowed
    if (details.tabId !== allowedTabId) {
      chrome.tabs.update(details.tabId, {
        url: chrome.runtime.getURL("redirect.html")
      });
    }
  }
});

// Clean up the allowed tab when the tab is closed
chrome.tabs.onRemoved.addListener((tabId) => {
  if (tabId === allowedTabId) {
    allowedTabId = null;
  }
});