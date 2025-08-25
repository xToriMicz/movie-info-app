// Content script สำหรับ extension2
// จัดการการทำงานในหน้าเว็บ

// ฟังก์ชันสำหรับดึงข้อมูลหนังจากหน้า Movie Info App
function extractMovieInfo() {
    try {
        // ตรวจสอบว่าเป็นหน้า Movie Info App หรือไม่
        if (!window.location.href.includes('movie-info-app') && 
            !window.location.href.includes('127.0.0.1:5000') && 
            !window.location.href.includes('localhost:5000')) {
            return { success: false, error: 'ไม่ใช่หน้า Movie Info App' };
        }

        // ดึงข้อมูลจาก DOM
        const movieData = {
            title: extractText('.movie-title h1, h1, .title'),
            original_title: extractText('.original-title, .original-title span'),
            year: extractYear(),
            director: extractText('.director, .director span, [data-field="director"]'),
            genres: extractGenres(),
            cast: extractCast(),
            trailer_id: extractTrailerId(),
            tmdb_id: extractTmdbId(),
            poster_url: extractPosterUrl(),
            streaming_providers: extractStreamingProviders()
        };

        return { success: true, data: movieData };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// ฟังก์ชันสำหรับตั้งค่า mapping ที่หน้า WordPress
function setupWordPressMapping(movieData) {
    try {
        // ตรวจสอบว่าเป็นหน้า WordPress หรือไม่
        if (!window.location.href.includes('wp-admin') && 
            !window.location.href.includes('wordpress')) {
            return { success: false, error: 'ไม่ใช่หน้า WordPress Admin' };
        }

        // สร้าง modal สำหรับตั้งค่า mapping
        createMappingModal(movieData);

        return { success: true };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// สร้าง modal สำหรับตั้งค่า mapping
function createMappingModal(movieData) {
    // ลบ modal เดิมถ้ามี
    const existingModal = document.getElementById('movie-mapping-modal');
    if (existingModal) {
        existingModal.remove();
    }

    // สร้าง modal
    const modal = document.createElement('div');
    modal.id = 'movie-mapping-modal';
    modal.innerHTML = `
        <div class="movie-mapping-overlay">
            <div class="movie-mapping-modal">
                <div class="movie-mapping-header">
                    <h3>ตั้งค่า Mapping ข้อมูลหนัง</h3>
                    <button class="movie-mapping-close">&times;</button>
                </div>
                <div class="movie-mapping-content">
                    <div class="movie-info">
                        <h4>${movieData.title}</h4>
                        <p>ปี: ${movieData.year || 'ไม่ระบุ'}</p>
                        <p>ผู้กำกับ: ${movieData.director || 'ไม่ระบุ'}</p>
                    </div>
                    
                    <div class="mapping-settings">
                        <h5>เลือกช่องที่ต้องการให้ข้อมูลไปตรงกับ:</h5>
                        
                        <div class="mapping-field">
                            <label>ชื่อหนัง:</label>
                            <select id="map-title">
                                <option value="">-- เลือกช่อง --</option>
                                ${getWordPressFields()}
                            </select>
                        </div>
                        
                        <div class="mapping-field">
                            <label>ผู้กำกับ:</label>
                            <select id="map-director">
                                <option value="">-- เลือกช่อง --</option>
                                ${getWordPressFields()}
                            </select>
                        </div>
                        
                        <div class="mapping-field">
                            <label>ปี:</label>
                            <select id="map-year">
                                <option value="">-- เลือกช่อง --</option>
                                ${getWordPressFields()}
                            </select>
                        </div>
                        
                        <div class="mapping-field">
                            <label>ประเภท:</label>
                            <select id="map-genres">
                                <option value="">-- เลือกช่อง --</option>
                                ${getWordPressFields()}
                            </select>
                        </div>
                        
                        <div class="mapping-field">
                            <label>นักแสดง:</label>
                            <select id="map-cast">
                                <option value="">-- เลือกช่อง --</option>
                                ${getWordPressFields()}
                            </select>
                        </div>
                        
                        <div class="mapping-field">
                            <label>โปสเตอร์:</label>
                            <select id="map-poster">
                                <option value="">-- เลือกช่อง --</option>
                                ${getWordPressFields()}
                            </select>
                        </div>
                        
                        <div class="mapping-field">
                            <label>Trailer ID:</label>
                            <select id="map-trailer">
                                <option value="">-- เลือกช่อง --</option>
                                ${getWordPressFields()}
                            </select>
                        </div>
                    </div>
                </div>
                <div class="movie-mapping-footer">
                    <button class="btn btn-primary" id="save-mapping">บันทึก Mapping</button>
                    <button class="btn btn-secondary" id="cancel-mapping">ยกเลิก</button>
                </div>
            </div>
        </div>
    `;

    // เพิ่ม CSS
    addMappingStyles();

    // เพิ่ม event listeners
    modal.querySelector('.movie-mapping-close').addEventListener('click', () => modal.remove());
    modal.querySelector('#cancel-mapping').addEventListener('click', () => modal.remove());
    modal.querySelector('#save-mapping').addEventListener('click', () => saveMapping(movieData));

    // เพิ่ม modal ลงในหน้า
    document.body.appendChild(modal);
}

// เพิ่ม CSS สำหรับ modal
function addMappingStyles() {
    if (document.getElementById('movie-mapping-styles')) return;

    const styles = document.createElement('style');
    styles.id = 'movie-mapping-styles';
    styles.textContent = `
        .movie-mapping-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 999999;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .movie-mapping-modal {
            background: white;
            border-radius: 8px;
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .movie-mapping-header {
            padding: 20px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .movie-mapping-header h3 {
            margin: 0;
        }
        
        .movie-mapping-close {
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: #666;
        }
        
        .movie-mapping-content {
            padding: 20px;
        }
        
        .movie-info {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        .mapping-field {
            margin-bottom: 15px;
        }
        
        .mapping-field label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        .mapping-field select {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        
        .movie-mapping-footer {
            padding: 20px;
            border-top: 1px solid #eee;
            text-align: right;
        }
        
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-left: 10px;
        }
        
        .btn-primary {
            background: #007cba;
            color: white;
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
    `;

    document.head.appendChild(styles);
}

// ดึงรายการ fields จาก WordPress
function getWordPressFields() {
    const fields = [];
    
    // ดึง input fields
    document.querySelectorAll('input[type="text"], input[type="url"], textarea').forEach(input => {
        const name = input.name || input.id || input.placeholder || 'Input Field';
        const value = input.name || input.id || '';
        if (value) {
            fields.push(`<option value="${value}">${name}</option>`);
        }
    });
    
    // ดึง select fields
    document.querySelectorAll('select').forEach(select => {
        const name = select.name || select.id || 'Select Field';
        const value = select.name || select.id || '';
        if (value) {
            fields.push(`<option value="${value}">${name}</option>`);
        }
    });
    
    return fields.join('');
}

// บันทึก mapping
function saveMapping(movieData) {
    const mapping = {
        title: document.getElementById('map-title').value,
        director: document.getElementById('map-director').value,
        year: document.getElementById('map-year').value,
        genres: document.getElementById('map-genres').value,
        cast: document.getElementById('map-cast').value,
        poster: document.getElementById('map-poster').value,
        trailer: document.getElementById('map-trailer').value
    };

    // บันทึก mapping ลงใน localStorage
    localStorage.setItem('movie_mapping', JSON.stringify(mapping));
    
    // กรอกข้อมูลลงในช่องที่เลือก
    fillWordPressFields(movieData, mapping);
    
    // ปิด modal
    document.getElementById('movie-mapping-modal').remove();
    
    // แสดงข้อความสำเร็จ
    showNotification('ตั้งค่า Mapping และกรอกข้อมูลเรียบร้อย', 'success');
}

// กรอกข้อมูลลงในช่อง WordPress
function fillWordPressFields(movieData, mapping) {
    if (mapping.title && movieData.title) {
        fillField(mapping.title, movieData.title);
    }
    
    if (mapping.director && movieData.director) {
        fillField(mapping.director, movieData.director);
    }
    
    if (mapping.year && movieData.year) {
        fillField(mapping.year, movieData.year);
    }
    
    if (mapping.genres && movieData.genres) {
        fillField(mapping.genres, movieData.genres);
    }
    
    if (mapping.cast && movieData.cast) {
        fillField(mapping.cast, movieData.cast);
    }
    
    if (mapping.poster && movieData.poster_url) {
        fillField(mapping.poster, movieData.poster_url);
    }
    
    if (mapping.trailer && movieData.trailer_id) {
        fillField(mapping.trailer, movieData.trailer_id);
    }
}

// กรอกข้อมูลลงในช่อง
function fillField(fieldName, value) {
    // ค้นหาช่องตาม name หรือ id
    let field = document.querySelector(`[name="${fieldName}"]`) || 
                document.querySelector(`#${fieldName}`) ||
                document.querySelector(`[id*="${fieldName}"]`);
    
    if (field) {
        field.value = value;
        // เรียก event เพื่อให้ WordPress รู้ว่าข้อมูลเปลี่ยน
        field.dispatchEvent(new Event('input', { bubbles: true }));
        field.dispatchEvent(new Event('change', { bubbles: true }));
    }
}

// แสดงข้อความแจ้งเตือน
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        z-index: 1000000;
        font-family: Arial, sans-serif;
        font-size: 14px;
        ${type === 'success' ? 'background: #28a745;' : 'background: #dc3545;'}
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Helper functions สำหรับดึงข้อมูล
function extractText(selector) {
    const element = document.querySelector(selector);
    return element ? element.textContent.trim() : '';
}

function extractYear() {
    const yearElement = document.querySelector('.year, .release-year, [data-field="year"]');
    if (yearElement) {
        const yearText = yearElement.textContent.trim();
        const yearMatch = yearText.match(/\d{4}/);
        return yearMatch ? yearMatch[0] : '';
    }
    return '';
}

function extractGenres() {
    const genreElements = document.querySelectorAll('.genres .genre, .genre-tag, [data-field="genres"]');
    if (genreElements.length > 0) {
        return Array.from(genreElements).map(el => el.textContent.trim()).join(', ');
    }
    return '';
}

function extractCast() {
    const castElements = document.querySelectorAll('.cast .actor, .cast-member, [data-field="cast"]');
    if (castElements.length > 0) {
        return Array.from(castElements).slice(0, 3).map(el => el.textContent.trim()).join(', ');
    }
    return '';
}

function extractTrailerId() {
    const trailerElement = document.querySelector('.trailer, .youtube-trailer, [data-field="trailer"]');
    if (trailerElement) {
        const href = trailerElement.getAttribute('href') || trailerElement.textContent;
        const match = href.match(/[?&]v=([^&]+)/);
        return match ? match[1] : '';
    }
    return '';
}

function extractTmdbId() {
    const tmdbElement = document.querySelector('.tmdb-id, [data-field="tmdb_id"]');
    if (tmdbElement) {
        return tmdbElement.textContent.trim();
    }
    return '';
}

function extractPosterUrl() {
    const posterElement = document.querySelector('.movie-poster img, .poster img');
    if (posterElement) {
        return posterElement.src;
    }
    return '';
}

function extractStreamingProviders() {
    const providerElements = document.querySelectorAll('.streaming-provider, .provider');
    if (providerElements.length > 0) {
        return Array.from(providerElements).map(el => el.textContent.trim());
    }
    return [];
}

// รับ message จาก popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getMovieInfo') {
        const result = extractMovieInfo();
        sendResponse(result);
    } else if (request.action === 'setupMapping') {
        const result = setupWordPressMapping(request.movieData);
        sendResponse(result);
    }
});
