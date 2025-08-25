#!/usr/bin/env python3
"""
Update Existing Movies
อัปเดตข้อมูล poster และ streaming providers ให้หนังที่มีอยู่แล้ว
"""

import os
import sys
import time
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def update_existing_movies():
    """อัปเดตข้อมูล poster และ streaming providers ให้หนังที่มีอยู่แล้ว"""
    print("🔄 Updating Existing Movies with Poster and Streaming Data")
    print("=" * 60)
    
    try:
        # เชื่อมต่อ Supabase
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        tmdb_api_key = os.getenv('TMDB_API_KEY')
        
        if not all([supabase_url, supabase_key, tmdb_api_key]):
            print("❌ Missing environment variables")
            return False
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # ดึงหนังทั้งหมดที่ยังไม่มี poster_path หรือ streaming_providers
        movies = supabase.table('movies').select('id, tmdb_id, title').execute()
        
        if not movies.data:
            print("ℹ️ No movies found in database")
            return True
        
        print(f"📊 Found {len(movies.data)} movies in database")
        
        # นับหนังที่ต้องอัปเดต
        movies_to_update = []
        for movie in movies.data:
            # ตรวจสอบว่าหนังนี้มี poster_path หรือไม่
            movie_detail = supabase.table('movies').select('poster_path, streaming_providers').eq('id', movie['id']).execute()
            if movie_detail.data:
                current_data = movie_detail.data[0]
                if not current_data.get('poster_path') or not current_data.get('streaming_providers'):
                    movies_to_update.append(movie)
        
        print(f"🎯 Found {len(movies_to_update)} movies that need updating")
        
        if not movies_to_update:
            print("✅ All movies already have poster and streaming data")
            return True
        
        # อัปเดตหนังทีละเรื่อง
        updated_count = 0
        failed_count = 0
        
        for movie in movies_to_update:
            tmdb_id = movie['tmdb_id']
            title = movie['title']
            db_id = movie['id']
            
            print(f"\n🔄 Updating: {title} (TMDB ID: {tmdb_id})")
            
            try:
                # ดึงข้อมูลจาก TMDB
                movie_data = get_movie_from_tmdb(tmdb_id, tmdb_api_key)
                if not movie_data:
                    print(f"   ❌ Failed to fetch data from TMDB")
                    failed_count += 1
                    continue
                
                # ดึงข้อมูล poster และ streaming providers
                poster_path = movie_data.get('poster_path', '')
                streaming_providers = get_streaming_providers(tmdb_id, tmdb_api_key)
                
                # อัปเดตฐานข้อมูล
                update_data = {}
                if poster_path:
                    update_data['poster_path'] = poster_path
                if streaming_providers:
                    update_data['streaming_providers'] = streaming_providers
                
                if update_data:
                    supabase.table('movies').update(update_data).eq('id', db_id).execute()
                    updated_count += 1
                    print(f"   ✅ Updated successfully")
                    print(f"      Poster: {poster_path if poster_path else 'None'}")
                    print(f"      Streaming providers: {len(streaming_providers) if streaming_providers else 0} providers")
                else:
                    print(f"   ⚠️ No new data to update")
                
                # รอสักครู่เพื่อไม่ให้เกิน rate limit
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   ❌ Error updating movie: {str(e)}")
                failed_count += 1
        
        # สรุปผลลัพธ์
        print(f"\n📊 Update Summary:")
        print(f"Total movies: {len(movies.data)}")
        print(f"Updated: {updated_count}")
        print(f"Failed: {failed_count}")
        print(f"Skipped: {len(movies.data) - len(movies_to_update)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating movies: {str(e)}")
        return False

def get_movie_from_tmdb(movie_id, api_key):
    """ดึงข้อมูลหนังจาก TMDB API"""
    import requests
    
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {
            'api_key': api_key,
            'append_to_response': 'credits,videos'
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching movie data: {e}")
        return {}

def get_streaming_providers(movie_id, api_key):
    """ดึงข้อมูล streaming providers จาก TMDB"""
    import requests
    
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers"
        params = {
            'api_key': api_key
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

def main():
    """Main function"""
    print("🎬 Update Existing Movies")
    print("=" * 50)
    
    # ตรวจสอบ environment variables
    required_vars = ['TMDB_API_KEY', 'SUPABASE_URL', 'SUPABASE_ANON_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        return False
    
    print("✅ Environment variables loaded")
    
    # อัปเดตหนังที่มีอยู่แล้ว
    if not update_existing_movies():
        return False
    
    print("\n🎉 Update completed!")
    print("\n📝 Next steps:")
    print("1. Run: python check_poster_status.py")
    print("2. Run: python check_poster_status.py --download")
    print("3. Visit: https://movie-info-app.onrender.com/admin/updates")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
