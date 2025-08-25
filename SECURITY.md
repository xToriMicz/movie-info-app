# 🛡️ Security Protection Guide

## ภาพรวมการป้องกันความปลอดภัย

ระบบ Movie Info App มีการป้องกันหลายชั้นเพื่อป้องกันการสแปมและความปลอดภัย:

## 🔒 **ชั้นการป้องกัน**

### 1. **Rate Limiting (จำกัดจำนวนการเรียก API)**
- **ต่อนาที:** 10 ครั้ง
- **ต่อชั่วโมง:** 100 ครั้ง  
- **ต่อวัน:** 1000 ครั้ง
- **การทำงาน:** เก็บประวัติการเรียก API ตาม IP address

### 2. **Input Validation (ตรวจสอบข้อมูล Input)**
- **Movie ID:** ตรวจสอบว่าเป็นตัวเลขและอยู่ในช่วงที่ถูกต้อง (1-999,999,999)
- **Text Sanitization:** ลบ HTML tags และ special characters ที่อันตราย
- **Length Limits:** จำกัดความยาวข้อความไม่เกิน 1000 ตัวอักษร

### 3. **User-Agent Detection (ตรวจจับ Bot)**
- **Blocked Patterns:** bot, crawler, spider, scraper, curl, wget, python-requests, postman, insomnia
- **การทำงาน:** ตรวจสอบ User-Agent header และบล็อก bot ที่รู้จัก

### 4. **Duplicate Prevention (ป้องกันข้อมูลซ้ำ)**
- **ตรวจสอบ:** หนังที่มี TMDB ID เดียวกันจะไม่ถูกเพิ่มซ้ำ
- **Response:** ส่งข้อความแจ้งเตือนว่าหนังมีอยู่ในระบบแล้ว

### 5. **IP-based Security (ความปลอดภัยตาม IP)**
- **Blacklist:** IP ที่ถูกแบนจะไม่สามารถใช้งานได้
- **Whitelist:** IP ที่เชื่อถือได้จะข้ามการตรวจสอบ
- **Suspicious Activity:** ตรวจจับกิจกรรมที่น่าสงสัย
- **Failed Attempts:** บันทึกการพยายามที่ล้มเหลว

## 🚨 **การตอบสนองต่อการโจมตี**

### **Rate Limit Exceeded**
```json
{
  "success": false,
  "message": "Rate limit exceeded: 11/10 per minute",
  "error_type": "rate_limit"
}
```

### **Invalid Movie ID**
```json
{
  "success": false,
  "message": "Movie ID ไม่ถูกต้อง",
  "error_type": "invalid_id"
}
```

### **Bot Detection**
```json
{
  "success": false,
  "message": "Invalid request",
  "error_type": "invalid_agent"
}
```

### **Duplicate Movie**
```json
{
  "success": false,
  "message": "หนังนี้มีอยู่ในระบบแล้ว (ID: 575265)",
  "error_type": "duplicate"
}
```

## 🔧 **การตั้งค่า**

### **Environment Variables**
```bash
# Admin Panel
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password

# Rate Limiting (ในโค้ด)
MAX_REQUESTS_PER_MINUTE=10
MAX_REQUESTS_PER_HOUR=100
MAX_REQUESTS_PER_DAY=1000
```

### **Security Configuration**
```python
# Failed attempts
MAX_FAILED_ATTEMPTS = 5
BAN_DURATION = 3600  # 1 ชั่วโมง

# Suspicious activity
SUSPICIOUS_THRESHOLD = 10
```

## 📊 **Admin Panel**

### **การเข้าถึง**
- **URL:** `/admin`
- **Default Credentials:** admin / admin123
- **เปลี่ยนรหัสผ่าน:** ตั้งค่า environment variables

### **ฟีเจอร์**
- **Dashboard:** ดูสถิติการใช้งาน
- **Security Management:** จัดการ blacklist/whitelist
- **IP Monitoring:** ติดตาม IP ที่ใช้งาน
- **Rate Limit Stats:** ดูสถิติ rate limiting

## 🛠️ **การใช้งาน Admin Panel**

### **1. เข้าสู่ระบบ**
```
https://your-domain.com/admin
```

### **2. จัดการ Blacklist**
```bash
# เพิ่ม IP ลง blacklist
POST /admin/api/blacklist
{
  "ip": "192.168.1.100"
}

# ลบ IP ออกจาก blacklist
DELETE /admin/api/blacklist/192.168.1.100
```

### **3. จัดการ Whitelist**
```bash
# เพิ่ม IP ลง whitelist
POST /admin/api/whitelist
{
  "ip": "192.168.1.100"
}

# ลบ IP ออกจาก whitelist
DELETE /admin/api/whitelist/192.168.1.100
```

### **4. ล้างประวัติ**
```bash
# ล้าง suspicious activity
POST /admin/api/clear_suspicious/192.168.1.100

# ล้าง failed attempts
POST /admin/api/clear_failed_attempts/192.168.1.100
```

## 📈 **การติดตามและ Monitoring**

### **Logs**
- **Security Events:** บันทึกการโจมตีและกิจกรรมที่น่าสงสัย
- **Rate Limiting:** บันทึกการเกิน limit
- **Failed Attempts:** บันทึกการพยายามที่ล้มเหลว

### **Metrics**
- **Requests per IP:** จำนวนการเรียกต่อ IP
- **Blocked Requests:** จำนวนการเรียกที่ถูกบล็อก
- **Suspicious IPs:** IP ที่มีกิจกรรมที่น่าสงสัย

## 🔄 **การอัปเดตและบำรุงรักษา**

### **Regular Tasks**
1. **ตรวจสอบ Logs:** ดูการโจมตีและกิจกรรมที่น่าสงสัย
2. **อัปเดต Blacklist:** เพิ่ม IP ที่โจมตีลง blacklist
3. **ปรับ Rate Limits:** ปรับตามการใช้งานจริง
4. **เปลี่ยนรหัสผ่าน Admin:** เปลี่ยนเป็นระยะ

### **Emergency Response**
1. **เพิ่ม IP ลง Blacklist:** หากพบการโจมตี
2. **ลด Rate Limits:** หากระบบถูกโจมตีหนัก
3. **ตรวจสอบ Logs:** หาสาเหตุของการโจมตี
4. **แจ้งเตือน:** แจ้งผู้ดูแลระบบ

## 🚀 **การ Deploy**

### **Production Settings**
```python
# เพิ่มความปลอดภัยใน production
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secure-secret-key')
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
```

### **Environment Variables**
```bash
# Production
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_secure_password
SECRET_KEY=your-secure-secret-key
```

## 📞 **การติดต่อ**

หากพบปัญหาความปลอดภัย:
1. **ตรวจสอบ Logs:** ดู error logs
2. **ใช้ Admin Panel:** จัดการผ่าน admin interface
3. **ติดต่อผู้ดูแล:** แจ้งปัญหาที่พบ

---

**หมายเหตุ:** ระบบนี้ได้รับการออกแบบให้ป้องกันการโจมตีทั่วไป แต่ควรติดตามและอัปเดตอย่างสม่ำเสมอเพื่อความปลอดภัยสูงสุด
