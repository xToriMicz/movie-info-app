from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
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

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Enable CORS for all routes
CORS(app, origins=['chrome-extension://*', 'https://www.themoviedb.org'])

class SupabaseMovieManager:
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
                return movie_id
            else:
                # เพิ่มข้อมูลใหม่
                result = self.supabase.table('movies').insert(movie_record).execute()
                return result.data[0]['id']
            
        except Exception as e:
            print(f"Error saving movie to database: {e}")
            return None
    
    def import_movie(self, movie_id: int) -> Dict:
        """นำเข้าข้อมูลหนังครบถ้วน"""
        try:
            # ดึงข้อมูลจาก TMDB
            movie_data = self.get_movie_from_tmdb(movie_id)
            if not movie_data:
                return {'success': False, 'message': 'Failed to fetch data from TMDB'}
            
            # ดึงเฉพาะข้อมูลที่ต้องการ
            simple_data = self.extract_simple_data(movie_data)
            
            # บันทึกลง Supabase
            db_movie_id = self.save_movie_to_database(simple_data)
            if not db_movie_id:
                return {'success': False, 'message': 'Failed to save movie to database'}
            
            return {
                'success': True, 
                'message': f'Successfully imported: {simple_data["title"]}',
                'movie_id': db_movie_id,
                'data': simple_data
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error importing movie: {str(e)}'}
    
    def get_movie_from_database(self, movie_id: int) -> Dict:
        """ดึงข้อมูลหนังจาก Supabase"""
        try:
            movie = self.supabase.table('movies').select('*').eq('id', movie_id).execute()
            
            if movie.data:
                return movie.data[0]
            else:
                return {}
                
        except Exception as e:
            print(f"Error getting movie from database: {e}")
            return {}
    
    def list_all_movies(self, limit: int = 50) -> List[Dict]:
        """แสดงรายการหนังทั้งหมดในฐานข้อมูล"""
        try:
            movies = self.supabase.table('movies').select(
                'id, tmdb_id, title, year, director, genres, created_at'
            ).order('created_at', desc=True).limit(limit).execute()
            
            return movies.data
            
        except Exception as e:
            print(f"Error listing movies: {e}")
            return []
    
    def search_movies(self, query: str) -> List[Dict]:
        """ค้นหาหนังในฐานข้อมูล"""
        try:
            movies = self.supabase.table('movies').select(
                'id, tmdb_id, title, year, director, genres'
            ).ilike('title', f'%{query}%').execute()
            
            return movies.data
            
        except Exception as e:
            print(f"Error searching movies: {e}")
            return []
    
    def search_tmdb_movies(self, query: str) -> List[Dict]:
        """ค้นหาหนังใน TMDB"""
        try:
            url = f"{self.tmdb_base_url}/search/movie"
            params = {
                'api_key': self.tmdb_api_key,
                'query': query,
                'page': 1
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('results', [])[:10]  # 10 ผลลัพธ์แรก
            
        except Exception as e:
            print(f"Error searching TMDB: {e}")
            return []

# Initialize movie manager
try:
    movie_manager = SupabaseMovieManager()
except Exception as e:
    print(f"Failed to initialize movie manager: {e}")
    movie_manager = None

@app.route('/')
def index():
    """หน้าแรก"""
    if not movie_manager:
        return render_template('error.html', message="Failed to connect to database")
    
    try:
        movies = movie_manager.list_all_movies(10)
        return render_template('index.html', movies=movies)
    except Exception as e:
        return render_template('error.html', message=f"Error loading movies: {str(e)}")

@app.route('/movies')
def movies():
    """หน้ารายการหนัง"""
    if not movie_manager:
        return render_template('error.html', message="Failed to connect to database")
    
    try:
        movies = movie_manager.list_all_movies(50)
        return render_template('movies.html', movies=movies)
    except Exception as e:
        return render_template('error.html', message=f"Error loading movies: {str(e)}")

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    """หน้ารายละเอียดหนัง"""
    if not movie_manager:
        return render_template('error.html', message="Failed to connect to database")
    
    try:
        movie = movie_manager.get_movie_from_database(movie_id)
        if not movie:
            return render_template('error.html', message="Movie not found")
        
        return render_template('movie_detail.html', movie=movie)
    except Exception as e:
        return render_template('error.html', message=f"Error loading movie: {str(e)}")

@app.route('/search')
def search():
    """หน้าค้นหา"""
    query = request.args.get('q', '')
    if not query:
        return render_template('search.html', movies=[], tmdb_results=[])
    
    if not movie_manager:
        return render_template('error.html', message="Failed to connect to database")
    
    try:
        # ค้นหาในฐานข้อมูล
        db_movies = movie_manager.search_movies(query)
        
        # ค้นหาใน TMDB
        tmdb_results = movie_manager.search_tmdb_movies(query)
        
        return render_template('search.html', movies=db_movies, tmdb_results=tmdb_results, query=query)
    except Exception as e:
        return render_template('error.html', message=f"Error searching: {str(e)}")

@app.route('/import', methods=['GET', 'POST'])
def import_movie():
    """หน้านำเข้าข้อมูล"""
    if request.method == 'POST':
        movie_id = request.form.get('movie_id')
        if not movie_id:
            flash('Please enter a movie ID', 'error')
            return redirect(url_for('import_movie'))
        
        try:
            movie_id = int(movie_id)
        except ValueError:
            flash('Invalid movie ID', 'error')
            return redirect(url_for('import_movie'))
        
        if not movie_manager:
            flash('Failed to connect to database', 'error')
            return redirect(url_for('import_movie'))
        
        try:
            result = movie_manager.import_movie(movie_id)
            if result['success']:
                flash(result['message'], 'success')
                return redirect(url_for('movie_detail', movie_id=result['movie_id']))
            else:
                flash(result['message'], 'error')
        except Exception as e:
            flash(f'Error importing movie: {str(e)}', 'error')
        
        return redirect(url_for('import_movie'))
    
    return render_template('import.html')

@app.route('/api/import/<int:movie_id>')
def api_import_movie(movie_id):
    """API สำหรับนำเข้าข้อมูล"""
    if not movie_manager:
        return jsonify({'success': False, 'message': 'Failed to connect to database'})
    
    try:
        result = movie_manager.import_movie(movie_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/movies')
def api_movies():
    """API สำหรับดึงรายการหนัง"""
    if not movie_manager:
        return jsonify({'success': False, 'message': 'Failed to connect to database'})
    
    try:
        movies = movie_manager.list_all_movies(50)
        return jsonify({'success': True, 'movies': movies})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

if __name__ == '__main__':
    # Get port from environment variable (for Render)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
