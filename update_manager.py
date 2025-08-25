"""
Update Manager for Movie Info App
จัดการการอัปเดตข้อมูลหนังเก่าจาก TMDB
"""

import os
import requests
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv
from utils import download_and_save_poster, format_streaming_providers

# Load environment variables
load_dotenv()

class MovieUpdateManager:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.tmdb_api_key = os.getenv('TMDB_API_KEY')
        
        if not all([self.supabase_url, self.supabase_key, self.tmdb_api_key]):
            raise ValueError("Missing required environment variables")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        self.tmdb_base_url = "https://api.themoviedb.org/3"
    
    def get_movie_from_tmdb(self, movie_id: int) -> Dict:
        """ดึงข้อมูลหนังจาก TMDB API"""
        try:
            url = f"{self.tmdb_base_url}/movie/{movie_id}"
            params = {
                'api_key': self.tmdb_api_key,
                'append_to_response': 'credits,videos'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching movie data: {e}")
            return {}
    
    def get_streaming_providers(self, movie_id: int) -> Dict:
        """ดึงข้อมูล streaming providers จาก TMDB"""
        try:
            url = f"{self.tmdb_base_url}/movie/{movie_id}/watch/providers"
            params = {
                'api_key': self.tmdb_api_key
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            providers = {}
            
            # ดึง providers จากประเทศไทย (TH)
            th_providers = data.get('results', {}).get('TH', {})
            
            # ดึง streaming providers
            streaming = th_providers.get('flatrate', [])
            if streaming:
                providers['streaming'] = [
                    {
                        'provider_name': provider.get('provider_name', ''),
                        'logo_path': provider.get('logo_path', ''),
                        'provider_id': provider.get('provider_id', '')
                    }
                    for provider in streaming[:5]
                ]
            
            # ดึง rent providers
            rent = th_providers.get('rent', [])
            if rent:
                providers['rent'] = [
                    {
                        'provider_name': provider.get('provider_name', ''),
                        'logo_path': provider.get('logo_path', ''),
                        'provider_id': provider.get('provider_id', '')
                    }
                    for provider in rent[:5]
                ]
            
            # ดึง buy providers
            buy = th_providers.get('buy', [])
            if buy:
                providers['buy'] = [
                    {
                        'provider_name': provider.get('provider_name', ''),
                        'logo_path': provider.get('logo_path', ''),
                        'provider_id': provider.get('provider_id', '')
                    }
                    for provider in buy[:5]
                ]
            
            return providers
            
        except Exception as e:
            print(f"Error fetching streaming providers: {e}")
            return {}
    
    def extract_movie_data(self, movie_data: Dict) -> Dict:
        """ดึงเฉพาะข้อมูลที่ต้องการ"""
        if not movie_data:
            return {}
        
        # ดึงข้อมูลพื้นฐาน
        title = movie_data.get('title', '')
        original_title = movie_data.get('original_title', '')
        year = movie_data.get('release_date', '')[:4] if movie_data.get('release_date') else ''
        
        # ดึงประเภทหนัง 3 ประเภทแรก
        genres = [genre['name'] for genre in movie_data.get('genres', [])[:3]]
        
        # ดึงนักแสดง 3 คนแรก
        cast = []
        for person in movie_data.get('credits', {}).get('cast', [])[:3]:
            cast.append({
                'name': person['name'],
                'character': person.get('character', '')
            })
        
        # ดึงผู้กำกับ 1 คนแรก
        director = None
        for person in movie_data.get('credits', {}).get('crew', []):
            if person.get('job') == 'Director':
                director = person['name']
                break
        
        # ดึง YouTube ID จาก trailer
        trailer_id = None
        for video in movie_data.get('videos', {}).get('results', []):
            if video.get('type') == 'Trailer' and video.get('site') == 'YouTube':
                trailer_id = video['key']
                break
        
        # ดึง poster path
        poster_path = movie_data.get('poster_path', '')
        
        # ดึง streaming providers
        streaming_providers = self.get_streaming_providers(movie_data.get('id'))
        
        return {
            'tmdb_id': movie_data.get('id'),
            'title': title,
            'year': year,
            'original_title': original_title,
            'genres': genres,
            'trailer_id': trailer_id,
            'director': director,
            'cast_data': cast,
            'poster_path': poster_path,
            'streaming_providers': streaming_providers
        }
    
    def get_all_movies_from_database(self) -> List[Dict]:
        """ดึงรายการหนังทั้งหมดจากฐานข้อมูล"""
        try:
            movies = self.supabase.table('movies').select('id, tmdb_id, title, updated_at').execute()
            return movies.data
        except Exception as e:
            print(f"Error getting movies from database: {e}")
            return []
    
    def update_movie_data(self, db_movie_id: int, movie_data: Dict) -> bool:
        """อัปเดตข้อมูลหนังในฐานข้อมูล"""
        try:
            movie_record = {
                'title': movie_data['title'],
                'original_title': movie_data['original_title'],
                'year': movie_data['year'],
                'genres': movie_data['genres'],
                'trailer_id': movie_data['trailer_id'],
                'director': movie_data['director'],
                'cast_data': movie_data['cast_data'],
                'poster_path': movie_data.get('poster_path', ''),
                'streaming_providers': movie_data.get('streaming_providers', {}),
                'updated_at': datetime.now().isoformat()
            }
            
            self.supabase.table('movies').update(movie_record).eq('id', db_movie_id).execute()
            return True
            
        except Exception as e:
            print(f"Error updating movie data: {e}")
            return False
    
    def check_movie_needs_update(self, movie: Dict, days_threshold: int = 7) -> bool:
        """ตรวจสอบว่าหนังต้องการการอัปเดตหรือไม่"""
        try:
            updated_at = movie.get('updated_at')
            if not updated_at:
                return True
            
            # แปลง string เป็น datetime
            if isinstance(updated_at, str):
                updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            
            # ตรวจสอบว่าผ่านไปกี่วันแล้ว
            days_since_update = (datetime.now() - updated_at).days
            return days_since_update >= days_threshold
            
        except Exception as e:
            print(f"Error checking update status: {e}")
            return True
    
    def update_single_movie(self, db_movie_id: int, tmdb_id: int) -> Dict:
        """อัปเดตหนัง 1 เรื่อง"""
        try:
            print(f"Updating movie TMDB ID: {tmdb_id}")
            
            # ดึงข้อมูลจาก TMDB
            movie_data = self.get_movie_from_tmdb(tmdb_id)
            if not movie_data:
                return {'success': False, 'message': 'Failed to fetch data from TMDB'}
            
            # ดึงเฉพาะข้อมูลที่ต้องการ
            simple_data = self.extract_movie_data(movie_data)
            
            # อัปเดตในฐานข้อมูล
            success = self.update_movie_data(db_movie_id, simple_data)
            if not success:
                return {'success': False, 'message': 'Failed to update database'}
            
            # ดาวน์โหลด poster ใหม่ (ถ้ามี)
            if simple_data.get('poster_path'):
                download_and_save_poster(simple_data['poster_path'], tmdb_id)
            
            return {
                'success': True,
                'message': f'Successfully updated: {simple_data["title"]}',
                'data': simple_data
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error updating movie: {str(e)}'}
    
    def update_all_movies(self, force_update: bool = False, days_threshold: int = 7) -> Dict:
        """อัปเดตหนังทั้งหมดที่ต้องการการอัปเดต"""
        try:
            # ดึงรายการหนังทั้งหมด
            movies = self.get_all_movies_from_database()
            if not movies:
                return {'success': False, 'message': 'No movies found in database'}
            
            updated_count = 0
            failed_count = 0
            skipped_count = 0
            results = []
            
            print(f"Found {len(movies)} movies in database")
            
            for movie in movies:
                db_movie_id = movie['id']
                tmdb_id = movie['tmdb_id']
                title = movie['title']
                
                # ตรวจสอบว่าต้องการอัปเดตหรือไม่
                if not force_update and not self.check_movie_needs_update(movie, days_threshold):
                    print(f"Skipping {title} (recently updated)")
                    skipped_count += 1
                    continue
                
                # อัปเดตหนัง
                result = self.update_single_movie(db_movie_id, tmdb_id)
                results.append({
                    'tmdb_id': tmdb_id,
                    'title': title,
                    'result': result
                })
                
                if result['success']:
                    updated_count += 1
                    print(f"✅ Updated: {title}")
                else:
                    failed_count += 1
                    print(f"❌ Failed: {title} - {result['message']}")
                
                # รอสักครู่เพื่อไม่ให้เกิน rate limit
                time.sleep(0.5)
            
            return {
                'success': True,
                'message': f'Update completed: {updated_count} updated, {failed_count} failed, {skipped_count} skipped',
                'summary': {
                    'total': len(movies),
                    'updated': updated_count,
                    'failed': failed_count,
                    'skipped': skipped_count
                },
                'results': results
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error updating movies: {str(e)}'}
    
    def update_movies_by_ids(self, tmdb_ids: List[int]) -> Dict:
        """อัปเดตหนังตาม TMDB IDs ที่ระบุ"""
        try:
            updated_count = 0
            failed_count = 0
            results = []
            
            for tmdb_id in tmdb_ids:
                # หา movie ในฐานข้อมูล
                movie = self.supabase.table('movies').select('id, title').eq('tmdb_id', tmdb_id).execute()
                
                if not movie.data:
                    failed_count += 1
                    results.append({
                        'tmdb_id': tmdb_id,
                        'result': {'success': False, 'message': 'Movie not found in database'}
                    })
                    continue
                
                db_movie_id = movie.data[0]['id']
                title = movie.data[0]['title']
                
                # อัปเดตหนัง
                result = self.update_single_movie(db_movie_id, tmdb_id)
                results.append({
                    'tmdb_id': tmdb_id,
                    'title': title,
                    'result': result
                })
                
                if result['success']:
                    updated_count += 1
                    print(f"✅ Updated: {title}")
                else:
                    failed_count += 1
                    print(f"❌ Failed: {title} - {result['message']}")
                
                # รอสักครู่
                time.sleep(0.5)
            
            return {
                'success': True,
                'message': f'Update completed: {updated_count} updated, {failed_count} failed',
                'summary': {
                    'total': len(tmdb_ids),
                    'updated': updated_count,
                    'failed': failed_count
                },
                'results': results
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error updating movies: {str(e)}'}
    
    def get_update_statistics(self) -> Dict:
        """ดึงสถิติการอัปเดต"""
        try:
            movies = self.get_all_movies_from_database()
            
            total_movies = len(movies)
            needs_update = 0
            recently_updated = 0
            never_updated = 0
            
            for movie in movies:
                if not movie.get('updated_at'):
                    never_updated += 1
                elif self.check_movie_needs_update(movie):
                    needs_update += 1
                else:
                    recently_updated += 1
            
            return {
                'total_movies': total_movies,
                'needs_update': needs_update,
                'recently_updated': recently_updated,
                'never_updated': never_updated,
                'update_percentage': round((recently_updated / total_movies * 100), 2) if total_movies > 0 else 0
            }
            
        except Exception as e:
            print(f"Error getting update statistics: {e}")
            return {}
