#!/usr/bin/env python3
"""
Test Update System
ทดสอบระบบอัปเดตข้อมูลหนัง
"""

import os
import sys
from dotenv import load_dotenv
from update_manager import MovieUpdateManager

# Load environment variables
load_dotenv()

def test_update_system():
    """ทดสอบระบบอัปเดต"""
    print("🧪 Testing Movie Update System")
    print("=" * 50)
    
    try:
        # สร้าง update manager
        update_manager = MovieUpdateManager()
        print("✅ Update Manager initialized successfully")
        
        # ทดสอบการดึงสถิติ
        print("\n📊 Testing Update Statistics...")
        stats = update_manager.get_update_statistics()
        print(f"Total movies: {stats.get('total_movies', 0)}")
        print(f"Needs update: {stats.get('needs_update', 0)}")
        print(f"Recently updated: {stats.get('recently_updated', 0)}")
        print(f"Never updated: {stats.get('never_updated', 0)}")
        print(f"Update percentage: {stats.get('update_percentage', 0)}%")
        
        # ทดสอบการดึงรายการหนัง
        print("\n📋 Testing Movie List...")
        movies = update_manager.get_all_movies_from_database()
        print(f"Found {len(movies)} movies in database")
        
        if movies:
            # แสดงหนัง 3 เรื่องแรก
            print("\n🎬 Sample Movies:")
            for i, movie in enumerate(movies[:3]):
                print(f"  {i+1}. {movie.get('title', 'Unknown')} (TMDB ID: {movie.get('tmdb_id', 'N/A')})")
                print(f"     Updated: {movie.get('updated_at', 'Never')}")
            
            # ทดสอบการอัปเดตหนังเดียว (ถ้ามี)
            if len(movies) > 0:
                test_movie = movies[0]
                tmdb_id = test_movie['tmdb_id']
                db_id = test_movie['id']
                
                print(f"\n🔄 Testing Single Movie Update (TMDB ID: {tmdb_id})...")
                result = update_manager.update_single_movie(db_id, tmdb_id)
                
                if result['success']:
                    print(f"✅ Successfully updated: {result['message']}")
                else:
                    print(f"❌ Update failed: {result['message']}")
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False
    
    return True

def test_tmdb_connection():
    """ทดสอบการเชื่อมต่อ TMDB"""
    print("\n🌐 Testing TMDB Connection...")
    
    try:
        update_manager = MovieUpdateManager()
        
        # ทดสอบดึงข้อมูลหนังตัวอย่าง (Mission: Impossible)
        movie_data = update_manager.get_movie_from_tmdb(575265)
        
        if movie_data:
            print("✅ TMDB connection successful")
            print(f"Movie title: {movie_data.get('title', 'Unknown')}")
            print(f"Release date: {movie_data.get('release_date', 'Unknown')}")
            return True
        else:
            print("❌ Failed to fetch movie data from TMDB")
            return False
            
    except Exception as e:
        print(f"❌ TMDB connection error: {str(e)}")
        return False

def test_streaming_providers():
    """ทดสอบการดึงข้อมูล streaming providers"""
    print("\n📺 Testing Streaming Providers...")
    
    try:
        update_manager = MovieUpdateManager()
        
        # ทดสอบดึงข้อมูล streaming providers
        providers = update_manager.get_streaming_providers(575265)
        
        if providers:
            print("✅ Streaming providers fetched successfully")
            for provider_type, provider_list in providers.items():
                if provider_list:
                    print(f"  {provider_type}: {len(provider_list)} providers")
                    for provider in provider_list[:2]:  # แสดง 2 providers แรก
                        print(f"    - {provider.get('provider_name', 'Unknown')}")
        else:
            print("ℹ️ No streaming providers found (this is normal for some movies)")
        
        return True
        
    except Exception as e:
        print(f"❌ Streaming providers error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🎬 Movie Update System Test")
    print("=" * 50)
    
    # ตรวจสอบ environment variables
    required_vars = ['TMDB_API_KEY', 'SUPABASE_URL', 'SUPABASE_ANON_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        return False
    
    print("✅ Environment variables loaded")
    
    # ทดสอบการเชื่อมต่อ TMDB
    if not test_tmdb_connection():
        return False
    
    # ทดสอบ streaming providers
    if not test_streaming_providers():
        return False
    
    # ทดสอบระบบอัปเดต
    if not test_update_system():
        return False
    
    print("\n🎉 All tests passed! The update system is ready to use.")
    print("\n📝 Next steps:")
    print("1. Run: python update_movies.py --stats")
    print("2. Run: python update_movies.py --single 575265")
    print("3. Run: python update_movies.py --all")
    print("4. Visit: https://movie-info-app.onrender.com/admin/updates")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
