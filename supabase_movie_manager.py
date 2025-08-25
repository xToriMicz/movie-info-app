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
            'cast_data': cast  # ใช้ cast_data แทน cast
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
    
    def get_movie_from_database(self, movie_id: int) -> Dict:
        """ดึงข้อมูลหนังจาก Supabase"""
        try:
            movie = self.supabase.table('movies').select('*').eq('id', movie_id).execute()
            
            if movie.data:
                return movie.data[0]
            else:
                print(f"❌ Movie with ID {movie_id} not found in database")
                return {}
                
        except Exception as e:
            print(f"❌ Error getting movie from database: {e}")
            return {}
    
    def list_all_movies(self, limit: int = 10) -> List[Dict]:
        """แสดงรายการหนังทั้งหมดในฐานข้อมูล"""
        try:
            movies = self.supabase.table('movies').select(
                'id, tmdb_id, title, year, director, genres'
            ).order('created_at', desc=True).limit(limit).execute()
            
            return movies.data
            
        except Exception as e:
            print(f"❌ Error listing movies: {e}")
            return []
    
    def search_movies(self, query: str) -> List[Dict]:
        """ค้นหาหนังในฐานข้อมูล"""
        try:
            movies = self.supabase.table('movies').select(
                'id, tmdb_id, title, year, director, genres'
            ).ilike('title', f'%{query}%').execute()
            
            return movies.data
            
        except Exception as e:
            print(f"❌ Error searching movies: {e}")
            return []
    
    def display_movie_data(self, movie_data: Dict):
        """แสดงข้อมูลหนังในรูปแบบที่อ่านง่าย"""
        if not movie_data:
            print("❌ No movie data to display")
            return
        
        print(f"\n{'='*60}")
        print(f"🎬 MOVIE INFORMATION")
        print(f"{'='*60}")
        
        print(f"️  Title: {movie_data.get('title', 'N/A')}")
        print(f"  Year: {movie_data.get('year', 'N/A')}")
        print(f"  Original Title: {movie_data.get('original_title', 'N/A')}")
        
        genres = movie_data.get('genres', [])
        if genres:
            print(f"🎭  Genres: {', '.join(genres)}")
        else:
            print(f"🎭  Genres: N/A")
        
        director = movie_data.get('director')
        if director:
            print(f"  Director: {director}")
        else:
            print(f"🎬  Director: N/A")
        
        cast = movie_data.get('cast_data', [])
        if cast:
            print(f"👥  Cast:")
            for i, actor in enumerate(cast, 1):
                character = f" as {actor['character']}" if actor['character'] else ""
                print(f"     {i}. {actor['name']}{character}")
        else:
            print(f"👥  Cast: N/A")
        
        trailer_id = movie_data.get('trailer_id')
        if trailer_id:
            print(f"🎥  Trailer ID: {trailer_id}")
            print(f"🔗  Trailer URL: https://www.youtube.com/watch?v={trailer_id}")
        else:
            print(f"🎥  Trailer: N/A")
        
        print(f"{'='*60}")

def test_supabase_connection():
    """ทดสอบการเชื่อมต่อ Supabase"""
    try:
        manager = SupabaseMovieManager()
        
        # ทดสอบดึงข้อมูลจากตาราง movies
        movies = manager.list_all_movies(1)
        print(f"✅ Supabase connection successful! Found {len(movies)} movies in database")
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

def import_multiple_movies():
    """นำเข้าหนังหลายเรื่อง"""
    manager = SupabaseMovieManager()
    
    # รายการหนังที่ต้องการนำเข้า
    movie_ids = [
        1022787,  # Elio
        299536,   # Avengers: Infinity War
        550,      # Fight Club
        13,       # Forrest Gump
        680,      # Pulp Fiction
        238,      # The Godfather
        278,      # The Shawshank Redemption
    ]
    
    print(f"🎬 Importing {len(movie_ids)} movies...")
    print("=" * 60)
    
    successful_imports = 0
    
    for i, movie_id in enumerate(movie_ids, 1):
        print(f"\n📋 [{i}/{len(movie_ids)}] Processing movie ID: {movie_id}")
        
        success = manager.import_movie(movie_id)
        if success:
            successful_imports += 1
        
        # หน่วงเวลาเล็กน้อย
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print("📊 IMPORT SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successful imports: {successful_imports}/{len(movie_ids)}")
    print(f"❌ Failed imports: {len(movie_ids) - successful_imports}/{len(movie_ids)}")

def main():
    """เมนูหลัก"""
    print("🎬 Supabase Movie Manager")
    print("=" * 40)
    print("1. Test Supabase connection")
    print("2. Import single movie")
    print("3. Import multiple movies")
    print("4. List all movies in database")
    print("5. Search movies")
    print("6. Get movie details")
    print("7. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            test_supabase_connection()
            break
        elif choice == '2':
            try:
                movie_id = int(input("Enter TMDB movie ID: "))
                manager = SupabaseMovieManager()
                manager.import_movie(movie_id)
            except ValueError:
                print("❌ Please enter a valid number")
            break
        elif choice == '3':
            import_multiple_movies()
            break
        elif choice == '4':
            try:
                limit = int(input("Enter limit (default 10): ") or "10")
                manager = SupabaseMovieManager()
                movies = manager.list_all_movies(limit)
                print(f"\n📋 Found {len(movies)} movies:")
                for movie in movies:
                    print(f"  • {movie['title']} ({movie['year']}) - {movie['director']}")
            except ValueError:
                print("❌ Please enter a valid number")
            break
        elif choice == '5':
            query = input("Enter search query: ").strip()
            if query:
                manager = SupabaseMovieManager()
                movies = manager.search_movies(query)
                print(f"\n🔍 Found {len(movies)} movies matching '{query}':")
                for movie in movies:
                    print(f"  • {movie['title']} ({movie['year']})")
            break
        elif choice == '6':
            try:
                movie_id = int(input("Enter database movie ID: "))
                manager = SupabaseMovieManager()
                movie_data = manager.get_movie_from_database(movie_id)
                manager.display_movie_data(movie_data)
            except ValueError:
                print("❌ Please enter a valid number")
            break
        elif choice == '7':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-7.")

if __name__ == "__main__":
    main()
