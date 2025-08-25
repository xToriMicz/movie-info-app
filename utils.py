"""
Utility functions for Movie Info App
จัดการ poster images และ streaming providers
"""

import os
import requests
import hashlib
from pathlib import Path

def get_poster_url(poster_path: str, size: str = 'w185') -> str:
    """
    สร้าง URL สำหรับ poster image (ใช้ขนาดเล็กเพื่อประหยัด bandwidth)
    
    Args:
        poster_path: Path ของ poster จาก TMDB
        size: ขนาดของรูป (w92, w154, w185, w342, w500, w780, original)
    
    Returns:
        URL เต็มของ poster image
    """
    if not poster_path:
        return '/static/images/no-poster.jpg'
    
    base_url = 'https://image.tmdb.org/t/p'
    return f"{base_url}/{size}{poster_path}"

def download_and_save_poster(poster_path: str, tmdb_id: int, size: str = 'w185') -> str:
    """
    ดาวน์โหลด poster และบันทึกไว้ที่เซิร์ฟเวอร์
    
    Args:
        poster_path: Path ของ poster จาก TMDB
        tmdb_id: TMDB ID ของหนัง
        size: ขนาดของรูป
    
    Returns:
        Path ของไฟล์ที่บันทึกไว้ หรือ URL ต้นฉบับหากดาวน์โหลดไม่สำเร็จ
    """
    if not poster_path:
        return '/static/images/no-poster.jpg'
    
    try:
        # สร้างชื่อไฟล์จาก TMDB ID และ hash ของ poster path
        file_hash = hashlib.md5(poster_path.encode()).hexdigest()[:8]
        filename = f"{tmdb_id}_{file_hash}.jpg"
        
        # Path สำหรับบันทึกไฟล์
        static_dir = Path("static/images/posters")
        static_dir.mkdir(parents=True, exist_ok=True)
        file_path = static_dir / filename
        
        # ตรวจสอบว่ามีไฟล์อยู่แล้วหรือไม่
        if file_path.exists():
            return f'/static/images/posters/{filename}'
        
        # ดาวน์โหลดรูปภาพ
        tmdb_url = f"https://image.tmdb.org/t/p/{size}{poster_path}"
        response = requests.get(tmdb_url, timeout=30)
        response.raise_for_status()
        
        # บันทึกไฟล์
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Downloaded poster: {filename}")
        return f'/static/images/posters/{filename}'
        
    except Exception as e:
        print(f"Error downloading poster: {e}")
        # หากดาวน์โหลดไม่สำเร็จ ให้ใช้ URL ต้นฉบับ
        return get_poster_url(poster_path, size)

def download_and_save_provider_logo(logo_path: str, provider_id: int, size: str = 'w45') -> str:
    """
    ดาวน์โหลด provider logo และบันทึกไว้ที่เซิร์ฟเวอร์
    
    Args:
        logo_path: Path ของ logo จาก TMDB
        provider_id: ID ของ provider
        size: ขนาดของรูป
    
    Returns:
        Path ของไฟล์ที่บันทึกไว้ หรือ URL ต้นฉบับหากดาวน์โหลดไม่สำเร็จ
    """
    if not logo_path:
        return '/static/images/no-logo.png'
    
    try:
        # สร้างชื่อไฟล์
        file_hash = hashlib.md5(logo_path.encode()).hexdigest()[:8]
        filename = f"provider_{provider_id}_{file_hash}.png"
        
        # Path สำหรับบันทึกไฟล์
        static_dir = Path("static/images/providers")
        static_dir.mkdir(parents=True, exist_ok=True)
        file_path = static_dir / filename
        
        # ตรวจสอบว่ามีไฟล์อยู่แล้วหรือไม่
        if file_path.exists():
            return f'/static/images/providers/{filename}'
        
        # ดาวน์โหลดรูปภาพ
        tmdb_url = f"https://image.tmdb.org/t/p/{size}{logo_path}"
        response = requests.get(tmdb_url, timeout=30)
        response.raise_for_status()
        
        # บันทึกไฟล์
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Downloaded provider logo: {filename}")
        return f'/static/images/providers/{filename}'
        
    except Exception as e:
        print(f"Error downloading provider logo: {e}")
        # หากดาวน์โหลดไม่สำเร็จ ให้ใช้ URL ต้นฉบับ
        return get_provider_logo_url(logo_path, size)

