// ตัวแปรสำหรับเก็บข้อมูล
let currentMovieData = null;
let settings = {};
let mappingSettings = {};

// โหลดการตั้งค่าเมื่อเปิด popup
document.addEventListener('DOMContentLoaded', function() {
    loadSettings();
    setupEventListeners();
    setupTabs();
});

// ตั้งค่า tabs
function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            
            // ลบ active class จากทุก tab
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // เพิ่ม active class ให้ tab ที่เลือก
            button.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });
}

// ตั้งค่า event listeners
function setupEventListeners() {
    document.getElementById('saveSettings').addEventListener('click', saveSettings);
    document.getElementById('searchMovies').addEventListener('click', searchMovies);
    document.getElementById('setupMapping').addEventListener('click', setupMapping);
    
    // เพิ่ม event listeners สำหรับปุ่มคัดลอก
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('copy-btn')) {
            const dataType = e.target.getAttribute('data-type');
            copyToClipboard(dataType);
        }
    });
    
    // เพิ่ม event listener สำหรับการค้นหาแบบ real-time
    document.getElementById('searchMovie').addEventListener('input', function(e) {
        const query = e.target.value.trim();
        if (query.length >= 2) {
            searchMoviesFromAPI(query);
        } else {
            document.getElementById('searchResults').style.display = 'none';
        }
    });
}

// โหลดการตั้งค่าจาก storage
async function loadSettings() {
    try {
        const result = await chrome.storage.sync.get(['movieAppUrl']);
        settings = result;
        
        // เติมข้อมูลในฟอร์ม
        document.getElementById('movieAppUrl').value = settings.movieAppUrl || '';
        
        showStatus('โหลดการตั้งค่าเรียบร้อย', 'success');
    } catch (error) {
        showStatus('เกิดข้อผิดพลาดในการโหลดการตั้งค่า: ' + error.message, 'error');
    }
}

// บันทึกการตั้งค่า
async function saveSettings() {
    try {
        const movieAppUrl = document.getElementById('movieAppUrl').value.trim();
        
        // ตรวจสอบข้อมูลที่จำเป็น
        if (!movieAppUrl) {
            showStatus('กรุณากรอก URL ของ Movie Info App', 'error');
            return;
        }
        
        // บันทึกการตั้งค่า
        await chrome.storage.sync.set({
            movieAppUrl: movieAppUrl
        });
        
        settings = { movieAppUrl };
        showStatus('บันทึกการตั้งค่าเรียบร้อย', 'success');
        
    } catch (error) {
        showStatus('เกิดข้อผิดพลาดในการบันทึก: ' + error.message, 'error');
    }
}

// ค้นหาหนังจาก API
async function searchMovies() {
    const query = document.getElementById('searchMovie').value.trim();
    
    if (!query) {
        showStatus('กรุณาพิมพ์ชื่อหนังที่ต้องการค้นหา', 'error');
        return;
    }
    
    if (!settings.movieAppUrl) {
        showStatus('กรุณาตั้งค่า URL ของ Movie Info App ก่อน', 'error');
        return;
    }
    
    await searchMoviesFromAPI(query);
}

