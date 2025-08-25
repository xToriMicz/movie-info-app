"""
Security Middleware for Movie Info App
ป้องกันการสแปมและความปลอดภัย
"""

import re
import hashlib
import time
from typing import Dict, List, Optional
from collections import defaultdict
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityMiddleware:
    def __init__(self):
        # Blacklist สำหรับ IP ที่ถูกแบน
        self.ip_blacklist = set()
        
        # Whitelist สำหรับ IP ที่เชื่อถือได้
        self.ip_whitelist = set()
        
        # Suspicious activity tracking
        self.suspicious_ips = defaultdict(int)
        
        # Failed attempts tracking
        self.failed_attempts = defaultdict(list)
        
        # Configuration
        self.max_failed_attempts = 5  # จำนวนครั้งที่ผิดพลาดสูงสุด
        self.ban_duration = 3600  # เวลาแบน (วินาที)
        self.suspicious_threshold = 10  # เกณฑ์การสงสัย
        
    def check_ip_security(self, ip_address: str) -> Dict:
        """ตรวจสอบความปลอดภัยของ IP address"""
        result = {
            'allowed': True,
            'reason': 'OK',
            'ban_remaining': 0
        }
        
        # ตรวจสอบ blacklist
        if ip_address in self.ip_blacklist:
            result['allowed'] = False
            result['reason'] = 'IP is blacklisted'
            return result
        
        # ตรวจสอบ whitelist (ข้ามการตรวจสอบอื่นๆ)
        if ip_address in self.ip_whitelist:
            return result
        
        # ตรวจสอบ failed attempts
        if ip_address in self.failed_attempts:
            failed_times = self.failed_attempts[ip_address]
            current_time = time.time()
            
            # ลบ failed attempts เก่า
            failed_times = [t for t in failed_times if current_time - t < self.ban_duration]
            self.failed_attempts[ip_address] = failed_times
            
            if len(failed_times) >= self.max_failed_attempts:
                result['allowed'] = False
                result['reason'] = 'Too many failed attempts'
                result['ban_remaining'] = self.ban_duration - (current_time - failed_times[0])
                return result
        
        # ตรวจสอบ suspicious activity
        if self.suspicious_ips[ip_address] >= self.suspicious_threshold:
            result['allowed'] = False
            result['reason'] = 'Suspicious activity detected'
            return result
        
        return result
    
    def record_failed_attempt(self, ip_address: str):
        """บันทึกการพยายามที่ล้มเหลว"""
        current_time = time.time()
        self.failed_attempts[ip_address].append(current_time)
        
        # ลบข้อมูลเก่า
        self.failed_attempts[ip_address] = [
            t for t in self.failed_attempts[ip_address]
            if current_time - t < self.ban_duration
        ]
        
        logger.warning(f"Failed attempt recorded for IP: {ip_address}")
    
    def record_suspicious_activity(self, ip_address: str, activity_type: str):
        """บันทึกกิจกรรมที่น่าสงสัย"""
        self.suspicious_ips[ip_address] += 1
        logger.warning(f"Suspicious activity detected: {activity_type} from IP: {ip_address}")
    
    def add_to_blacklist(self, ip_address: str):
        """เพิ่ม IP ลงใน blacklist"""
        self.ip_blacklist.add(ip_address)
        logger.warning(f"IP added to blacklist: {ip_address}")
    
    def add_to_whitelist(self, ip_address: str):
        """เพิ่ม IP ลงใน whitelist"""
        self.ip_whitelist.add(ip_address)
        logger.info(f"IP added to whitelist: {ip_address}")
    
    def remove_from_blacklist(self, ip_address: str):
        """ลบ IP ออกจาก blacklist"""
        self.ip_blacklist.discard(ip_address)
        logger.info(f"IP removed from blacklist: {ip_address}")

class InputValidator:
    """ตรวจสอบความถูกต้องของข้อมูล input"""
    
    @staticmethod
    def validate_movie_id(movie_id) -> bool:
        """ตรวจสอบ Movie ID"""
        try:
            movie_id_int = int(movie_id)
            return 1 <= movie_id_int <= 999999999
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """ทำความสะอาดข้อความ"""
        if not text:
            return ""
        
        # ลบ HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # ลบ special characters ที่อันตราย
        text = re.sub(r'[<>"\']', '', text)
        
        # จำกัดความยาว
        if len(text) > 1000:
            text = text[:1000]
        
        return text.strip()
    
    @staticmethod
    def validate_api_key(api_key: str, expected_key: str) -> bool:
        """ตรวจสอบ API key"""
        if not api_key or not expected_key:
            return False
        return api_key == expected_key
    
    @staticmethod
    def validate_user_agent(user_agent: str) -> bool:
        """ตรวจสอบ User-Agent"""
        if not user_agent:
            return False
        
        # ตรวจสอบ bot patterns
        bot_patterns = [
            r'bot', r'crawler', r'spider', r'scraper',
            r'curl', r'wget', r'python-requests',
            r'postman', r'insomnia'
        ]
        
        user_agent_lower = user_agent.lower()
        for pattern in bot_patterns:
            if re.search(pattern, user_agent_lower):
                return False
        
        return True

class RateLimiter:
    """จำกัดจำนวนการเรียก API"""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.limits = {
            'per_minute': 10,
            'per_hour': 100,
            'per_day': 1000
        }
    
    def check_rate_limit(self, ip_address: str) -> Dict:
        """ตรวจสอบ rate limit"""
        current_time = time.time()
        
        # ลบข้อมูลเก่า
        self.requests[ip_address] = [
            t for t in self.requests[ip_address]
            if current_time - t < 86400  # 24 ชั่วโมง
        ]
        
        # นับจำนวนการเรียก
        requests_last_minute = len([
            t for t in self.requests[ip_address]
            if current_time - t < 60
        ])
        
        requests_last_hour = len([
            t for t in self.requests[ip_address]
            if current_time - t < 3600
        ])
        
        requests_last_day = len(self.requests[ip_address])
        
        # ตรวจสอบ limit
        if requests_last_minute >= self.limits['per_minute']:
            return {
                'allowed': False,
                'reason': f"Rate limit exceeded: {requests_last_minute}/{self.limits['per_minute']} per minute",
                'retry_after': 60
            }
        
        if requests_last_hour >= self.limits['per_hour']:
            return {
                'allowed': False,
                'reason': f"Rate limit exceeded: {requests_last_hour}/{self.limits['per_hour']} per hour",
                'retry_after': 3600
            }
        
        if requests_last_day >= self.limits['per_day']:
            return {
                'allowed': False,
                'reason': f"Rate limit exceeded: {requests_last_day}/{self.limits['per_day']} per day",
                'retry_after': 86400
            }
        
        # เพิ่มการเรียกปัจจุบัน
        self.requests[ip_address].append(current_time)
        
        return {
            'allowed': True,
            'reason': 'OK',
            'limits': {
                'per_minute': f"{requests_last_minute}/{self.limits['per_minute']}",
                'per_hour': f"{requests_last_hour}/{self.limits['per_hour']}",
                'per_day': f"{requests_last_day}/{self.limits['per_day']}"
            }
        }

# Global instances
security_middleware = SecurityMiddleware()
input_validator = InputValidator()
rate_limiter = RateLimiter()
