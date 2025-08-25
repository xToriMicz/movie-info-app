# Movie Info to WordPress Helper

Chrome Extension สำหรับช่วยกรอกข้อมูลหนังจาก Movie Info App ลงใน WordPress Post Editor

## 🎯 ฟีเจอร์หลัก

- **ดึงข้อมูลหนัง** จากหน้า Movie Info App
- **คัดลอกข้อมูล** ไปยัง Clipboard
- **ช่วยกรอกข้อมูล** ลงในช่องต่างๆ ของ WordPress Post Editor
- **รองรับ Custom Fields** ของ WordPress
- **ไม่ต้องใช้ REST API** - ปลอดภัยและง่ายต่อการใช้งาน

## 📋 ข้อมูลที่รองรับ

### ข้อมูลพื้นฐาน
- ชื่อหนัง (Title)
- ชื่อต้นฉบับ (Original Title)
- ปีที่เข้าฉาย (Year)
- ผู้กำกับ (Director)
- TMDB ID

### ข้อมูลเพิ่มเติม
- ประเภทหนัง (Genres)
- นักแสดงหลัก (Cast) - 3 คนแรก
- โปสเตอร์ (Poster)
- Trailer YouTube ID
- Streaming Providers (สตรีมมิ่ง, เช่า, ซื้อ)

### Custom Fields ที่รองรับ
- **Trailer ID**: สำหรับช่อง Trailersx
- **IMDB**: สำหรับช่อง Imdb (ใช้ TMDB ID)
- **Featured Image**: สำหรับช่อง Featured Image
- **Player TH**: สำหรับช่อง PlayerxTH
- **Player SUB**: สำหรับช่อง PlayerxSUB
- **Collection**: สำหรับช่อง Collectionmovies

## 🚀 การติดตั้ง

### 1. โหลด Extension ใน Chrome

1. เปิด Chrome และไปที่ `chrome://extensions/`
2. เปิด "Developer mode" (มุมขวาบน)
3. คลิก "Load unpacked"
4. เลือกโฟลเดอร์ `extension2`

### 2. ตั้งค่า Movie Info App URL

- **Local**: `http://127.0.0.1:5000`
- **Production**: `https://movie-info-app.onrender.com`

## 📖 วิธีการใช้งาน

### 1. เปิดหน้า Movie Info App
- ไปที่หน้า Movie Info App
- เลือกหนังที่ต้องการนำข้อมูล

### 2. เปิด Extension
- คลิกที่ icon ของ extension ใน Chrome
- หรือใช้ปุ่ม "ดึงข้อมูลหนังจากหน้าเว็บปัจจุบัน"

### 3. ตั้งค่า Mapping (แนะนำ)
- ไปที่แท็บ "กำหนด Mapping"
- กำหนดว่าข้อมูลแต่ละช่องจะไปตรงกับช่องไหนใน WordPress
- คลิก "บันทึก Mapping"

### 4. ดึงข้อมูล
- คลิก "ดึงข้อมูลหนังจากหน้าเว็บปัจจุบัน"
- Extension จะดึงข้อมูลจากหน้าเว็บปัจจุบัน

### 5. คัดลอกข้อมูล
- คลิกปุ่มคัดลอกข้อมูลที่ต้องการ:
  - **ชื่อหนัง**: สำหรับช่อง Title
  - **เนื้อหาทั้งหมด**: สำหรับช่อง Content
  - **บทคัดย่อ**: สำหรับช่อง Excerpt
  - **Tags**: สำหรับช่อง Tags
  - **URL โปสเตอร์**: สำหรับ Featured Image
  - **YouTube Embed**: สำหรับแทรก Trailer
  - **ข้อมูลตาม Mapping**: สำหรับ Custom Fields

### 6. วางข้อมูลใน WordPress
- เปิดหน้า WordPress Post Editor
- วางข้อมูลลงในช่องที่ต้องการ (Ctrl+V)

## 🔧 การแก้ไขปัญหา

### ปัญหาการดึงข้อมูล

1. **ตรวจสอบหน้าเว็บ**
   - ต้องเป็นหน้า Movie Info App
   - ต้องมีข้อมูลหนังครบถ้วน

2. **ตรวจสอบ Network**
   - ต้องเชื่อมต่ออินเทอร์เน็ตได้
   - ไม่มี firewall บล็อก

### ปัญหาการคัดลอก

1. **ตรวจสอบ Clipboard**
   - ต้องอนุญาตให้ extension เข้าถึง clipboard
   - ลองใช้ Ctrl+C แทน

2. **ตรวจสอบข้อมูล**
   - ต้องดึงข้อมูลหนังสำเร็จก่อน
   - ข้อมูลต้องไม่เป็น null หรือ empty

