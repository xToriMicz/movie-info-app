# 🔄 Movie Update Management Guide

## ภาพรวม

ระบบ Movie Update Management ช่วยให้คุณสามารถอัปเดตข้อมูลหนังเก่าที่มีอยู่ในฐานข้อมูลให้ตรงกับข้อมูลล่าสุดจาก TMDB ได้อย่างอัตโนมัติ

## 🎯 **ประโยชน์ของการอัปเดต**

### **ข้อมูลที่อัปเดตได้:**
- **Poster** - รูปภาพใหม่หรือคุณภาพดีขึ้น
- **Streaming Providers** - ข้อมูลสตรีมมิ่งล่าสุด
- **Cast & Crew** - นักแสดงและทีมงานที่อัปเดต
- **Trailer** - ลิงก์ trailer ใหม่
- **Genres** - ประเภทหนังที่อาจเปลี่ยนแปลง
- **Release Date** - วันที่เข้าฉายที่อาจเลื่อน

### **เหตุผลที่ต้องอัปเดต:**
- ข้อมูลใน TMDB เปลี่ยนแปลงตลอดเวลา
- เพิ่มข้อมูล streaming providers ใหม่
- อัปเดต poster ที่มีคุณภาพดีขึ้น
- แก้ไขข้อมูลที่ผิดพลาด

## 🛠️ **วิธีการอัปเดต**

### **1. ผ่าน Admin Panel (แนะนำ)**

#### **เข้าถึง Admin Panel:**
```
https://your-domain.com/admin
```

#### **ไปที่หน้า Updates:**
```
https://your-domain.com/admin/updates
```

#### **ตัวเลือกการอัปเดต:**

##### **📦 Update All Movies**
- อัปเดตหนังทั้งหมดที่ต้องการการอัปเดต
- ตั้งค่า Days Threshold (1, 3, 7, 14, 30 วัน)
- Force Update (อัปเดตทั้งหมดโดยไม่สนใจ threshold)

##### **🎬 Update Single Movie**
- อัปเดตหนัง 1 เรื่องตาม TMDB ID
- เหมาะสำหรับหนังที่ต้องการอัปเดตเฉพาะ

##### **📋 Update Multiple Movies**
- อัปเดตหลายหนังพร้อมกัน
- ใส่ TMDB IDs คั่นด้วยเครื่องหมายจุลภาค

### **2. ผ่าน Command Line Script**

#### **ติดตั้งและใช้งาน:**
```bash
# ไปที่โฟลเดอร์โปรเจค
cd "C:\Users\PUMMY\Desktop\Save App"

# เปิดใช้งาน virtual environment
.venv\Scripts\activate

# แสดงสถิติการอัปเดต
python update_movies.py --stats

# อัปเดตหนังทั้งหมด (7 วัน threshold)
python update_movies.py --all

# อัปเดตหนังทั้งหมด (force update)
python update_movies.py --all --force

# อัปเดตหนังทั้งหมด (3 วัน threshold)
python update_movies.py --all --days 3

# อัปเดตหนังเดียว
python update_movies.py --single 575265

# อัปเดตหลายหนัง
python update_movies.py --ids 575265 123456 789012
```

## 📊 **การตรวจสอบสถานะ**

### **สถิติที่แสดง:**
- **Total Movies** - จำนวนหนังทั้งหมดในฐานข้อมูล
- **Needs Update** - หนังที่ต้องการการอัปเดต
- **Recently Updated** - หนังที่อัปเดตล่าสุด
- **Update Percentage** - เปอร์เซ็นต์หนังที่อัปเดตล่าสุด

### **เกณฑ์การอัปเดต:**
- **Default**: 7 วัน (หนังที่อัปเดตเกิน 7 วันแล้ว)
- **Customizable**: 1, 3, 7, 14, 30 วัน
- **Force Update**: อัปเดตทั้งหมดโดยไม่สนใจเกณฑ์

## 🔧 **การตั้งค่า**

