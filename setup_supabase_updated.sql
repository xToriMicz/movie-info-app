-- Updated Supabase Schema for Movie Info App with Update Management
-- Run this in Supabase SQL Editor

-- Drop existing table if exists
DROP TABLE IF EXISTS movies;

-- Create movies table with update management
CREATE TABLE movies (
    id SERIAL PRIMARY KEY,
    tmdb_id INTEGER UNIQUE NOT NULL,
    title TEXT NOT NULL,
    original_title TEXT,
    year TEXT,
    genres TEXT[],
    trailer_id TEXT,
    director TEXT,
    cast_data JSONB,
    poster_path TEXT,
    streaming_providers JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_movies_tmdb_id ON movies(tmdb_id);
CREATE INDEX idx_movies_title ON movies(title);
CREATE INDEX idx_movies_year ON movies(year);
CREATE INDEX idx_movies_updated_at ON movies(updated_at);

-- Enable Row Level Security (RLS)
ALTER TABLE movies ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (for now)
CREATE POLICY "Allow all operations" ON movies
    FOR ALL USING (true);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_movies_updated_at 
    BEFORE UPDATE ON movies 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data (optional)
INSERT INTO movies (tmdb_id, title, original_title, year, genres, trailer_id, director, cast_data, poster_path, streaming_providers) VALUES
(575265, 'Mission: Impossible - The Final Reckoning', 'Mission: Impossible - Dead Reckoning Part Two', '2025', ARRAY['Action', 'Adventure', 'Thriller'], 'abc123', 'Christopher McQuarrie', 
'[{"name": "Tom Cruise", "character": "Ethan Hunt"}, {"name": "Hayley Atwell", "character": "Grace"}, {"name": "Ving Rhames", "character": "Luther Stickell"}]',
'/poster_path_1.jpg',
'{"streaming": [{"provider_name": "Netflix", "logo_path": "/netflix_logo.png", "provider_id": 8}], "rent": [{"provider_name": "iTunes", "logo_path": "/itunes_logo.png", "provider_id": 2}]}'
);

-- Grant permissions
GRANT ALL ON movies TO anon;
GRANT ALL ON movies TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE movies_id_seq TO anon;
GRANT USAGE, SELECT ON SEQUENCE movies_id_seq TO authenticated;

-- Create view for update statistics (optional)
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
