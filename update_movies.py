#!/usr/bin/env python3
"""
Movie Update Script
สคริปต์สำหรับอัปเดตข้อมูลหนังเก่าจาก TMDB
"""

import argparse
import sys
from update_manager import MovieUpdateManager

def main():
    parser = argparse.ArgumentParser(description='Update movie data from TMDB')
    parser.add_argument('--all', action='store_true', help='Update all movies')
    parser.add_argument('--force', action='store_true', help='Force update even if recently updated')
    parser.add_argument('--days', type=int, default=7, help='Days threshold for updates (default: 7)')
    parser.add_argument('--ids', nargs='+', type=int, help='Update specific TMDB IDs')
    parser.add_argument('--stats', action='store_true', help='Show update statistics')
    parser.add_argument('--single', type=int, help='Update single movie by TMDB ID')
    
    args = parser.parse_args()
    
    try:
        # สร้าง update manager
        update_manager = MovieUpdateManager()
        
        # แสดงสถิติ
        if args.stats:
            stats = update_manager.get_update_statistics()
            print("\n📊 Update Statistics:")
            print(f"Total movies: {stats.get('total_movies', 0)}")
            print(f"Needs update: {stats.get('needs_update', 0)}")
            print(f"Recently updated: {stats.get('recently_updated', 0)}")
            print(f"Never updated: {stats.get('never_updated', 0)}")
            print(f"Update percentage: {stats.get('update_percentage', 0)}%")
            return
        
        # อัปเดตหนังเดียว
        if args.single:
            print(f"\n🔄 Updating single movie (TMDB ID: {args.single})")
            
            # หา movie ในฐานข้อมูล
            movie = update_manager.supabase.table('movies').select('id, title').eq('tmdb_id', args.single).execute()
            
            if not movie.data:
                print(f"❌ Movie with TMDB ID {args.single} not found in database")
                return
            
            db_movie_id = movie.data[0]['id']
            title = movie.data[0]['title']
            
            result = update_manager.update_single_movie(db_movie_id, args.single)
            
            if result['success']:
                print(f"✅ Successfully updated: {title}")
            else:
                print(f"❌ Failed to update: {result['message']}")
            
            return
        
        # อัปเดตตาม IDs ที่ระบุ
        if args.ids:
            print(f"\n🔄 Updating {len(args.ids)} movies by TMDB IDs")
            result = update_manager.update_movies_by_ids(args.ids)
            
            if result['success']:
                summary = result['summary']
                print(f"✅ Update completed:")
                print(f"   - Updated: {summary['updated']}")
                print(f"   - Failed: {summary['failed']}")
                print(f"   - Total: {summary['total']}")
            else:
                print(f"❌ Update failed: {result['message']}")
            
            return
        
        # อัปเดตหนังทั้งหมด
        if args.all:
            print(f"\n🔄 Updating all movies (force: {args.force}, days threshold: {args.days})")
            result = update_manager.update_all_movies(force_update=args.force, days_threshold=args.days)
            
            if result['success']:
                summary = result['summary']
                print(f"✅ Update completed:")
                print(f"   - Total: {summary['total']}")
                print(f"   - Updated: {summary['updated']}")
                print(f"   - Failed: {summary['failed']}")
                print(f"   - Skipped: {summary['skipped']}")
            else:
                print(f"❌ Update failed: {result['message']}")
            
            return
        
        # หากไม่ระบุอาร์กิวเมนต์ ให้แสดง help
        parser.print_help()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
