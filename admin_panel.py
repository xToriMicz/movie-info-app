"""
Admin Panel for Movie Info App
จัดการความปลอดภัยและติดตามการใช้งาน
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from security_middleware import security_middleware, rate_limiter
from update_manager import MovieUpdateManager
import os
import json
import time
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin credentials (ควรย้ายไป environment variables)
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

def require_admin_auth(f):
    """Decorator สำหรับตรวจสอบ admin authentication"""
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """หน้า login สำหรับ admin"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            return render_template('admin/login.html', error='Invalid credentials')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    """ออกจากระบบ admin"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
@require_admin_auth
def dashboard():
    """หน้า dashboard หลัก"""
    # สถิติการใช้งาน
    stats = {
        'total_requests': len(rate_limiter.requests),
        'blacklisted_ips': len(security_middleware.ip_blacklist),
        'whitelisted_ips': len(security_middleware.ip_whitelist),
        'suspicious_ips': len(security_middleware.suspicious_ips)
    }
    
    # IP ที่ใช้งานล่าสุด
    recent_ips = []
    current_time = time.time()
    for ip, requests in rate_limiter.requests.items():
        if requests:
            recent_requests = [r for r in requests if current_time - r < 3600]  # 1 ชั่วโมง
            if recent_requests:
                recent_ips.append({
                    'ip': ip,
                    'requests_count': len(recent_requests),
                    'last_request': datetime.fromtimestamp(max(recent_requests))
                })
    
    recent_ips.sort(key=lambda x: x['last_request'], reverse=True)
    
    # สร้าง update manager
    try:
        update_manager = MovieUpdateManager()
        update_stats = update_manager.get_update_statistics()
    except Exception as e:
        update_stats = {}
    
    return render_template('admin/dashboard.html', stats=stats, recent_ips=recent_ips[:10], update_stats=update_stats)

@admin_bp.route('/security')
@require_admin_auth
def security():
    """หน้าจัดการความปลอดภัย"""
    blacklisted_ips = list(security_middleware.ip_blacklist)
    whitelisted_ips = list(security_middleware.ip_whitelist)
    suspicious_ips = [
        {'ip': ip, 'count': count} 
        for ip, count in security_middleware.suspicious_ips.items()
    ]
    
    return render_template('admin/security.html', 
                         blacklisted_ips=blacklisted_ips,
                         whitelisted_ips=whitelisted_ips,
                         suspicious_ips=suspicious_ips)

@admin_bp.route('/api/blacklist', methods=['POST'])
@require_admin_auth
def add_to_blacklist():
    """เพิ่ม IP ลงใน blacklist"""
    data = request.get_json()
    ip_address = data.get('ip')
    
    if not ip_address:
        return jsonify({'success': False, 'message': 'IP address required'})
    
    security_middleware.add_to_blacklist(ip_address)
    return jsonify({'success': True, 'message': f'IP {ip_address} added to blacklist'})

@admin_bp.route('/api/blacklist/<ip>', methods=['DELETE'])
@require_admin_auth
def remove_from_blacklist(ip):
    """ลบ IP ออกจาก blacklist"""
    security_middleware.remove_from_blacklist(ip)
    return jsonify({'success': True, 'message': f'IP {ip} removed from blacklist'})

@admin_bp.route('/api/whitelist', methods=['POST'])
@require_admin_auth
def add_to_whitelist():
    """เพิ่ม IP ลงใน whitelist"""
    data = request.get_json()
    ip_address = data.get('ip')
    
    if not ip_address:
        return jsonify({'success': False, 'message': 'IP address required'})
    
    security_middleware.add_to_whitelist(ip_address)
    return jsonify({'success': True, 'message': f'IP {ip_address} added to whitelist'})

@admin_bp.route('/api/whitelist/<ip>', methods=['DELETE'])
@require_admin_auth
def remove_from_whitelist(ip):
    """ลบ IP ออกจาก whitelist"""
    security_middleware.ip_whitelist.discard(ip)
    return jsonify({'success': True, 'message': f'IP {ip} removed from whitelist'})