def get_provider_logo_url(logo_path: str, size: str = 'w45') -> str:
    """
    สร้าง URL สำหรับ provider logo
    
    Args:
        logo_path: Path ของ logo จาก TMDB
        size: ขนาดของรูป (w45, w92, w154, w185, w300, w500)
    
    Returns:
        URL เต็มของ provider logo
    """
    if not logo_path:
        return '/static/images/no-logo.png'
    
    base_url = 'https://image.tmdb.org/t/p'
    return f"{base_url}/{size}{logo_path}"

def format_streaming_providers(providers_data: dict) -> dict:
    """
    จัดรูปแบบข้อมูล streaming providers สำหรับแสดงผล
    
    Args:
        providers_data: ข้อมูล providers จาก TMDB
    
    Returns:
        ข้อมูลที่จัดรูปแบบแล้ว
    """
    if not providers_data:
        return {
            'streaming': [],
            'rent': [],
            'buy': [],
            'has_providers': False
        }
    
    formatted = {
        'streaming': [],
        'rent': [],
        'buy': [],
        'has_providers': False
    }
    
    # จัดรูปแบบ streaming providers
    if 'streaming' in providers_data:
        formatted['streaming'] = [
            {
                'name': provider.get('provider_name', ''),
                'logo_url': download_and_save_provider_logo(
                    provider.get('logo_path', ''), 
                    provider.get('provider_id', 0)
                ),
                'id': provider.get('provider_id', '')
            }
            for provider in providers_data['streaming']
        ]
    
    # จัดรูปแบบ rent providers
    if 'rent' in providers_data:
        formatted['rent'] = [
            {
                'name': provider.get('provider_name', ''),
                'logo_url': download_and_save_provider_logo(
                    provider.get('logo_path', ''), 
                    provider.get('provider_id', 0)
                ),
                'id': provider.get('provider_id', '')
            }
            for provider in providers_data['rent']
        ]
    
    # จัดรูปแบบ buy providers
    if 'buy' in providers_data:
        formatted['buy'] = [
            {
                'name': provider.get('provider_name', ''),
                'logo_url': download_and_save_provider_logo(
                    provider.get('logo_path', ''), 
                    provider.get('provider_id', 0)
                ),
                'id': provider.get('provider_id', '')
            }
            for provider in providers_data['buy']
        ]
    
    # ตรวจสอบว่ามี providers หรือไม่
    formatted['has_providers'] = (
        len(formatted['streaming']) > 0 or 
        len(formatted['rent']) > 0 or 
        len(formatted['buy']) > 0
    )
    
    return formatted

def get_provider_type_name(provider_type: str) -> str:
    """
    แปลงชื่อประเภท provider เป็นภาษาไทย
    
    Args:
        provider_type: ประเภท provider (streaming, rent, buy)
    
    Returns:
        ชื่อภาษาไทย
    """
    type_names = {
        'streaming': 'สตรีมมิ่ง',
        'rent': 'เช่า',
        'buy': 'ซื้อ'
    }
    return type_names.get(provider_type, provider_type)

def truncate_text(text: str, max_length: int = 50) -> str:
    """
    ตัดข้อความให้สั้นลง
    
    Args:
        text: ข้อความที่ต้องการตัด
        max_length: ความยาวสูงสุด
    
    Returns:
        ข้อความที่ตัดแล้ว
    """
    if not text:
        return ''
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + '...'

def format_year(year: str) -> str:
    """
    จัดรูปแบบปี
    
    Args:
        year: ปีที่ต้องการจัดรูปแบบ
    
    Returns:
        ปีที่จัดรูปแบบแล้ว
    """
    if not year or year == 'None':
        return 'ไม่ระบุปี'
    return year

def format_genres(genres: list) -> str:
    """
    จัดรูปแบบประเภทหนัง
    
    Args:
        genres: รายการประเภทหนัง
    
    Returns:
        ข้อความประเภทหนัง
    """
    if not genres:
        return 'ไม่ระบุประเภท'
    
    return ', '.join(genres)

def format_cast(cast_data: list) -> str:
    """
    จัดรูปแบบนักแสดง
    
    Args:
        cast_data: ข้อมูลนักแสดง
    
    Returns:
        ข้อความนักแสดง
    """
    if not cast_data:
        return 'ไม่ระบุนักแสดง'
    
    cast_names = []
    for person in cast_data:
        name = person.get('name', '')
        character = person.get('character', '')
        if name:
            if character:
                cast_names.append(f"{name} ({character})")
            else:
                cast_names.append(name)
    
    return ', '.join(cast_names[:3])  # จำกัด 3 คน
