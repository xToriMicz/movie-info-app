// Global variables
let currentMovieId = null;
let currentMovieData = null;

// DOM elements
const statusEl = document.getElementById('status');
const movieInfoEl = document.getElementById('movieInfo');
const movieTitleEl = document.getElementById('movieTitle');
const movieDetailsEl = document.getElementById('movieDetails');
const importBtn = document.getElementById('importBtn');
const openWebBtn = document.getElementById('openWebBtn');
const loadingEl = document.getElementById('loading');
const errorEl = document.getElementById('error');
const successEl = document.getElementById('success');
const apiUrlEl = document.getElementById('apiUrl');
const tmdbApiKeyEl = document.getElementById('tmdbApiKey');

// Initialize popup
document.addEventListener('DOMContentLoaded', function() {
    loadSettings();
    checkCurrentTab();
    setupEventListeners();
});

// Load saved settings
function loadSettings() {
    chrome.storage.sync.get({
        apiUrl: 'https://movie-info-app.onrender.com',
        tmdbApiKey: '7ea748ccb9bded39260d8099c884c306'
    }, function(result) {
        apiUrlEl.value = result.apiUrl;
        tmdbApiKeyEl.value = result.tmdbApiKey;
    });
}

// Save settings
function saveSettings() {
    chrome.storage.sync.set({
        apiUrl: apiUrlEl.value,
        tmdbApiKey: tmdbApiKeyEl.value
    });
}

// Setup event listeners
function setupEventListeners() {
    importBtn.addEventListener('click', importMovie);
    openWebBtn.addEventListener('click', openWebApp);
    
    // Save settings on change
    apiUrlEl.addEventListener('change', saveSettings);
    tmdbApiKeyEl.addEventListener('change', saveSettings);
}

// Check current tab for TMDB movie page
function checkCurrentTab() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        const currentTab = tabs[0];
        const url = currentTab.url;
        
        if (url && url.includes('themoviedb.org/movie/')) {
            extractMovieId(url);
        } else {
            showStatus('กรุณาเปิดหน้าหนังใน TMDB', 'info');
        }
    });
}

// Extract movie ID from URL
function extractMovieId(url) {
    const match = url.match(/\/movie\/(\d+)/);
    if (match) {
        currentMovieId = match[1];
        fetchMovieData(currentMovieId);
    } else {
        showStatus('ไม่พบ Movie ID ใน URL', 'error');
    }
}

// Fetch movie data from TMDB
async function fetchMovieData(movieId) {
    try {
        showStatus('กำลังดึงข้อมูลหนัง...', 'loading');
        
        const apiKey = tmdbApiKeyEl.value;
        if (!apiKey) {
            showStatus('กรุณาใส่ TMDB API Key', 'error');
            return;
        }
        
        const url = `https://api.themoviedb.org/3/movie/${movieId}?api_key=${apiKey}&append_to_response=credits,videos`;
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        currentMovieData = data;
        displayMovieInfo(data);
        showStatus('พบข้อมูลหนังแล้ว', 'success');
        importBtn.style.display = 'block';
        
    } catch (error) {
        console.error('Error fetching movie data:', error);
        showStatus('เกิดข้อผิดพลาดในการดึงข้อมูล: ' + error.message, 'error');
    }
}

// Display movie information
function displayMovieInfo(movie) {
    movieTitleEl.textContent = movie.title;
    
    const details = [];
    if (movie.release_date) {
        details.push(`📅 ปี: ${movie.release_date.substring(0, 4)}`);
    }
    if (movie.vote_average) {
        details.push(`⭐ คะแนน: ${movie.vote_average}/10`);
    }
    if (movie.genres && movie.genres.length > 0) {
        const genres = movie.genres.slice(0, 3).map(g => g.name).join(', ');
        details.push(`🎭 ประเภท: ${genres}`);
    }
    if (movie.credits && movie.credits.cast && movie.credits.cast.length > 0) {
        const cast = movie.credits.cast.slice(0, 3).map(c => c.name).join(', ');
        details.push(`👥 นักแสดง: ${cast}`);
    }
    
    movieDetailsEl.innerHTML = details.map(detail => `<div>${detail}</div>`).join('');
    movieInfoEl.style.display = 'block';
}

// Import movie to web app
async function importMovie() {
    if (!currentMovieId || !currentMovieData) {
        showStatus('ไม่มีข้อมูลหนังที่จะนำเข้า', 'error');
        return;
    }
    
    try {
        showLoading(true);
        importBtn.disabled = true;
        
        const apiUrl = apiUrlEl.value;
        if (!apiUrl) {
            throw new Error('กรุณาใส่ URL ของเว็บแอป');
        }
        
        const importUrl = `${apiUrl}/api/import/${currentMovieId}`;
        const response = await fetch(importUrl);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess(`นำเข้าข้อมูลสำเร็จ: ${result.message}`);
            showStatus('นำเข้าข้อมูลสำเร็จแล้ว', 'success');
        } else {
            throw new Error(result.message || 'เกิดข้อผิดพลาดในการนำเข้า');
        }
        
    } catch (error) {
        console.error('Error importing movie:', error);
        showError('เกิดข้อผิดพลาด: ' + error.message);
        showStatus('เกิดข้อผิดพลาดในการนำเข้า', 'error');
    } finally {
        showLoading(false);
        importBtn.disabled = false;
    }
}

// Open web app
function openWebApp() {
    const apiUrl = apiUrlEl.value || 'http://127.0.0.1:5000';
    chrome.tabs.create({url: apiUrl});
}

// Show status message
function showStatus(message, type = 'info') {
    statusEl.textContent = message;
    
    // Update status styling based on type
    statusEl.className = 'status-content';
    if (type === 'error') {
        statusEl.style.color = '#ff6b6b';
    } else if (type === 'success') {
        statusEl.style.color = '#51cf66';
    } else if (type === 'loading') {
        statusEl.style.color = '#74c0fc';
    }
}

// Show loading state
function showLoading(show) {
    if (show) {
        loadingEl.style.display = 'block';
        importBtn.style.display = 'none';
    } else {
        loadingEl.style.display = 'none';
        importBtn.style.display = 'block';
    }
}

// Show error message
function showError(message) {
    errorEl.textContent = message;
    errorEl.style.display = 'block';
    successEl.style.display = 'none';
    
    setTimeout(() => {
        errorEl.style.display = 'none';
    }, 5000);
}

// Show success message
function showSuccess(message) {
    successEl.textContent = message;
    successEl.style.display = 'block';
    errorEl.style.display = 'none';
    
    setTimeout(() => {
        successEl.style.display = 'none';
    }, 5000);
}
