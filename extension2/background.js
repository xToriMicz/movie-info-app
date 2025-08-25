// Background script สำหรับ extension2
// จัดการการทำงานเบื้องหลังของ extension

// เมื่อ extension ถูกติดตั้ง
chrome.runtime.onInstalled.addListener(() => {
    console.log('Movie Info to WordPress Helper Extension installed');
    
    // ตั้งค่าเริ่มต้น
    chrome.storage.sync.set({
        movieAppUrl: 'http://127.0.0.1:5000'
    });
});

// จัดการการเปลี่ยนแปลงของ tabs
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    // เมื่อหน้าเว็บโหลดเสร็จ
    if (changeInfo.status === 'complete') {
        // ตรวจสอบว่าเป็นหน้า Movie Info App หรือไม่
        if (tab.url && (tab.url.includes('movie-info-app') || 
                       tab.url.includes('127.0.0.1:5000') || 
                       tab.url.includes('localhost:5000'))) {
            
            // แสดง notification
            chrome.action.setBadgeText({ 
                text: '!', 
                tabId: tabId 
            });
            chrome.action.setBadgeBackgroundColor({ 
                color: '#28a745', 
                tabId: tabId 
            });
        } else {
            // ลบ notification
            chrome.action.setBadgeText({ 
                text: '', 
                tabId: tabId 
            });
        }
    }
});

// จัดการการคลิกที่ extension icon
chrome.action.onClicked.addListener((tab) => {
    // เปิด popup เมื่อคลิกที่ icon
    if (tab.url && (tab.url.includes('movie-info-app') || 
                   tab.url.includes('127.0.0.1:5000') || 
                   tab.url.includes('localhost:5000'))) {
        // แสดง popup
        chrome.action.setPopup({ 
            popup: 'popup.html' 
        });
    }
});

// ฟังก์ชันสำหรับการจัดการ error
function handleError(error) {
    console.error('Extension error:', error);
    
    // ส่ง error ไปยัง popup ถ้ามี
    chrome.runtime.sendMessage({
        action: 'error',
        error: error.message
    }).catch(() => {
        // ถ้า popup ไม่เปิดอยู่ ให้ ignore error
    });
}

// จัดการ error ที่เกิดขึ้น
chrome.runtime.onSuspend.addListener(() => {
    console.log('Extension suspended');
});

// ฟังก์ชันสำหรับการจัดการ storage
chrome.storage.onChanged.addListener((changes, namespace) => {
    if (namespace === 'sync') {
        console.log('Settings changed:', changes);
    }
});
