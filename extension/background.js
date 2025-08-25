// Background script for Movie Info Collector
chrome.runtime.onInstalled.addListener(() => {
    console.log('Movie Info Collector Extension installed');
    
    // Set default settings
    chrome.storage.sync.set({
        apiUrl: 'https://movie-info-app.onrender.com',
        tmdbApiKey: '7ea748ccb9bded39260d8099c884c306'
    });
});

// Handle extension icon click
chrome.action.onClicked.addListener((tab) => {
    // Check if we're on a TMDB movie page
    if (tab.url && tab.url.includes('themoviedb.org/movie/')) {
        // Extract movie ID from URL
        const match = tab.url.match(/\/movie\/(\d+)/);
        if (match) {
            const movieId = match[1];
            // Send message to content script to import movie
            chrome.tabs.sendMessage(tab.id, {
                action: 'importMovie',
                movieId: movieId
            });
        }
    } else {
        // Open popup for settings
        chrome.action.setPopup({ popup: 'popup.html' });
    }
});

// Listen for messages from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'openPopup') {
        // Open popup for settings
        chrome.action.setPopup({ popup: 'popup.html' });
        // Trigger popup to open
        chrome.action.openPopup();
    }
});