// ค้นหาหนังจาก API (internal function)
async function searchMoviesFromAPI(query) {
    try {
        showStatus('กำลังค้นหาหนัง...', 'success');
        
        const response = await fetch(`${settings.movieAppUrl}/api/search?q=${encodeURIComponent(query)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success && data.movies) {
            displaySearchResults(data.movies);
            showStatus(`พบหนัง ${data.movies.length} เรื่อง`, 'success');
        } else {
            showStatus('ไม่พบหนังที่ค้นหา', 'error');
            document.getElementById('searchResults').style.display = 'none';
        }
        
    } catch (error) {
        showStatus('เกิดข้อผิดพลาดในการค้นหา: ' + error.message, 'error');
        document.getElementById('searchResults').style.display = 'none';
    }
}

// แสดงผลการค้นหา
function displaySearchResults(movies) {
    const searchResults = document.getElementById('searchResults');
    
    if (movies.length === 0) {
        searchResults.style.display = 'none';
        return;
    }
    
    let html = '';
    movies.forEach(movie => {
        html += `
            <div class="search-item" data-movie-id="${movie.id}">
                <div class="movie-title">${movie.title}</div>
                <div class="movie-year">${movie.formatted_year || 'ไม่ระบุปี'}</div>
            </div>
        `;
    });
    
    searchResults.innerHTML = html;
    searchResults.style.display = 'block';
    
    // เพิ่ม event listeners สำหรับการคลิกเลือกหนัง
    searchResults.querySelectorAll('.search-item').forEach(item => {
        item.addEventListener('click', function() {
            const movieId = this.getAttribute('data-movie-id');
            loadMovieDetails(movieId);
        });
    });
}

// โหลดรายละเอียดหนัง
async function loadMovieDetails(movieId) {
    try {
        showStatus('กำลังโหลดข้อมูลหนัง...', 'success');
        
        const response = await fetch(`${settings.movieAppUrl}/api/movie/${movieId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success && data.movie) {
            currentMovieData = data.movie;
            displayMovieInfo(currentMovieData);
            document.getElementById('copyButtons').style.display = 'block';
            document.getElementById('searchResults').style.display = 'none';
            showStatus('โหลดข้อมูลหนังเรียบร้อย', 'success');
        } else {
            showStatus('ไม่สามารถโหลดข้อมูลหนังได้', 'error');
        }
        
    } catch (error) {
        showStatus('เกิดข้อผิดพลาดในการโหลดข้อมูล: ' + error.message, 'error');
    }
}

// ตั้งค่า Mapping ที่หน้า WordPress
async function setupMapping() {
    try {
        // ดึงข้อมูลจาก active tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        // ตรวจสอบว่าเป็นหน้า WordPress หรือไม่
        if (!tab.url.includes('wp-admin') && !tab.url.includes('wordpress')) {
            showStatus('กรุณาเปิดหน้า WordPress Admin ก่อน', 'error');
            return;
        }
        
        // ส่ง message ไปยัง content script เพื่อตั้งค่า mapping
        const result = await chrome.tabs.sendMessage(tab.id, { 
            action: 'setupMapping',
            movieData: currentMovieData
        });
        
        if (result && result.success) {
            showStatus('ตั้งค่า Mapping เรียบร้อย', 'success');
        } else {
            showStatus('ไม่สามารถตั้งค่า Mapping ได้', 'error');
        }
        
    } catch (error) {
        showStatus('เกิดข้อผิดพลาด: ' + error.message, 'error');
    }
}

// แสดงข้อมูลหนัง
function displayMovieInfo(movieData) {
    const movieInfoDiv = document.getElementById('movieInfo');
    const moviePoster = document.getElementById('moviePoster');
    const movieDetails = document.getElementById('movieDetails');
    
    // แสดงโปสเตอร์
    if (movieData.poster_url) {
        moviePoster.src = movieData.poster_url;
        moviePoster.style.display = 'block';
    } else {
        moviePoster.style.display = 'none';
    }
    
    // แสดงรายละเอียด
    movieDetails.innerHTML = `
        <h6>${movieData.title}</h6>
        <p><strong>ปี:</strong> ${movieData.formatted_year || 'ไม่ระบุ'}</p>
        <p><strong>ผู้กำกับ:</strong> ${movieData.director || 'ไม่ระบุ'}</p>
        <p><strong>ประเภท:</strong> ${movieData.formatted_genres || 'ไม่ระบุ'}</p>
        <p><strong>นักแสดง:</strong> ${movieData.formatted_cast || 'ไม่ระบุ'}</p>
        ${movieData.trailer_id ? `<p><strong>Trailer:</strong> <a href="https://www.youtube.com/watch?v=${movieData.trailer_id}" target="_blank">ดูบน YouTube</a></p>` : ''}
    `;
    
    movieInfoDiv.style.display = 'block';
}

// คัดลอกข้อมูลไปยัง clipboard
async function copyToClipboard(dataType) {
    if (!currentMovieData) {
        showStatus('ไม่มีข้อมูลหนังที่จะคัดลอก', 'error');
        return;
    }
    
    try {
        let textToCopy = '';
        
        switch (dataType) {
            case 'title':
                textToCopy = currentMovieData.title;
                break;
                
            case 'content':
                textToCopy = createWordPressContent(currentMovieData);
                break;
                
            case 'excerpt':
                textToCopy = createExcerpt(currentMovieData);
                break;
                
            case 'tags':
                textToCopy = extractTags(currentMovieData).join(', ');
                break;
                
            case 'featured-image':
                textToCopy = currentMovieData.poster_url || '';
                break;
                
            case 'youtube-embed':
                if (currentMovieData.trailer_id) {
                    textToCopy = `[embed]https://www.youtube.com/watch?v=${currentMovieData.trailer_id}[/embed]`;
                } else {
                    textToCopy = '';
                }
                break;
                
            case 'custom-mapping':
                textToCopy = createCustomMappingContent(currentMovieData);
                break;
                
            default:
                showStatus('ประเภทข้อมูลไม่ถูกต้อง', 'error');
                return;
        }
        
        if (!textToCopy) {
            showStatus('ไม่มีข้อมูลสำหรับคัดลอก', 'error');
            return;
        }
        
        // คัดลอกไปยัง clipboard
        await navigator.clipboard.writeText(textToCopy);
        showStatus(`คัดลอก ${getDataTypeName(dataType)} เรียบร้อย`, 'success');
        
    } catch (error) {
        showStatus('เกิดข้อผิดพลาดในการคัดลอก: ' + error.message, 'error');
    }
}

// สร้างเนื้อหาตาม custom mapping
function createCustomMappingContent(movieData) {
    let content = '';
    
    // สร้างเนื้อหาตาม mapping ที่กำหนด
    if (movieData.title) {
        content += `ชื่อหนัง: ${movieData.title}\n`;
    }
    
    if (movieData.director) {
        content += `ผู้กำกับ: ${movieData.director}\n`;
    }
    
    if (movieData.formatted_year) {
        content += `ปี: ${movieData.formatted_year}\n`;
    }
    
    if (movieData.formatted_genres) {
        content += `ประเภท: ${movieData.formatted_genres}\n`;
    }
    
    if (movieData.formatted_cast) {
        content += `นักแสดง: ${movieData.formatted_cast}\n`;
    }
    
    if (movieData.poster_url) {
        content += `โปสเตอร์: ${movieData.poster_url}\n`;
    }
    
    if (movieData.trailer_id) {
        content += `Trailer ID: ${movieData.trailer_id}\n`;
    }
    
    if (movieData.tmdb_id) {
        content += `TMDB ID: ${movieData.tmdb_id}\n`;
    }
    
    return content.trim();
}

// สร้างเนื้อหา WordPress
function createWordPressContent(movieData) {
    let content = '';
    
    // เพิ่มโปสเตอร์
    if (movieData.poster_url) {
        content += `<img src="${movieData.poster_url}" alt="${movieData.title}" style="max-width: 300px; height: auto; border-radius: 8px; margin-bottom: 20px;">\n\n`;
    }
    
    // ข้อมูลพื้นฐาน
    content += `<h2>ข้อมูลหนัง</h2>\n`;
    content += `<ul>\n`;
    content += `<li><strong>ชื่อ:</strong> ${movieData.title}</li>\n`;
    
    if (movieData.original_title && movieData.original_title !== movieData.title) {
        content += `<li><strong>ชื่อต้นฉบับ:</strong> ${movieData.original_title}</li>\n`;
    }
    
    content += `<li><strong>ปี:</strong> ${movieData.formatted_year || 'ไม่ระบุ'}</li>\n`;
    content += `<li><strong>ผู้กำกับ:</strong> ${movieData.director || 'ไม่ระบุ'}</li>\n`;
    content += `<li><strong>ประเภท:</strong> ${movieData.formatted_genres || 'ไม่ระบุ'}</li>\n`;
    content += `<li><strong>นักแสดง:</strong> ${movieData.formatted_cast || 'ไม่ระบุ'}</li>\n`;
    content += `</ul>\n\n`;
    
    // Trailer
    if (movieData.trailer_id) {
        content += `<h2>Trailer</h2>\n`;
        content += `<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; margin-bottom: 20px;">\n`;
        content += `<iframe src="https://www.youtube.com/embed/${movieData.trailer_id}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;" allowfullscreen></iframe>\n`;
        content += `</div>\n\n`;
    }
    
    // Streaming Providers
    if (movieData.formatted_providers && movieData.formatted_providers.has_providers) {
        content += `<h2>สตรีมมิ่ง</h2>\n`;
        
        if (movieData.formatted_providers.streaming && movieData.formatted_providers.streaming.length > 0) {
            content += `<h3>สตรีมมิ่ง</h3>\n<ul>\n`;
            movieData.formatted_providers.streaming.forEach(provider => {
                content += `<li>${provider.provider_name}</li>\n`;
            });
            content += `</ul>\n`;
        }
        
        if (movieData.formatted_providers.rent && movieData.formatted_providers.rent.length > 0) {
            content += `<h3>เช่า</h3>\n<ul>\n`;
            movieData.formatted_providers.rent.forEach(provider => {
                content += `<li>${provider.provider_name}</li>\n`;
            });
            content += `</ul>\n`;
        }
        
        if (movieData.formatted_providers.buy && movieData.formatted_providers.buy.length > 0) {
            content += `<h3>ซื้อ</h3>\n<ul>\n`;
            movieData.formatted_providers.buy.forEach(provider => {
                content += `<li>${provider.provider_name}</li>\n`;
            });
            content += `</ul>\n`;
        }
    }
    
    // ลิงก์ภายนอก
    content += `<h2>ลิงก์ภายนอก</h2>\n`;
    content += `<ul>\n`;
    content += `<li><a href="https://www.themoviedb.org/movie/${movieData.tmdb_id}" target="_blank">ดูใน TMDB</a></li>\n`;
    if (movieData.trailer_id) {
        content += `<li><a href="https://www.youtube.com/watch?v=${movieData.trailer_id}" target="_blank">ดู Trailer บน YouTube</a></li>\n`;
    }
    content += `</ul>\n`;
    
    return content;
}

// สร้างบทคัดย่อ
function createExcerpt(movieData) {
    let excerpt = `${movieData.title}`;
    
    if (movieData.formatted_year) {
        excerpt += ` (${movieData.formatted_year})`;
    }
    
    if (movieData.director) {
        excerpt += ` - ผู้กำกับ: ${movieData.director}`;
    }
    
    if (movieData.formatted_genres) {
        excerpt += ` - ประเภท: ${movieData.formatted_genres}`;
    }
    
    if (movieData.formatted_cast) {
        excerpt += ` - นักแสดง: ${movieData.formatted_cast}`;
    }
    
    return excerpt;
}

// สร้าง tags สำหรับ WordPress
function extractTags(movieData) {
    const tags = [];
    
    // เพิ่มประเภทเป็น tags
    if (movieData.formatted_genres) {
        const genres = movieData.formatted_genres.split(', ');
        tags.push(...genres);
    }
    
    // เพิ่มปี
    if (movieData.formatted_year) {
        tags.push(movieData.formatted_year.toString());
    }
    
    // เพิ่มผู้กำกับ
    if (movieData.director) {
        tags.push(movieData.director);
    }
    
    return tags;
}

// แสดงชื่อประเภทข้อมูล
function getDataTypeName(dataType) {
    const names = {
        'title': 'ชื่อหนัง',
        'content': 'เนื้อหาทั้งหมด',
        'excerpt': 'บทคัดย่อ',
        'tags': 'Tags',
        'featured-image': 'URL โปสเตอร์',
        'youtube-embed': 'YouTube Embed',
        'custom-mapping': 'ข้อมูลตาม Mapping'
    };
    return names[dataType] || dataType;
}

// แสดงสถานะ
function showStatus(message, type) {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
    statusDiv.style.display = 'block';
    
    // ซ่อนสถานะหลังจาก 3 วินาที
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 3000);
}
