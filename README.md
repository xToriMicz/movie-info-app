# 🎬 Movie Info App - Supabase Integration

ระบบเก็บข้อมูลหนังจาก TMDB และบันทึกลง Supabase Database

## 📋 ข้อมูลที่เก็บ:
- **Title** - ชื่อหนัง
- **Year** - ปีที่เข้าฉาย  
- **Original Title** - ชื่อต้นฉบับ
- **Genres** - ประเภทหนัง (3 ประเภทแรก)
- **Trailer ID** - YouTube ID
- **Director** - ผู้กำกับ (1 คน)
- **Cast** - นักแสดง (3 คนแรก)

## 🚀 การติดตั้ง:

### 1. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 2. ตั้งค่า Environment Variables
เปลี่ยนชื่อไฟล์ `env_file.txt` เป็น `.env` และตรวจสอบ API keys:
```
TMDB_API_KEY=7ea748ccb9bded39260d8099c884c306
SUPABASE_URL=https://imewlphekrkaxkefunai.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
```

### 3. สร้างตารางใน Supabase
ไปที่ [Supabase Dashboard](https://supabase.com/dashboard/project/imewlphekrkaxkefunai) → SQL Editor และรันคำสั่งในไฟล์ `setup_supabase.sql`

## 🎯 การใช้งาน:

### รันระบบ
```bash
python supabase_movie_manager.py
```

### เมนูหลัก:
1. **Test Supabase connection** - ทดสอบการเชื่อมต่อ
2. **Import single movie** - นำเข้าหนังเรื่องเดียว
3. **Import multiple movies** - นำเข้าหนังหลายเรื่อง
4. **List all movies** - แสดงรายการหนังทั้งหมด
5. **Search movies** - ค้นหาหนัง
6. **Get movie details** - ดูรายละเอียดหนัง
7. **Exit** - ออกจากระบบ

## 📁 ไฟล์ในโปรเจค:
- `supabase_movie_manager.py` - ระบบหลัก
- `requirements.txt` - Dependencies
- `env_file.txt` - Environment variables (เปลี่ยนเป็น .env)
- `setup_supabase.sql` - SQL สำหรับสร้างตาราง
- `README.md` - คู่มือการใช้งาน

## 🔧 การแก้ไขปัญหา:

### ปัญหา: ไม่พบไฟล์ .env
```bash
# เปลี่ยนชื่อไฟล์
mv env_file.txt .env
```

### ปัญหา: Supabase connection failed
- ตรวจสอบ SUPABASE_URL และ SUPABASE_ANON_KEY
- ตรวจสอบว่าได้รัน SQL ใน Supabase แล้ว

### ปัญหา: TMDB API error
- ตรวจสอบ TMDB_API_KEY
- ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต

## 🎉 ตัวอย่างการใช้งาน:

```
🎬 Supabase Movie Manager
========================================
1. Test Supabase connection
2. Import single movie
3. Import multiple movies
4. List all movies in database
5. Search movies
6. Get movie details
7. Exit

Enter your choice (1-7): 1
✅ Supabase connection successful!
```

## 📊 ข้อมูลที่เก็บใน Supabase:
- ตาราง `movies` - ข้อมูลหนังทั้งหมด
- Indexes สำหรับการค้นหาที่รวดเร็ว
- Auto-update timestamp
- JSONB สำหรับข้อมูล cast

Happy Coding! 🎬✨
