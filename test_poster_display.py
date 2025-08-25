#!/usr/bin/env python3
"""
Test Poster Display
ทดสอบการแสดงผลโปสเตอร์ในหน้าเว็บ
"""

import requests
import json
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Supabase configuration
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

def test_poster_data():
    """ทดสอบข้อมูลโปสเตอร์ในฐานข้อมูล"""
    print("🎬 Testing Poster Data")
    print("=" * 50)
    
    try:
        # ดึงข้อมูลหนังจากฐานข้อมูล
        response = supabase.table('movies').select('*').execute()
        movies = response.data
        
        print(f"📊 Found {len(movies)} movies in database")
        print()
        
        for movie in movies:
            print(f"🎬 {movie['title']} (ID: {movie['id']})")
            print(f"   TMDB ID: {movie['tmdb_id']}")
            print(f"   Poster Path: {movie.get('poster_path', '❌ None')}")
            streaming_providers = movie.get('streaming_providers', [])
            if streaming_providers is None:
                streaming_providers = []
            print(f"   Streaming Providers: {len(streaming_providers)} providers")
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_web_display():
    """ทดสอบการแสดงผลในหน้าเว็บ"""
    print("🌐 Testing Web Display")
    print("=" * 50)
    
    try:
        # ทดสอบหน้าแรก
        response = requests.get('http://127.0.0.1:5000/')
        if response.status_code == 200:
            content = response.text
            if 'movie-poster-thumbnail' in content:
                print("✅ Poster thumbnail CSS class found in homepage")
            else:
                print("❌ Poster thumbnail CSS class NOT found in homepage")
                
            if 'no-poster.jpg' in content:
                print("⚠️  No-poster placeholder found (may indicate missing posters)")
            else:
                print("✅ No-poster placeholder not found (good sign)")
        else:
            print(f"❌ Homepage returned status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing web display: {e}")

def test_static_files():
    """ทดสอบไฟล์ static"""
    print("📁 Testing Static Files")
    print("=" * 50)
    
    poster_dir = "static/images/posters"
    if os.path.exists(poster_dir):
        files = os.listdir(poster_dir)
        print(f"✅ Poster directory exists: {poster_dir}")
        print(f"📊 Found {len(files)} poster files:")
        for file in files:
            file_path = os.path.join(poster_dir, file)
            size = os.path.getsize(file_path)
            print(f"   📄 {file} ({size:,} bytes)")
    else:
        print(f"❌ Poster directory not found: {poster_dir}")

if __name__ == "__main__":
    print("🎬 Movie Info App - Poster Display Test")
    print("=" * 60)
    print()
    
    test_poster_data()
    print()
    test_static_files()
    print()
    test_web_display()
    print()
    
    print("🎉 Test completed!")
    print()
    print("📝 Next steps:")
    print("1. Visit: http://127.0.0.1:5000/")
    print("2. Check if posters are displayed")
    print("3. If not, try refreshing the page (Ctrl+F5)")