### ปัญหา Mapping

1. **ตรวจสอบ Custom Fields**
   - ต้องตั้งค่า Mapping ให้ตรงกับชื่อช่องใน WordPress
   - ใช้ปุ่ม "รีเซ็ตเป็นค่าเริ่มต้น" ถ้าต้องการเริ่มใหม่

## 📝 ตัวอย่างข้อมูลที่คัดลอก

### ชื่อหนัง
```
Mission: Impossible - Dead Reckoning Part One
```

### ข้อมูลตาม Mapping
```
ใส่ชื่อ: Mission: Impossible - Dead Reckoning Part One
Director: Christopher McQuarrie
Released: 2023
ประเภท: Action, Adventure, Thriller
Cast: Tom Cruise, Hayley Atwell, Ving Rhames
Featured Image: https://movie-info-app.onrender.com/static/images/posters/575265_b4dc86da.jpg
Trailersx: avz06pdqSXY
Imdb: 575265
PlayerxTH: 
PlayerxSUB: 
สตรีมมิ่ง: Netflix
Collectionmovies: 
```

### เนื้อหาทั้งหมด
```html
<img src="https://movie-info-app.onrender.com/static/images/posters/575265_b4dc86da.jpg" alt="Mission: Impossible - Dead Reckoning Part One" style="max-width: 300px; height: auto; border-radius: 8px; margin-bottom: 20px;">

<h2>ข้อมูลหนัง</h2>
<ul>
<li><strong>ชื่อ:</strong> Mission: Impossible - Dead Reckoning Part One</li>
<li><strong>ปี:</strong> 2023</li>
<li><strong>ผู้กำกับ:</strong> Christopher McQuarrie</li>
<li><strong>ประเภท:</strong> Action, Adventure, Thriller</li>
<li><strong>นักแสดง:</strong> Tom Cruise, Hayley Atwell, Ving Rhames</li>
</ul>

<h2>Trailer</h2>
<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; margin-bottom: 20px;">
<iframe src="https://www.youtube.com/embed/avz06pdqSXY" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;" allowfullscreen></iframe>
</div>

<h2>สตรีมมิ่ง</h2>
<h3>สตรีมมิ่ง</h3>
<ul>
<li>Netflix</li>
</ul>

<h2>ลิงก์ภายนอก</h2>
<ul>
<li><a href="https://www.themoviedb.org/movie/575264" target="_blank">ดูใน TMDB</a></li>
<li><a href="https://www.youtube.com/watch?v=avz06pdqSXY" target="_blank">ดู Trailer บน YouTube</a></li>
</ul>
```

### บทคัดย่อ
```
Mission: Impossible - Dead Reckoning Part One (2023) - ผู้กำกับ: Christopher McQuarrie - ประเภท: Action, Adventure, Thriller - นักแสดง: Tom Cruise, Hayley Atwell, Ving Rhames
```

### Tags
```
Action, Adventure, Thriller, 2023, Christopher McQuarrie
```

### URL โปสเตอร์
```
https://movie-info-app.onrender.com/static/images/posters/575265_b4dc86da.jpg
```

### YouTube Embed
```
[embed]https://www.youtube.com/watch?v=avz06pdqSXY[/embed]
```

## 🔒 ความปลอดภัย

- **ไม่ใช้ REST API** - ไม่ต้องใส่ credentials
- **ไม่ส่งข้อมูล** ไปยังเซิร์ฟเวอร์อื่น
- **ใช้ Clipboard** - ข้อมูลอยู่ในเครื่องเท่านั้น
- **ไม่เก็บข้อมูล** ในรูปแบบ plain text

## 🛠️ การพัฒนา

### โครงสร้างไฟล์
```
extension2/
├── manifest.json      # การตั้งค่า extension
├── popup.html         # หน้า popup
├── popup.js          # JavaScript สำหรับ popup
├── content.js        # Content script
├── background.js     # Background script
├── content.css       # สไตล์สำหรับ content
└── README.md         # คู่มือการใช้งาน
```

### การแก้ไข
1. แก้ไขไฟล์ที่ต้องการ
2. ไปที่ `chrome://extensions/`
3. คลิก "Reload" ที่ extension
4. ทดสอบการทำงาน

## 📞 การสนับสนุน

หากพบปัญหาในการใช้งาน:
1. ตรวจสอบ Console ใน Developer Tools
2. ตรวจสอบการตั้งค่า Movie Info App URL
3. ตรวจสอบข้อมูลในหน้า Movie Info App
4. ตรวจสอบ Clipboard permissions
5. ตรวจสอบ Mapping settings

## 📄 License

MIT License - ใช้งานได้อย่างอิสระ
