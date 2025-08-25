#!/usr/bin/env python3
"""
Check Poster Status
ตรวจสอบสถานะ poster ในระบบ
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def check_poster_status():
    """ตรวจสอบสถานะ poster ทั้งหมด"""
    print("🖼️ Checking Poster Status")
    print("=" * 50)
    
    try:
        # เชื่อมต่อ Supabase
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not all([supabase_url, supabase_key]):
            print("❌ Missing Supabase environment variables")
            return False
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # ดึงข้อมูลหนังทั้งหมด
        movies = supabase.table('movies').select('id, tmdb_id, title, poster_path').execute()
        
        if not movies.data:
            print("ℹ️ No movies found in database")
            return True
        
        print(f"📊 Found {len(movies.data)} movies in database")
        
        # ตรวจสอบ poster paths
        movies_with_poster = 0
        movies_without_poster = 0
        poster_files_exist = 0
        poster_files_missing = 0
        
        posters_dir = Path("static/images/posters")
        posters_dir.mkdir(parents=True, exist_ok=True)
        
        print("\n🎬 Poster Status:")
        print("-" * 30)
        
        for movie in movies.data:
            tmdb_id = movie['tmdb_id']
            title = movie['title']
            poster_path = movie.get('poster_path')
            
            # ตรวจสอบในฐานข้อมูล
            if poster_path:
                movies_with_poster += 1
                print(f"✅ {title} (TMDB ID: {tmdb_id})")
                print(f"   Database: {poster_path}")
                
                # ตรวจสอบไฟล์ (ทั้งแบบมี hash และไม่มี hash)
                poster_file_simple = posters_dir / f"{tmdb_id}.jpg"
                poster_files_with_hash = list(posters_dir.glob(f"{tmdb_id}_*.jpg"))
                
                if poster_file_simple.exists():
                    poster_files_exist += 1
                    file_size = poster_file_simple.stat().st_size
                    print(f"   File: ✅ {poster_file_simple.name} ({file_size:,} bytes)")
                elif poster_files_with_hash:
                    poster_files_exist += 1
                    poster_file = poster_files_with_hash[0]
                    file_size = poster_file.stat().st_size
                    print(f"   File: ✅ {poster_file.name} ({file_size:,} bytes)")
                else:
                    poster_files_missing += 1
                    print(f"   File: ❌ Missing ({tmdb_id}.jpg)")
            else:
                movies_without_poster += 1
                print(f"❌ {title} (TMDB ID: {tmdb_id})")
                print(f"   Database: No poster path")
        
        # สรุปสถิติ
        print("\n📈 Summary:")
        print("-" * 30)
        print(f"Total movies: {len(movies.data)}")
        print(f"Movies with poster path: {movies_with_poster}")
        print(f"Movies without poster path: {movies_without_poster}")
        print(f"Poster files exist: {poster_files_exist}")
        print(f"Poster files missing: {poster_files_missing}")
        
        # คำนวณเปอร์เซ็นต์
        if movies.data:
            poster_coverage = (movies_with_poster / len(movies.data)) * 100
            file_coverage = (poster_files_exist / len(movies.data)) * 100
            print(f"Poster path coverage: {poster_coverage:.1f}%")
            print(f"Poster file coverage: {file_coverage:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking poster status: {str(e)}")
        return False

def download_missing_posters():
    """ดาวน์โหลด poster ที่หายไป"""
    print("\n🔄 Downloading Missing Posters")
    print("=" * 50)
    
    try:
        from update_manager import MovieUpdateManager
        from utils import download_and_save_poster
        
        update_manager = MovieUpdateManager()
        supabase = update_manager.supabase
        
        # ดึงหนังที่มี poster_path แต่ไม่มีไฟล์
        movies = supabase.table('movies').select('id, tmdb_id, title, poster_path').execute()
        
        posters_dir = Path("static/images/posters")
        downloaded_count = 0
        failed_count = 0
        
        for movie in movies.data:
            tmdb_id = movie['tmdb_id']
            title = movie['title']
            poster_path = movie.get('poster_path')
            
            if poster_path:
                # ตรวจสอบไฟล์ (ทั้งแบบมี hash และไม่มี hash)
                poster_file_simple = posters_dir / f"{tmdb_id}.jpg"
                poster_files_with_hash = list(posters_dir.glob(f"{tmdb_id}_*.jpg"))
                
                if not poster_file_simple.exists() and not poster_files_with_hash:
                    print(f"📥 Downloading poster for: {title} (TMDB ID: {tmdb_id})")
                    
                    try:
                        download_and_save_poster(poster_path, tmdb_id)
                        downloaded_count += 1
                        print(f"   ✅ Downloaded successfully")
                    except Exception as e:
                        failed_count += 1
                        print(f"   ❌ Failed: {str(e)}")
        
        print(f"\n📊 Download Summary:")
        print(f"Downloaded: {downloaded_count}")
        print(f"Failed: {failed_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error downloading posters: {str(e)}")
        return False

def cleanup_orphaned_posters():
    """ลบไฟล์ poster ที่ไม่มีในฐานข้อมูล"""
    print("\n🧹 Cleaning Up Orphaned Posters")
    print("=" * 50)
    
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # ดึง TMDB IDs จากฐานข้อมูล
        movies = supabase.table('movies').select('tmdb_id').execute()
        db_tmdb_ids = {movie['tmdb_id'] for movie in movies.data}
        
        # ตรวจสอบไฟล์ในโฟลเดอร์
        posters_dir = Path("static/images/posters")
        if not posters_dir.exists():
            print("ℹ️ Posters directory does not exist")
            return True
        
        orphaned_files = []
        total_files = 0
        
        for poster_file in posters_dir.glob("*.jpg"):
            total_files += 1
            # ดึง TMDB ID จากชื่อไฟล์ (ทั้งแบบมี hash และไม่มี hash)
            try:
                if "_" in poster_file.stem:
                    tmdb_id = int(poster_file.stem.split("_")[0])
                else:
                    tmdb_id = int(poster_file.stem)
                
                if tmdb_id not in db_tmdb_ids:
                    orphaned_files.append(poster_file)
            except ValueError:
                # ไฟล์ที่ไม่ใช่ตัวเลข (เช่น no-poster.jpg)
                continue
        
        print(f"📁 Found {total_files} poster files")
        print(f"🗑️ Found {len(orphaned_files)} orphaned files")
        
        if orphaned_files:
            print("\nOrphaned files:")
            for file in orphaned_files:
                file_size = file.stat().st_size
                print(f"   {file.name} ({file_size:,} bytes)")
            
            # ถามผู้ใช้ว่าต้องการลบหรือไม่
            response = input("\nDo you want to delete these orphaned files? (y/N): ")
            if response.lower() == 'y':
                deleted_count = 0
                for file in orphaned_files:
                    try:
                        file.unlink()
                        deleted_count += 1
                        print(f"   ✅ Deleted: {file.name}")
                    except Exception as e:
                        print(f"   ❌ Failed to delete {file.name}: {str(e)}")
                
                print(f"\n🗑️ Deleted {deleted_count} orphaned files")
            else:
                print("❌ No files deleted")
        else:
            print("✅ No orphaned files found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning up posters: {str(e)}")
        return False

def main():
    """Main function"""
    print("🎬 Poster Management System")
    print("=" * 50)
    
    # ตรวจสอบ environment variables
    required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        return False
    
    print("✅ Environment variables loaded")
    
    # ตรวจสอบสถานะ poster
    if not check_poster_status():
        return False
    
    # ถามผู้ใช้ว่าต้องการดาวน์โหลด poster ที่หายไปหรือไม่
    if len(sys.argv) > 1 and sys.argv[1] == '--download':
        download_missing_posters()
    
    # ถามผู้ใช้ว่าต้องการลบไฟล์ที่ไม่ได้ใช้หรือไม่
    if len(sys.argv) > 1 and sys.argv[1] == '--cleanup':
        cleanup_orphaned_posters()
    
    print("\n🎉 Poster status check completed!")
    print("\n📝 Available commands:")
    print("  python check_poster_status.py --download  # Download missing posters")
    print("  python check_poster_status.py --cleanup   # Clean up orphaned files")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
