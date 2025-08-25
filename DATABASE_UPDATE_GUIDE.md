# 🗄️ Database Update Guide

## ภาพรวม

คู่มือนี้จะช่วยคุณอัปเดต Database Schema เพื่อรองรับระบบอัปเดตข้อมูลหนังเก่าจาก TMDB

## 📋 **สิ่งที่ต้องทำ**

### **1. อัปเดต Database Schema**

#### **วิธีที่ 1: อัปเดตแบบปลอดภัย (แนะนำ)**
ใช้ไฟล์ `update_database_schema.sql` เพื่ออัปเดต schema โดยไม่สูญเสียข้อมูล

```sql
-- ไปที่ Supabase Dashboard > SQL Editor
-- Copy และ paste เนื้อหาจากไฟล์ update_database_schema.sql
-- กด Run
```

#### **วิธีที่ 2: สร้างใหม่ทั้งหมด**
หากต้องการเริ่มต้นใหม่ ใช้ไฟล์ `setup_supabase_updated.sql`

```sql
-- ⚠️ วิธีนี้จะลบข้อมูลเก่าทั้งหมด
-- ไปที่ Supabase Dashboard > SQL Editor
-- Copy และ paste เนื้อหาจากไฟล์ setup_supabase_updated.sql
-- กด Run
```

### **2. ตรวจสอบการอัปเดต**

หลังจากรัน SQL แล้ว ให้ตรวจสอบว่า:

```sql
-- ตรวจสอบว่ามีคอลัมน์ updated_at
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'movies' AND column_name = 'updated_at';

-- ตรวจสอบ trigger
SELECT trigger_name, event_manipulation, action_statement
FROM information_schema.triggers 
WHERE event_object_table = 'movies';

-- ตรวจสอบ view
SELECT * FROM movie_update_stats;
```

## 🔧 **การเปลี่ยนแปลงใน Schema**

### **คอลัมน์ใหม่:**
- **`updated_at`**: TIMESTAMP WITH TIME ZONE - เวลาที่อัปเดตล่าสุด

### **Index ใหม่:**
- **`idx_movies_updated_at`**: เพิ่มประสิทธิภาพการค้นหาตาม updated_at

### **Trigger ใหม่:**
- **`update_movies_updated_at`**: อัปเดต `updated_at` อัตโนมัติเมื่อมีการแก้ไขข้อมูล

### **View ใหม่:**
- **`movie_update_stats`**: สถิติการอัปเดตแบบ Real-time

## 🧪 **ทดสอบระบบ**

### **1. ทดสอบการเชื่อมต่อ**
```bash
# ไปที่โฟลเดอร์โปรเจค
cd "C:\Users\PUMMY\Desktop\Save App"

# เปิดใช้งาน virtual environment
.venv\Scripts\activate

# ทดสอบระบบ
python test_update_system.py
```

### **2. ทดสอบการอัปเดต**
```bash
# แสดงสถิติ
python update_movies.py --stats

# อัปเดตหนังเดียว
python update_movies.py --single 575265

# อัปเดตหนังทั้งหมด
python update_movies.py --all
```

## 📊 **ตรวจสอบผลลัพธ์**

### **ผ่าน Supabase Dashboard:**
1. ไปที่ **Table Editor**
2. เลือกตาราง **movies**
3. ตรวจสอบคอลัมน์ **updated_at**

### **ผ่าน SQL Query:**
```sql
-- ดูข้อมูลตัวอย่าง
SELECT id, title, tmdb_id, created_at, updated_at 
FROM movies 
ORDER BY updated_at DESC 
LIMIT 5;

-- ดูสถิติการอัปเดต
SELECT * FROM movie_update_stats;
```

## 🚨 **ข้อควรระวัง**

### **ก่อนอัปเดต:**
1. **Backup ข้อมูล** - สำรองข้อมูลก่อนอัปเดต
2. **ตรวจสอบ Environment Variables** - ต้องมี TMDB_API_KEY, SUPABASE_URL, SUPABASE_ANON_KEY
3. **ทดสอบใน Development** - ทดสอบก่อนใช้ใน Production

### **หลังอัปเดต:**
1. **ตรวจสอบ Trigger** - ดูว่า trigger ทำงานถูกต้อง
2. **ทดสอบการอัปเดต** - ลองอัปเดตหนัง 1 เรื่อง
3. **ตรวจสอบ Performance** - ดูว่า index ทำงานดี

## 🔄 **การ Rollback (หากมีปัญหา)**

### **ลบ Trigger:**
```sql
DROP TRIGGER IF EXISTS update_movies_updated_at ON movies;
```

### **ลบ Function:**
```sql
DROP FUNCTION IF EXISTS update_updated_at_column();
```

### **ลบ Index:**
```sql
DROP INDEX IF EXISTS idx_movies_updated_at;
```

### **ลบ View:**
```sql
DROP VIEW IF EXISTS movie_update_stats;
```

### **ลบคอลัมน์ (ระวัง!):**
```sql
-- ⚠️ วิธีนี้จะลบข้อมูลในคอลัมน์ updated_at
ALTER TABLE movies DROP COLUMN IF EXISTS updated_at;
```

## 📞 **การแก้ไขปัญหา**

### **ปัญหา: "Column updated_at does not exist"**
**แก้ไข:** รันไฟล์ `update_database_schema.sql` อีกครั้ง

### **ปัญหา: "Trigger update_movies_updated_at already exists"**
**แก้ไข:** ไม่เป็นไร ระบบจะ replace trigger เก่า

### **ปัญหา: "Permission denied"**
**แก้ไข:** ตรวจสอบสิทธิ์ใน Supabase Dashboard

### **ปัญหา: "Function update_updated_at_column() does not exist"**
**แก้ไข:** รันไฟล์ `update_database_schema.sql` อีกครั้ง

## ✅ **ตรวจสอบความสำเร็จ**

### **สัญญาณที่แสดงว่าระบบทำงานถูกต้อง:**

1. **คอลัมน์ updated_at มีอยู่**
2. **Trigger ทำงานอัตโนมัติ**
3. **Index สร้างสำเร็จ**
4. **View แสดงสถิติได้**
5. **Python script ทำงานได้**

### **ทดสอบสุดท้าย:**
```bash
# ทดสอบระบบทั้งหมด
python test_update_system.py

# ควรเห็นผลลัพธ์:
# ✅ All tests passed! The update system is ready to use.
```

## 🎯 **ขั้นตอนต่อไป**

หลังจากอัปเดต Database สำเร็จแล้ว:

1. **Push ไป GitHub:**
   ```bash
   git add .
   git commit -m "Add movie update management system"
   git push origin main
   ```

2. **ทดสอบใน Production:**
   - ไปที่: https://movie-info-app.onrender.com/admin/updates
   - ทดสอบการอัปเดตหนัง

3. **ตั้งเวลาอัตโนมัติ:**
   - ใช้ Windows Task Scheduler
   - หรือ GitHub Actions
   - หรือ Cron Job

---

**หมายเหตุ:** หากมีปัญหาใดๆ ให้ตรวจสอบ logs และติดต่อผู้ดูแลระบบ 🛠️✨