@admin_bp.route('/api/stats')
@require_admin_auth
def get_stats():
    """ดึงสถิติการใช้งาน"""
    current_time = time.time()
    
    # สถิติ rate limiting
    rate_limit_stats = {}
    for ip, requests in rate_limiter.requests.items():
        requests_last_hour = [r for r in requests if current_time - r < 3600]
        if requests_last_hour:
            rate_limit_stats[ip] = {
                'requests_last_hour': len(requests_last_hour),
                'last_request': datetime.fromtimestamp(max(requests_last_hour))
            }
    
    # สถิติความปลอดภัย
    security_stats = {
        'blacklisted_ips': len(security_middleware.ip_blacklist),
        'whitelisted_ips': len(security_middleware.ip_whitelist),
        'suspicious_ips': len(security_middleware.suspicious_ips),
        'failed_attempts': len(security_middleware.failed_attempts)
    }
    
    return jsonify({
        'success': True,
        'rate_limit_stats': rate_limit_stats,
        'security_stats': security_stats
    })

@admin_bp.route('/api/clear_suspicious/<ip>', methods=['POST'])
@require_admin_auth
def clear_suspicious(ip):
    """ล้างประวัติ suspicious activity ของ IP"""
    if ip in security_middleware.suspicious_ips:
        del security_middleware.suspicious_ips[ip]
    return jsonify({'success': True, 'message': f'Suspicious activity cleared for {ip}'})

@admin_bp.route('/api/clear_failed_attempts/<ip>', methods=['POST'])
@require_admin_auth
def clear_failed_attempts(ip):
    """ล้างประวัติ failed attempts ของ IP"""
    if ip in security_middleware.failed_attempts:
        del security_middleware.failed_attempts[ip]
    return jsonify({'success': True, 'message': f'Failed attempts cleared for {ip}'})

@admin_bp.route('/updates')
@require_admin_auth
def updates():
    """หน้าจัดการการอัปเดตข้อมูล"""
    try:
        update_manager = MovieUpdateManager()
        stats = update_manager.get_update_statistics()
        return render_template('admin/updates.html', stats=stats)
    except Exception as e:
        return render_template('admin/updates.html', stats={}, error=str(e))

@admin_bp.route('/api/update/all', methods=['POST'])
@require_admin_auth
def update_all_movies():
    """API สำหรับอัปเดตหนังทั้งหมด"""
    try:
        force_update = request.json.get('force_update', False)
        days_threshold = request.json.get('days_threshold', 7)
        
        update_manager = MovieUpdateManager()
        result = update_manager.update_all_movies(force_update=force_update, days_threshold=days_threshold)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@admin_bp.route('/api/update/single', methods=['POST'])
@require_admin_auth
def update_single_movie():
    """API สำหรับอัปเดตหนังเดียว"""
    try:
        tmdb_id = request.json.get('tmdb_id')
        if not tmdb_id:
            return jsonify({'success': False, 'message': 'TMDB ID required'})
        
        update_manager = MovieUpdateManager()
        
        # หา movie ในฐานข้อมูล
        movie = update_manager.supabase.table('movies').select('id, title').eq('tmdb_id', tmdb_id).execute()
        
        if not movie.data:
            return jsonify({'success': False, 'message': 'Movie not found in database'})
        
        db_movie_id = movie.data[0]['id']
        result = update_manager.update_single_movie(db_movie_id, tmdb_id)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@admin_bp.route('/api/update/ids', methods=['POST'])
@require_admin_auth
def update_movies_by_ids():
    """API สำหรับอัปเดตหนังตาม IDs"""
    try:
        tmdb_ids = request.json.get('tmdb_ids', [])
        if not tmdb_ids:
            return jsonify({'success': False, 'message': 'TMDB IDs required'})
        
        update_manager = MovieUpdateManager()
        result = update_manager.update_movies_by_ids(tmdb_ids)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@admin_bp.route('/api/update/stats')
@require_admin_auth
def get_update_stats():
    """API สำหรับดึงสถิติการอัปเดต"""
    try:
        update_manager = MovieUpdateManager()
        stats = update_manager.get_update_statistics()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})
