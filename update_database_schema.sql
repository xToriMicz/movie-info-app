-- Update Database Schema for Movie Info App (Preserve Existing Data)
-- Run this in Supabase SQL Editor to add update management features

-- Add poster_path column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'movies' AND column_name = 'poster_path') THEN
        ALTER TABLE movies ADD COLUMN poster_path TEXT;
        RAISE NOTICE 'Added poster_path column';
    END IF;
END $$;

-- Add streaming_providers column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'movies' AND column_name = 'streaming_providers') THEN
        ALTER TABLE movies ADD COLUMN streaming_providers JSONB;
        RAISE NOTICE 'Added streaming_providers column';
    END IF;
END $$;

-- Add updated_at column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'movies' AND column_name = 'updated_at') THEN
        ALTER TABLE movies ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
        
        -- Update existing records to have updated_at = created_at
        UPDATE movies SET updated_at = created_at WHERE updated_at IS NULL;
        RAISE NOTICE 'Added updated_at column';
    END IF;
END $$;

-- Create index for updated_at if it doesn't exist
CREATE INDEX IF NOT EXISTS idx_movies_updated_at ON movies(updated_at);

-- Create or replace function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop existing trigger if exists
DROP TRIGGER IF EXISTS update_movies_updated_at ON movies;

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_movies_updated_at 
    BEFORE UPDATE ON movies 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Create or replace view for update statistics
CREATE OR REPLACE VIEW movie_update_stats AS
SELECT 
    COUNT(*) as total_movies,
    COUNT(CASE WHEN updated_at IS NULL THEN 1 END) as never_updated,
    COUNT(CASE WHEN updated_at < NOW() - INTERVAL '7 days' THEN 1 END) as needs_update,
    COUNT(CASE WHEN updated_at >= NOW() - INTERVAL '7 days' THEN 1 END) as recently_updated,
    ROUND(
        (COUNT(CASE WHEN updated_at >= NOW() - INTERVAL '7 days' THEN 1 END)::DECIMAL / COUNT(*)) * 100, 
        2
    ) as update_percentage
FROM movies;

-- Grant permissions on view
GRANT SELECT ON movie_update_stats TO anon;
GRANT SELECT ON movie_update_stats TO authenticated;

-- Show current schema status
SELECT 
    'Schema updated successfully!' as status,
    COUNT(*) as total_movies,
    COUNT(CASE WHEN updated_at IS NOT NULL THEN 1 END) as movies_with_updated_at,
    COUNT(CASE WHEN poster_path IS NOT NULL THEN 1 END) as movies_with_poster_path,
    COUNT(CASE WHEN streaming_providers IS NOT NULL THEN 1 END) as movies_with_streaming_providers
FROM movies;