### **Environment Variables:**
```bash
# ต้องมี environment variables เหล่านี้
TMDB_API_KEY=your_tmdb_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

### **Rate Limiting:**
- **Delay**: 0.5 วินาที ระหว่างการอัปเดตแต่ละเรื่อง
- **Purpose**: ป้องกันการเกิน TMDB API rate limit
- **Configurable**: แก้ไขใน `update_manager.py`

## 📈 **การติดตามผล**

### **ผลลัพธ์ที่ได้:**
```json
{
  "success": true,
  "message": "Update completed: 15 updated, 2 failed, 8 skipped",
  "summary": {
    "total": 25,
    "updated": 15,
    "failed": 2,
    "skipped": 8
  }
}
```

### **ประเภทผลลัพธ์:**
- **Updated**: อัปเดตสำเร็จ
- **Failed**: อัปเดตไม่สำเร็จ (ดู error message)
- **Skipped**: ข้ามการอัปเดต (อัปเดตล่าสุดแล้ว)

## 🚨 **ข้อควรระวัง**

### **Rate Limiting:**
- TMDB มี rate limit สำหรับ API calls
- ระบบจะรอ 0.5 วินาที ระหว่างการอัปเดต
- หากมีหนังจำนวนมาก ควรอัปเดตทีละส่วน

### **Poster Downloads:**
- ระบบจะดาวน์โหลด poster ใหม่หากมีการเปลี่ยนแปลง
- ใช้พื้นที่จัดเก็บเพิ่มขึ้น
- ตรวจสอบพื้นที่ว่างในเซิร์ฟเวอร์

### **Error Handling:**
- หากหนังไม่พบใน TMDB จะข้ามการอัปเดต
- หากเกิด network error จะลองใหม่
- ดู error logs สำหรับรายละเอียด

## 🔄 **การตั้งเวลาอัตโนมัติ**

### **Windows Task Scheduler:**
```batch
# สร้างไฟล์ update_movies.bat
@echo off
cd "C:\Users\PUMMY\Desktop\Save App"
call .venv\Scripts\activate
python update_movies.py --all --days 7
```

### **Cron Job (Linux/Mac):**
```bash
# อัปเดตทุกวันเวลา 02:00
0 2 * * * cd /path/to/project && python update_movies.py --all --days 7
```

### **GitHub Actions:**
```yaml
# .github/workflows/update-movies.yml
name: Update Movies
on:
  schedule:
    - cron: '0 2 * * *'  # ทุกวันเวลา 02:00 UTC

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Update movies
        run: python update_movies.py --all --days 7
        env:
          TMDB_API_KEY: ${{ secrets.TMDB_API_KEY }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
```

## 📞 **การแก้ไขปัญหา**

### **ปัญหาที่พบบ่อย:**

#### **1. "Movie not found in database"**
- ตรวจสอบ TMDB ID ว่าถูกต้อง
- ตรวจสอบว่าหนังมีอยู่ในฐานข้อมูล

#### **2. "Failed to fetch data from TMDB"**
- ตรวจสอบ TMDB API Key
- ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
- ตรวจสอบ TMDB API status

#### **3. "Rate limit exceeded"**
- รอสักครู่แล้วลองใหม่
- ลดจำนวนหนังที่อัปเดตพร้อมกัน
- เพิ่ม delay ระหว่างการอัปเดต

#### **4. "Failed to update database"**
- ตรวจสอบ Supabase credentials
- ตรวจสอบการเชื่อมต่อฐานข้อมูล
- ดู error logs

### **การ Debug:**
```bash
# เปิด debug mode
python update_movies.py --single 575265 --debug

# ดู logs
tail -f logs/update.log
```

## 🎯 **คำแนะนำการใช้งาน**

### **สำหรับ Production:**
1. **ตั้งเวลาอัตโนมัติ** - อัปเดตทุกวันหรือทุกสัปดาห์
2. **ตรวจสอบ logs** - ดูผลการอัปเดตเป็นประจำ
3. **Backup ข้อมูล** - สำรองข้อมูลก่อนอัปเดตครั้งใหญ่
4. **Monitor Storage** - ตรวจสอบพื้นที่จัดเก็บ poster

### **สำหรับ Development:**
1. **ทดสอบกับหนังน้อย** - เริ่มจาก 1-2 เรื่อง
2. **ตรวจสอบผลลัพธ์** - ดูข้อมูลที่อัปเดต
3. **ปรับแต่ง threshold** - หาค่าที่เหมาะสม

### **การบำรุงรักษา:**
1. **ลบ poster เก่า** - ลบรูปที่ไม่ได้ใช้
2. **ตรวจสอบ error logs** - แก้ไขปัญหาที่เกิดขึ้น
3. **อัปเดต dependencies** - ใช้ library เวอร์ชันล่าสุด

---

**หมายเหตุ:** ระบบนี้ช่วยให้ข้อมูลหนังในฐานข้อมูลของคุณทันสมัยและตรงกับ TMDB เสมอ 🎬✨
