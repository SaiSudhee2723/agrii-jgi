-- ============================================================================
-- GEOSENSE SMART AGRICULTURE: FARMS TABLE & ROW LEVEL SECURITY (RLS)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.farms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    farm_name TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    boundary_coordinates JSONB, -- Array of [lat, lon] coordinates
    area_acres DOUBLE PRECISION DEFAULT 0.0,
    crop_type TEXT DEFAULT 'General Crop',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE public.farms ENABLE ROW LEVEL SECURITY;

-- 1. SELECT: Users can only read their own farms
CREATE POLICY "Users can view their own farms"
    ON public.farms FOR SELECT
    USING (auth.uid() = user_id);

-- 2. INSERT: Users can only insert farms for their own authenticated user_id
CREATE POLICY "Users can insert their own farms"
    ON public.farms FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- 3. UPDATE: Users can only update their own farms
CREATE POLICY "Users can update their own farms"
    ON public.farms FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- 4. DELETE: Users can only delete their own farms
CREATE POLICY "Users can delete their own farms"
    ON public.farms FOR DELETE
    USING (auth.uid() = user_id);

-- Index for speedy queries by user
CREATE INDEX IF NOT EXISTS idx_farms_user_id ON public.farms(user_id);
