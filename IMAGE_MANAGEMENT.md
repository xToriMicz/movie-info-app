# 🖼️ Image Management Guide

## ภาพรวม

ระบบ Movie Info App มีการจัดการรูปภาพแบบอัตโนมัติเพื่อ:
- **ประหยัด Bandwidth**: ใช้ขนาดรูปเล็ก (w185 สำหรับ poster, w45 สำหรับ logo)
- **ป้องกันการถูกบล็อก**: ดาวน์โหลดรูปมาเก็บไว้ที่เซิร์ฟเวอร์
- **เพิ่มความเร็ว**: ใช้รูปที่เก็บไว้ในเครื่องแทนการเรียกจาก TMDB ทุกครั้ง

## 📁 โครงสร้างโฟลเดอร์

```
static/
├── images/
│   ├── posters/          # เก็บ poster หนัง
│   ├── providers/        # เก็บ logo ของ streaming providers
│   ├── no-poster.jpg     # รูป fallback สำหรับ poster
│   └── no-logo.png       # รูป fallback สำหรับ logo
```

## 🔧 การทำงาน

### 1. **Poster Management**
- **ขนาดที่ใช้**: w185 (185x278 pixels)
- **รูปแบบไฟล์**: JPG
- **การตั้งชื่อ**: `{tmdb_id}_{hash}.jpg`
- **ตัวอย่าง**: `575265_a1b2c3d4.jpg`

### 2. **Provider Logo Management**
- **ขนาดที่ใช้**: w45 (45x45 pixels)
- **รูปแบบไฟล์**: PNG
- **การตั้งชื่อ**: `provider_{provider_id}_{hash}.png`
- **ตัวอย่าง**: `provider_8_a1b2c3d4.png`

## 📊 ขนาดไฟล์ที่แนะนำ

### **Poster Images**
- **ขนาด**: 185x278 pixels
- **รูปแบบ**: JPEG
- **คุณภาพ**: 85-90%
- **ขนาดไฟล์**: ~15-30 KB

### **Provider Logos**
- **ขนาด**: 45x45 pixels
- **รูปแบบ**: PNG (with transparency)
- **คุณภาพ**: 100%
- **ขนาดไฟล์**: ~2-5 KB

## 🚀 การ Deploy

### **Local Development**
```bash
# รูปภาพจะถูกดาวน์โหลดอัตโนมัติเมื่อเพิ่มหนังใหม่
python app.py
```

### **Production (Render)**
```bash
# รูปภาพจะถูกดาวน์โหลดเมื่อมีการเรียกใช้
# ระบบจะตรวจสอบว่ามีไฟล์อยู่แล้วหรือไม่ก่อนดาวน์โหลด
```

## 🔄 การอัปเดต

### **อัปเดต Poster**
```python
# ระบบจะตรวจสอบและดาวน์โหลดใหม่หากไม่มีไฟล์
poster_url = download_and_save_poster(poster_path, tmdb_id)
```

### **อัปเดต Provider Logo**
```python
# ระบบจะตรวจสอบและดาวน์โหลดใหม่หากไม่มีไฟล์
logo_url = download_and_save_provider_logo(logo_path, provider_id)
```

## 🛡️ การป้องกัน

### **Rate Limiting**
- ระบบจะไม่ดาวน์โหลดรูปซ้ำหากมีไฟล์อยู่แล้ว
- ใช้ hash เพื่อตรวจสอบความเปลี่ยนแปลง

### **Error Handling**
- หากดาวน์โหลดไม่สำเร็จ จะใช้ URL ต้นฉบับจาก TMDB
- มี fallback images สำหรับกรณีที่ไม่มีรูป

### **Storage Management**
- รูปภาพถูก ignore ใน Git เพื่อไม่ให้ push ไฟล์ใหญ่
- ระบบจะสร้างโฟลเดอร์อัตโนมัติหากไม่มี

## 📈 ประสิทธิภาพ

### **Bandwidth Savings**
- **Poster**: จาก ~200KB (w500) เป็น ~25KB (w185) = ประหยัด 87.5%
- **Logo**: จาก ~15KB (w92) เป็น ~3KB (w45) = ประหยัด 80%

### **Loading Speed**
- **Local**: ~10-50ms
- **TMDB**: ~200-500ms
- **Improvement**: เร็วขึ้น 4-10 เท่า

## 🔧 การตั้งค่า

### **Environment Variables**
```bash
# ไม่ต้องตั้งค่าพิเศษ - ระบบทำงานอัตโนมัติ
```

### **Customization**
```python
# เปลี่ยนขนาดรูปใน utils.py
def get_poster_url(poster_path: str, size: str = 'w185') -> str:
    # เปลี่ยน w185 เป็นขนาดที่ต้องการ

def download_and_save_poster(poster_path: str, tmdb_id: int, size: str = 'w185') -> str:
    # เปลี่ยน w185 เป็นขนาดที่ต้องการ
```

## 🚨 ข้อควรระวัง

### **Storage Space**
- ตรวจสอบพื้นที่ว่างในเซิร์ฟเวอร์
- ลบรูปเก่าที่ไม่ได้ใช้เป็นระยะ

### **TMDB Rate Limits**
- TMDB มี rate limit สำหรับการดาวน์โหลดรูป
- ระบบจะใช้รูปที่มีอยู่แล้วก่อนดาวน์โหลดใหม่

### **File Permissions**
- ตรวจสอบสิทธิ์การเขียนไฟล์ในโฟลเดอร์ static/images/
- ระบบจะสร้างโฟลเดอร์อัตโนมัติหากมีสิทธิ์

## 📞 การแก้ไขปัญหา

### **รูปไม่แสดง**
1. ตรวจสอบสิทธิ์การเขียนไฟล์
2. ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
3. ดู error logs

### **รูปใหญ่เกินไป**
1. เปลี่ยนขนาดใน utils.py
2. ลบรูปเก่าและดาวน์โหลดใหม่

### **ดาวน์โหลดช้า**
1. ตรวจสอบการเชื่อมต่อ TMDB
2. ใช้รูปที่มีอยู่แล้วแทนการดาวน์โหลดใหม่
