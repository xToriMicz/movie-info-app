// Content script for TMDB movie pages - One Click Add
(function() {
    'use strict';
    
    // Check if we're on a TMDB movie page
    if (!window.location.href.includes('themoviedb.org/movie/')) {
        return;
    }
    
    // Extract movie ID from URL
    const movieIdMatch = window.location.href.match(/\/movie\/(\d+)/);
    if (!movieIdMatch) {
        return;
    }
    
    const movieId = movieIdMatch[1];
    
    // Create floating button for one-click add
    function createFloatingButton() {
        const button = document.createElement('div');
        button.id = 'movie-info-collector-btn';
        button.innerHTML = `
            <div class="collector-icon">🎬</div>
            <div class="collector-text">+ เพิ่มหนัง</div>
        `;
        
        // Click handler - direct import
        button.addEventListener('click', function() {
            importMovieDirectly(movieId);
        });
        
        document.body.appendChild(button);
    }
    
    // Show notification
    function showNotification(message, type = 'success') {
        // Remove existing notification
        const existingNotification = document.querySelector('.movie-info-notification');
        if (existingNotification) {
            existingNotification.remove();
        }
        
        const notification = document.createElement('div');
        notification.className = `movie-info-notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Auto hide after 3 seconds
        setTimeout(() => {
            notification.classList.add('hide');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }, 3000);
    }
    
    // Import movie directly (one-click)
    async function importMovieDirectly(movieId) {
        try {
            // Show loading notification
            showNotification('กำลังนำเข้าข้อมูล...', 'loading');
            
            // Get settings from storage with default values
            const settings = await new Promise(resolve => {
                chrome.storage.sync.get({
                    apiUrl: 'https://movie-info-app.onrender.com',
                    tmdbApiKey: '7ea748ccb9bded39260d8099c884c306'
                }, resolve);
            });
            
            if (!settings.apiUrl || settings.apiUrl === '') {
                showNotification('กรุณาตั้งค่า URL ของเว็บแอปใน Extension', 'error');
                // Open popup for settings
                chrome.runtime.sendMessage({action: 'openPopup'});
                return;
            }
            
            if (!settings.tmdbApiKey || settings.tmdbApiKey === '') {
                showNotification('กรุณาตั้งค่า TMDB API Key ใน Extension', 'error');
                // Open popup for settings
                chrome.runtime.sendMessage({action: 'openPopup'});
                return;
            }
            
            // Call web app API
            const response = await fetch(`${settings.apiUrl}/api/import/${movieId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                showNotification(`✅ เพิ่มหนังสำเร็จ: ${result.message}`);
            } else {
                showNotification(`❌ เกิดข้อผิดพลาด: ${result.message}`, 'error');
            }
            
        } catch (error) {
            console.error('Error importing movie:', error);
            if (error.message.includes('Failed to fetch')) {
                showNotification('❌ ไม่สามารถเชื่อมต่อกับเว็บแอปได้ กรุณาตรวจสอบ URL', 'error');
            } else {
                showNotification('❌ เกิดข้อผิดพลาดในการเชื่อมต่อ', 'error');
            }
        }
    }
    
    // Listen for messages from background script
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (message.action === 'importMovie') {
            importMovieDirectly(message.movieId);
        }
    });
    
    // Initialize when page is loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createFloatingButton);
    } else {
        createFloatingButton();
    }
    
})();
