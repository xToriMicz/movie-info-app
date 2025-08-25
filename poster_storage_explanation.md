# 🖼️ Poster Storage System

## ภาพรวม

ระบบจัดเก็บ poster ของหนังใน 2 แบบ:

### **1. ในฐานข้อมูล (Database)**
- **คอลัมน์:** `poster_path TEXT`
- **เก็บ:** Path ของ poster จาก TMDB (เช่น `/abc123.jpg`)
- **ใช้สำหรับ:** อ้างอิงและตรวจสอบการเปลี่ยนแปลง

### **2. ในไฟล์ระบบ (Local Storage)**
- **โฟลเดอร์:** `static/images/posters/`
- **เก็บ:** ไฟล์รูปภาพจริง
- **ใช้สำหรับ:** แสดงผลในเว็บไซต์

## 🔄 **การทำงานของระบบ**

### **เมื่อเพิ่มหนังใหม่:**
1. ดึง `poster_path` จาก TMDB API
2. บันทึก `poster_path` ลงฐานข้อมูล
3. ดาวน์โหลดไฟล์รูปภาพจาก TMDB
4. บันทึกไฟล์ใน `static/images/posters/`

### **เมื่ออัปเดตหนัง:**
1. ตรวจสอบ `poster_path` ใหม่จาก TMDB
2. เปรียบเทียบกับ `poster_path` เก่าในฐานข้อมูล
3. หากเปลี่ยน จะดาวน์โหลด poster ใหม่
4. อัปเดต `poster_path` ในฐานข้อมูล

## 📊 **โครงสร้างข้อมูล**

### **ในฐานข้อมูล:**
```sql
CREATE TABLE movies (
    -- ... other columns ...
    poster_path TEXT,  -- เก็บ path จาก TMDB
    -- ... other columns ...
);
```

### **ในไฟล์ระบบ:**
```
static/
└── images/
    ├── posters/
    │   ├── 575265.jpg     -- Mission: Impossible
    │   ├── 123456.jpg     -- อีกหนังหนึ่ง
    │   └── no-poster.jpg  -- รูป default
    └── providers/
        ├── netflix.png
        └── no-logo.png
```

## 🛠️ **ประโยชน์ของการจัดเก็บแบบนี้**

### **ข้อดี:**
1. **Performance:** โหลดรูปจาก local เร็วกว่า TMDB
2. **Reliability:** ไม่ขึ้นกับการเชื่อมต่อ TMDB
3. **Bandwidth:** ลดการใช้ bandwidth
4. **Caching:** รูปภาพถูก cache ใน browser
5. **Backup:** มีรูปภาพสำรอง

### **การจัดการ:**
1. **Automatic Download:** ดาวน์โหลดอัตโนมัติเมื่อเพิ่ม/อัปเดต
2. **File Naming:** ใช้ TMDB ID เป็นชื่อไฟล์
3. **Error Handling:** ใช้รูป default หากดาวน์โหลดไม่สำเร็จ
4. **Storage Management:** ลบรูปเก่าเมื่ออัปเดต

## 📝 **ตัวอย่างการใช้งาน**

### **เพิ่มหนังใหม่:**
```python
# 1. ดึงข้อมูลจาก TMDB
movie_data = get_movie_from_tmdb(575265)
poster_path = movie_data['poster_path']  # '/abc123.jpg'

# 2. บันทึกลงฐานข้อมูล
save_movie_to_database({
    'tmdb_id': 575265,
    'poster_path': poster_path,
    # ... other data
})

# 3. ดาวน์โหลดรูปภาพ
download_and_save_poster(poster_path, 575265)
# ผลลัพธ์: ไฟล์ static/images/posters/575265.jpg
```

### **อัปเดตหนัง:**
```python
# 1. ตรวจสอบ poster ใหม่
new_poster_path = get_movie_from_tmdb(575265)['poster_path']

# 2. เปรียบเทียบกับเก่า
if new_poster_path != old_poster_path:
    # 3. ดาวน์โหลด poster ใหม่
    download_and_save_poster(new_poster_path, 575265)
    
    # 4. อัปเดตฐานข้อมูล
    update_movie_poster(575265, new_poster_path)
```

## 🎯 **การตั้งค่า**

### **Environment Variables:**
```bash
# ไม่ต้องตั้งค่าเพิ่มเติม
# ระบบใช้ TMDB API key ที่มีอยู่แล้ว
TMDB_API_KEY=your_tmdb_api_key
```

### **โฟลเดอร์ที่ต้องมี:**
```bash
# สร้างโฟลเดอร์สำหรับเก็บรูปภาพ
mkdir -p static/images/posters
mkdir -p static/images/providers

# ไฟล์ default
touch static/images/posters/no-poster.jpg
touch static/images/providers/no-logo.png
```

## 📈 **การติดตาม**

### **ตรวจสอบในฐานข้อมูล:**
```sql
-- ดู poster paths ทั้งหมด
SELECT tmdb_id, title, poster_path 
FROM movies 
WHERE poster_path IS NOT NULL;

-- นับหนังที่มี poster
SELECT 
    COUNT(*) as total_movies,
    COUNT(poster_path) as movies_with_poster,
    COUNT(*) - COUNT(poster_path) as movies_without_poster
FROM movies;
```

### **ตรวจสอบไฟล์:**
```bash
# นับไฟล์ poster
ls static/images/posters/ | wc -l

# ดูขนาดโฟลเดอร์
du -sh static/images/posters/
```

## 🚨 **ข้อควรระวัง**

### **Storage Space:**
- Poster 1 ไฟล์ ≈ 100KB-500KB
- หนัง 1000 เรื่อง ≈ 100MB-500MB
- ตรวจสอบพื้นที่ว่างในเซิร์ฟเวอร์

### **File Management:**
- ระบบจะไม่ลบไฟล์เก่าอัตโนมัติ
- ควรลบไฟล์ที่ไม่ได้ใช้เป็นระยะ
- ใช้ TMDB ID เป็นชื่อไฟล์เพื่อป้องกันซ้ำ

### **Error Handling:**
- หากดาวน์โหลดไม่สำเร็จ จะใช้รูป default
- ตรวจสอบ logs หากมีปัญหา
- ลองดาวน์โหลดใหม่ในภายหลัง

## ✅ **สรุป**

ระบบจัดเก็บ poster **ทั้งในฐานข้อมูลและไฟล์ระบบ** เพื่อ:
- **ประสิทธิภาพสูงสุด** - โหลดเร็ว
- **ความน่าเชื่อถือ** - ไม่ขึ้นกับ TMDB
- **การจัดการที่ดี** - อัปเดตอัตโนมัติ
- **การสำรองข้อมูล** - มีรูปภาพสำรอง

**ตอนนี้ระบบพร้อมใช้งานแล้ว! 🎬✨**
