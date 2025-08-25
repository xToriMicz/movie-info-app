import os
from supabase import create_client, Client
from dotenv import load_dotenv
import requests
from typing import Dict, List, Optional
import json
from datetime import datetime
import time

# Load environment variables
load_dotenv()

class SupabaseMovieManager:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.tmdb_api_key = os.getenv('TMDB_API_KEY')
        
        if not all([self.supabase_url, self.supabase_key, self.tmdb_api_key]):
            raise ValueError("Missing required environment variables")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        self.tmdb_base_url = "https://api.themoviedb.org/3"
        
        print("🎬 Supabase Movie Manager initialized!")
        print(f"📊 Supabase URL: {self.supabase_url}")
        print(f"🎭 TMDB API: Connected")
    
    def get_movie_from_tmdb(self, movie_id: int) -> Dict:
        """ดึงข้อมูลหนังจาก TMDB API"""
        try:
            url = f"{self.tmdb_base_url}/movie/{movie_id}"
            params = {
                'api_key': self.tmdb_api_key,
                'append_to_response': 'credits,videos'
            }
            
            print(f"🔍 Fetching movie data for ID: {movie_id}")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching movie data: {e}")
            return {}
    
    def extract_simple_data(self, movie_data: Dict) -> Dict:
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
        
        return {
            'tmdb_id': movie_data.get('id'),
            'title': title,
            'year': year,
            'original_title': original_title,
            'genres': genres,
            'trailer_id': trailer_id,
            'director': director,
            'cast_data': cast
        }
    
    def save_movie_to_database(self, movie_data: Dict) -> Optional[int]:
        """บันทึกข้อมูลหนังลง Supabase"""
        try:
            # ตรวจสอบว่ามีหนังนี้ในฐานข้อมูลแล้วหรือไม่
            existing = self.supabase.table('movies').select('id').eq('tmdb_id', movie_data['tmdb_id']).execute()
            
            movie_record = {
                'tmdb_id': movie_data['tmdb_id'],
                'title': movie_data['title'],
                'original_title': movie_data['original_title'],
                'year': movie_data['year'],
                'genres': movie_data['genres'],
                'trailer_id': movie_data['trailer_id'],
                'director': movie_data['director'],
                'cast_data': movie_data['cast_data']
            }
            
            if existing.data:
                # อัพเดทข้อมูล
                movie_id = existing.data[0]['id']
                self.supabase.table('movies').update(movie_record).eq('id', movie_id).execute()
                print(f"🔄 Updated movie: {movie_data['title']}")
            else:
                # เพิ่มข้อมูลใหม่
                result = self.supabase.table('movies').insert(movie_record).execute()
                movie_id = result.data[0]['id']
                print(f"✅ Added new movie: {movie_data['title']}")
            
            return movie_id
            
        except Exception as e:
            print(f"❌ Error saving movie to database: {e}")
            return None
    
    def import_movie(self, movie_id: int) -> bool:
        """นำเข้าข้อมูลหนังครบถ้วน"""
        try:
            print(f"\n🎬 Starting import for movie ID: {movie_id}")
            print("=" * 50)
            
            # ดึงข้อมูลจาก TMDB
            movie_data = self.get_movie_from_tmdb(movie_id)
            if not movie_data:
                print("❌ Failed to fetch data from TMDB")
                return False
            
            # ดึงเฉพาะข้อมูลที่ต้องการ
            simple_data = self.extract_simple_data(movie_data)
            
            # แสดงข้อมูลที่ได้
            print(f"📽️  Title: {simple_data['title']}")
            print(f"📅  Year: {simple_data['year']}")
            print(f"🎭  Genres: {', '.join(simple_data['genres'])}")
            print(f"🎬  Director: {simple_data['director']}")
            print(f"👥  Cast: {len(simple_data['cast_data'])} people")
            print(f"🎥  Trailer ID: {simple_data['trailer_id']}")
            
            # บันทึกลง Supabase
            db_movie_id = self.save_movie_to_database(simple_data)
            if not db_movie_id:
                print("❌ Failed to save movie to database")
                return False
            
            print("=" * 50)
            print(f"✅ Successfully imported: {simple_data['title']}")
            print(f" Database ID: {db_movie_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error importing movie: {e}")
            return False

def main():
    """ทดสอบนำเข้าหนังเรื่องเดียว"""
    print("🎬 Testing Single Movie Import")
    print("=" * 50)
    
    # ทดสอบกับหนัง Elio
    movie_id = 1022787  # Elio
    
    try:
        manager = SupabaseMovieManager()
        success = manager.import_movie(movie_id)
        
        if success:
            print("\n🎉 Test completed successfully!")
        else:
            print("\n❌ Test failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
