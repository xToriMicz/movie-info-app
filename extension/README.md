# 🎬 Movie Info Collector Chrome Extension

**One Click Add** - เพิ่มหนังจาก TMDB ไปยัง Movie Info App ด้วยการคลิกเดียว!

## ✨ ฟีเจอร์

- **One Click Add** - คลิกเดียวเพิ่มหนังจาก TMDB
- **Floating Button** - ปุ่มลอยบนหน้า TMDB
- **Real-time Notification** - แจ้งเตือนผลการทำงาน
- **Auto Settings** - บันทึกการตั้งค่าอัตโนมัติ
- **Direct API Call** - เชื่อมต่อกับ Movie Info App โดยตรง

## 🚀 วิธีติดตั้ง

### 1. โหลด Extension ใน Chrome

1. เปิด Chrome และไปที่ `chrome://extensions/`
2. เปิด **Developer mode** (มุมขวาบน)
3. คลิก **Load unpacked**
4. เลือกโฟลเดอร์ `extension` จากโปรเจคนี้

### 2. ตั้งค่า Extension

1. คลิกไอคอน Extension ในแถบเครื่องมือ
2. ใส่ **TMDB API Key** ของคุณ
3. ใส่ **URL ของเว็บแอป** (เช่น `http://127.0.0.1:5000`)

## 📖 วิธีใช้งาน

### วิธีที่ 1: คลิกปุ่มลอย
1. เปิดหน้าหนังใน TMDB (เช่น https://www.themoviedb.org/movie/1022787)
2. จะเห็นปุ่ม **"+ เพิ่มหนัง"** ลอยอยู่มุมขวาบน
3. คลิกปุ่มเพื่อเพิ่มหนังทันที

### วิธีที่ 2: คลิกไอคอน Extension
1. เปิดหน้าหนังใน TMDB
2. คลิกไอคอน Extension ในแถบเครื่องมือ
3. ระบบจะเพิ่มหนังอัตโนมัติ

## ⚙️ การตั้งค่า

### TMDB API Key
- ไปที่ https://www.themoviedb.org/settings/api
- สร้าง API Key ใหม่
- ใส่ใน Extension

### Web App URL
- ใส่ URL ของ Movie Info App
- เช่น `http://127.0.0.1:5000` (localhost)
- หรือ URL ของเซิร์ฟเวอร์ที่ deploy

## 🎯 ข้อมูลที่นำเข้า

Extension จะนำเข้าข้อมูลต่อไปนี้:
- ✅ ชื่อหนัง (Title)
- ✅ ปีที่เข้าฉาย (Year)
- ✅ ชื่อต้นฉบับ (Original Title)
- ✅ ประเภท (Genres) - 3 ประเภทแรก
- ✅ ผู้กำกับ (Director) - 1 คน
- ✅ นักแสดง (Cast) - 3 คนแรก
- ✅ Trailer ID (YouTube)

## 🔧 การพัฒนา

### โครงสร้างไฟล์
```
extension/
├── manifest.json      # Extension configuration
├── popup.html         # Settings popup
├── popup.js           # Popup functionality
├── content.js         # Content script (one-click add)
├── content.css        # Content styles
└── background.js      # Background script
```

### การแก้ไข
1. แก้ไขไฟล์ที่ต้องการ
2. ไปที่ `chrome://extensions/`
3. คลิก **Reload** ที่ Extension
4. ทดสอบการทำงาน

## 🐛 การแก้ไขปัญหา

### Extension ไม่ทำงาน
- ตรวจสอบว่าเปิด Developer mode แล้ว
- ตรวจสอบ Console ใน Developer Tools
- ตรวจสอบการตั้งค่า API Key และ URL

### ไม่สามารถเพิ่มหนังได้
- ตรวจสอบ TMDB API Key
- ตรวจสอบ URL ของเว็บแอป
- ตรวจสอบว่าเว็บแอปกำลังทำงานอยู่

### ปุ่มลอยไม่แสดง
- ตรวจสอบว่าเปิดหน้าหนังใน TMDB
- ตรวจสอบ URL ว่ามี `/movie/` หรือไม่
- รีเฟรชหน้าเว็บ

## 📝 หมายเหตุ

- Extension ทำงานเฉพาะกับหน้า TMDB movie เท่านั้น
- ต้องมี Movie Info App ทำงานอยู่
- ข้อมูลจะถูกบันทึกลง Supabase database
- สามารถเพิ่มหนังซ้ำได้ (จะอัพเดทข้อมูล)

## 🎉 สนุกกับการใช้งาน!

**One Click Add** - เพิ่มหนังได้ง่ายๆ ด้วยการคลิกเดียว! 🎬✨
