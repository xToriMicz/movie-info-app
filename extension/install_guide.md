# 📋 คู่มือการติดตั้ง Chrome Extension

## 🎯 เป้าหมาย
สร้าง Chrome Extension สำหรับ **One Click Add** หนังจาก TMDB ไปยัง Movie Info App

## 📁 โครงสร้างไฟล์ที่สร้างแล้ว

```
extension/
├── manifest.json          ✅ Extension configuration
├── popup.html             ✅ Settings popup UI
├── popup.js               ✅ Popup functionality
├── content.js             ✅ One-click add script
├── content.css            ✅ Floating button styles
├── background.js          ✅ Background service worker
├── README.md              ✅ Documentation
└── install_guide.md       ✅ This file
```

## 🚀 ขั้นตอนการติดตั้ง

### 1. โหลด Extension ใน Chrome



1. **เปิด Chrome** และไปที่ `chrome://extensions/`
2. **เปิด Developer mode** (สวิตช์มุมขวาบน)
3. **คลิก "Load unpacked"**
4. **เลือกโฟลเดอร์** `extension` จากโปรเจคนี้
5. **Extension จะปรากฏ** ในรายการ

### 2. ตั้งค่า Extension

1. **คลิกไอคอน Extension** ในแถบเครื่องมือ
2. **ใส่ TMDB API Key:**
   - ไปที่ https://www.themoviedb.org/settings/api
   - สร้าง API Key ใหม่
   - คัดลอกและใส่ใน Extension
3. **ใส่ Web App URL:**
   - `http://127.0.0.1:5000` (localhost)
   - หรือ URL ของเซิร์ฟเวอร์ที่ deploy

## 🧪 การทดสอบ

### ทดสอบ One Click Add

1. **เปิดเว็บแอป** Movie Info App:
   ```bash
   python app.py
   ```

2. **เปิดหน้าหนังใน TMDB:**
   - ไปที่ https://www.themoviedb.org/movie/1022787
   - หรือหนังอื่นๆ ที่มี Movie ID

3. **ทดสอบการทำงาน:**
   - **วิธีที่ 1:** คลิกปุ่มลอย **"+ เพิ่มหนัง"** มุมขวาบน
   - **วิธีที่ 2:** คลิกไอคอน Extension ในแถบเครื่องมือ

4. **ตรวจสอบผลลัพธ์:**
   - ดู notification ที่แสดงผล
   - ตรวจสอบในเว็บแอปว่าข้อมูลถูกเพิ่มแล้ว

## 🔧 การแก้ไขปัญหา

### ปัญหาที่พบบ่อย

#### 1. Extension ไม่โหลด
```
Error: Could not load extension
```
**วิธีแก้:**
- ตรวจสอบไฟล์ `manifest.json` ว่าถูกต้อง
- ตรวจสอบว่าไฟล์ทั้งหมดอยู่ในโฟลเดอร์ `extension`
- ลบและโหลด Extension ใหม่

#### 2. ปุ่มลอยไม่แสดง
**วิธีแก้:**
- ตรวจสอบว่าเปิดหน้าหนังใน TMDB
- ตรวจสอบ URL ว่ามี `/movie/` หรือไม่
- เปิด Developer Tools และดู Console
- รีเฟรชหน้าเว็บ

#### 3. ไม่สามารถเพิ่มหนังได้
**วิธีแก้:**
- ตรวจสอบ TMDB API Key
- ตรวจสอบ URL ของเว็บแอป
- ตรวจสอบว่าเว็บแอปกำลังทำงานอยู่
- ดู Console ใน Developer Tools

#### 4. CORS Error
```
Access to fetch at 'http://127.0.0.1:5000' from origin 'https://www.themoviedb.org' has been blocked by CORS policy
```
**วิธีแก้:**
- ตรวจสอบว่าเว็บแอป Flask ตั้งค่า CORS ถูกต้อง
- หรือใช้ localhost แทน 127.0.0.1

## 📝 การปรับแต่ง

### เปลี่ยนสีปุ่มลอย
แก้ไขใน `content.css`:
```css
#movie-info-collector-btn {
    background: linear-gradient(135deg, #your-color 0%, #your-color 100%);
}
```

### เปลี่ยนข้อความปุ่ม
แก้ไขใน `content.js`:
```javascript
button.innerHTML = `
    <div class="collector-icon">🎬</div>
    <div class="collector-text">ข้อความที่ต้องการ</div>
`;
```

### เปลี่ยนตำแหน่งปุ่ม
แก้ไขใน `content.css`:
```css
#movie-info-collector-btn {
    top: 20px;    /* ระยะจากด้านบน */
    right: 20px;  /* ระยะจากด้านขวา */
}
```

## 🎉 เสร็จสิ้น!

หลังจากทำตามขั้นตอนทั้งหมด คุณจะมี Chrome Extension ที่สามารถ:

✅ **One Click Add** - เพิ่มหนังด้วยการคลิกเดียว  
✅ **Floating Button** - ปุ่มลอยบนหน้า TMDB  
✅ **Real-time Notification** - แจ้งเตือนผลการทำงาน  
✅ **Auto Settings** - บันทึกการตั้งค่าอัตโนมัติ  

**สนุกกับการใช้งาน! 🎬✨**
