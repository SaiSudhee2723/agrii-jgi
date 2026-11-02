-- ============================================================================
-- GEOSENSE SMART AGRICULTURE DATABASE SCHEMA
-- PostgreSQL schema for Supabase with Row Level Security (RLS)
-- ============================================================================

-- 1. Enable Necessary Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- 2. User Profiles & Farms
-- ============================================================================

-- Profiles table: Extends Supabase auth.users
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    phone TEXT,
    avatar_url TEXT,
    role TEXT NOT NULL DEFAULT 'farmer' CHECK (role IN ('farmer', 'agronomist', 'researcher', 'admin')),
    region TEXT,
    preferred_language TEXT DEFAULT 'en',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- Farms table
CREATE TABLE IF NOT EXISTS public.farms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    location_name TEXT,
    latitude NUMERIC(9, 6),
    longitude NUMERIC(9, 6),
    area_acres NUMERIC(8, 2) NOT NULL DEFAULT 1.0,
    soil_type TEXT,
    primary_crops TEXT[] DEFAULT '{}',
    irrigation_source TEXT DEFAULT 'borewell',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- ============================================================================
-- 3. Module 1: Soil Analysis
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.soil_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    farm_id UUID REFERENCES public.farms(id) ON DELETE SET NULL,
    image_url TEXT,
    quality_status TEXT NOT NULL CHECK (quality_status IN ('passed', 'suboptimal', 'rejected')),
    quality_details JSONB NOT NULL DEFAULT '{}'::jsonb, -- blur_score, glare_ratio, lighting_ok, resolution
    color_metrics JSONB NOT NULL DEFAULT '{}'::jsonb,   -- mean_rgb, mean_hsv, estimated_hue
    soil_texture_estimate TEXT,                         -- e.g. 'Loamy / Sandy / Clay'
    soil_condition TEXT NOT NULL,                       -- e.g. 'Healthy surface organic layer', 'Dry / Low moisture'
    nitrogen_level TEXT DEFAULT 'Laboratory Test Required',
    phosphorus_level TEXT DEFAULT 'Laboratory Test Required',
    potassium_level TEXT DEFAULT 'Laboratory Test Required',
    scientific_disclaimer TEXT NOT NULL DEFAULT 'RGB mobile imagery alone cannot quantitatively measure chemical NPK concentrations. Laboratory chemical assay is strongly recommended.',
    lab_test_recommended BOOLEAN NOT NULL DEFAULT true,
    recommendations TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- ============================================================================
-- 4. Module 2: Crop Recommendations
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.crop_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    farm_id UUID REFERENCES public.farms(id) ON DELETE SET NULL,
    input_nitrogen NUMERIC(7, 2) NOT NULL,
    input_phosphorus NUMERIC(7, 2) NOT NULL,
    input_potassium NUMERIC(7, 2) NOT NULL,
    input_temperature NUMERIC(5, 2) NOT NULL,
    input_humidity NUMERIC(5, 2) NOT NULL,
    input_ph NUMERIC(4, 2) NOT NULL,
    input_rainfall NUMERIC(7, 2) NOT NULL,
    primary_recommendation TEXT NOT NULL,
    confidence_score NUMERIC(5, 4) NOT NULL,
    alternative_crops JSONB NOT NULL DEFAULT '[]'::jsonb, -- list of {crop, probability, suitability}
    growing_conditions JSONB NOT NULL DEFAULT '{}'::jsonb,
    farming_advice TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- ============================================================================
-- 5. Module 3: Smart Irrigation Records
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.irrigation_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    farm_id UUID REFERENCES public.farms(id) ON DELETE SET NULL,
    crop_name TEXT NOT NULL,
    growth_stage TEXT NOT NULL CHECK (growth_stage IN ('initial', 'vegetative', 'flowering', 'yield_formation', 'ripening')),
    soil_moisture_percentage NUMERIC(5, 2) NOT NULL,
    temperature_celsius NUMERIC(5, 2),
    humidity_percentage NUMERIC(5, 2),
    forecast_rainfall_mm NUMERIC(6, 2) NOT NULL DEFAULT 0.0,
    evapotranspiration_mm NUMERIC(6, 2) NOT NULL DEFAULT 0.0,
    water_required_liters_per_acre NUMERIC(10, 2) NOT NULL,
    irrigation_needed BOOLEAN NOT NULL,
    schedule_recommendation TEXT NOT NULL,
    water_saving_tips TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- ============================================================================
-- 6. Module 5: Market Intelligence
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.market_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commodity TEXT NOT NULL,
    variety TEXT DEFAULT 'Common',
    mandi_name TEXT NOT NULL,
    district TEXT NOT NULL,
    state TEXT NOT NULL,
    min_price NUMERIC(10, 2) NOT NULL,
    max_price NUMERIC(10, 2) NOT NULL,
    modal_price NUMERIC(10, 2) NOT NULL,
    unit TEXT NOT NULL DEFAULT 'INR / Quintal',
    price_date DATE NOT NULL DEFAULT CURRENT_DATE,
    is_live BOOLEAN NOT NULL DEFAULT false, -- Clearly labels demo vs live verified mandi data
    source_attribution TEXT DEFAULT 'Agmarknet / Agricultural Produce Market Committee',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- ============================================================================
-- 7. Module 6: Farmer Community & Messaging
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.community_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'general' CHECK (category IN ('general', 'soil_health', 'pest_control', 'crop_advice', 'market', 'equipment')),
    image_url TEXT,
    likes_count INTEGER NOT NULL DEFAULT 0,
    comments_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE TABLE IF NOT EXISTS public.community_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES public.community_posts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE TABLE IF NOT EXISTS public.post_likes (
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    post_id UUID NOT NULL REFERENCES public.community_posts(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    PRIMARY KEY (user_id, post_id)
);

CREATE TABLE IF NOT EXISTS public.messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    receiver_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'info' CHECK (type IN ('info', 'weather_alert', 'market_alert', 'community', 'system')),
    link_url TEXT,
    is_read BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- ============================================================================
-- 8. Performance Indexes
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_farms_user_id ON public.farms(user_id);
CREATE INDEX IF NOT EXISTS idx_soil_analysis_user ON public.soil_analysis(user_id);
CREATE INDEX IF NOT EXISTS idx_crop_rec_user ON public.crop_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_irrigation_user ON public.irrigation_records(user_id);
CREATE INDEX IF NOT EXISTS idx_market_commodity_date ON public.market_prices(commodity, price_date DESC);
CREATE INDEX IF NOT EXISTS idx_market_mandi ON public.market_prices(mandi_name, state);
CREATE INDEX IF NOT EXISTS idx_posts_created ON public.community_posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_posts_user ON public.community_posts(user_id);
CREATE INDEX IF NOT EXISTS idx_comments_post ON public.community_comments(post_id);
CREATE INDEX IF NOT EXISTS idx_messages_pair ON public.messages(sender_id, receiver_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON public.notifications(user_id, is_read, created_at DESC);

-- ============================================================================
-- 9. Automatic Profile Creation on Signup (Trigger)
-- ============================================================================

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name, avatar_url)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email),
        COALESCE(NEW.raw_user_meta_data->>'avatar_url', '')
    )
    ON CONFLICT (id) DO UPDATE SET
        full_name = EXCLUDED.full_name,
        updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Trigger for post counters
CREATE OR REPLACE FUNCTION public.update_post_counters()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        UPDATE public.community_posts SET comments_count = comments_count + 1 WHERE id = NEW.post_id;
    ELSIF (TG_OP = 'DELETE') THEN
        UPDATE public.community_posts SET comments_count = GREATEST(comments_count - 1, 0) WHERE id = OLD.post_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_comment_change ON public.community_comments;
CREATE TRIGGER on_comment_change
    AFTER INSERT OR DELETE ON public.community_comments
    FOR EACH ROW EXECUTE FUNCTION public.update_post_counters();

-- ============================================================================
-- 10. Row Level Security (RLS) Policies
-- ============================================================================

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.farms ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.soil_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.crop_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.irrigation_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.market_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.community_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.community_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.post_likes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

-- Profiles: Public can view, owner can update
CREATE POLICY "Public profiles are viewable by everyone" ON public.profiles
    FOR SELECT USING (true);
CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- Farms: Owners have full control
CREATE POLICY "Users can view own farms" ON public.farms
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own farms" ON public.farms
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own farms" ON public.farms
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own farms" ON public.farms
    FOR DELETE USING (auth.uid() = user_id);

-- Soil Analysis: Owners have full control
CREATE POLICY "Users can view own soil analyses" ON public.soil_analysis
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own soil analysis" ON public.soil_analysis
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete own soil analysis" ON public.soil_analysis
    FOR DELETE USING (auth.uid() = user_id);

-- Crop Recommendations: Owners have full control
CREATE POLICY "Users can view own crop recommendations" ON public.crop_recommendations
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own crop recommendations" ON public.crop_recommendations
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Irrigation: Owners have full control
CREATE POLICY "Users can view own irrigation records" ON public.irrigation_records
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own irrigation records" ON public.irrigation_records
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Market Prices: Publicly readable by all authenticated & anonymous users
CREATE POLICY "Market prices are viewable by all" ON public.market_prices
    FOR SELECT USING (true);

-- Community Posts: Viewable by all, insertable/editable/deletable by author
CREATE POLICY "Community posts are viewable by everyone" ON public.community_posts
    FOR SELECT USING (true);
CREATE POLICY "Authenticated users can create posts" ON public.community_posts
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own posts" ON public.community_posts
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own posts" ON public.community_posts
    FOR DELETE USING (auth.uid() = user_id);

-- Comments: Viewable by all, author can create/delete
CREATE POLICY "Comments are viewable by everyone" ON public.community_comments
    FOR SELECT USING (true);
CREATE POLICY "Authenticated users can create comments" ON public.community_comments
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete own comments" ON public.community_comments
    FOR DELETE USING (auth.uid() = user_id);

-- Likes: Users can like/unlike posts
CREATE POLICY "Post likes are viewable by everyone" ON public.post_likes
    FOR SELECT USING (true);
CREATE POLICY "Authenticated users can manage own likes" ON public.post_likes
    FOR ALL USING (auth.uid() = user_id);

-- Messages: Only sender and receiver can see messages
CREATE POLICY "Users can view sent and received messages" ON public.messages
    FOR SELECT USING (auth.uid() = sender_id OR auth.uid() = receiver_id);
CREATE POLICY "Users can send messages" ON public.messages
    FOR INSERT WITH CHECK (auth.uid() = sender_id);
CREATE POLICY "Receivers can update message read status" ON public.messages
    FOR UPDATE USING (auth.uid() = receiver_id);

-- Notifications: Only owner can view and mark as read
CREATE POLICY "Users can view own notifications" ON public.notifications
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own notifications" ON public.notifications
    FOR UPDATE USING (auth.uid() = user_id);

-- ============================================================================
-- 11. Storage Bucket Setup (execute in Supabase SQL editor or dashboard)
-- ============================================================================
-- INSERT INTO storage.buckets (id, name, public) VALUES ('soil-images', 'soil-images', true) ON CONFLICT DO NOTHING;
-- INSERT INTO storage.buckets (id, name, public) VALUES ('community-media', 'community-media', true) ON CONFLICT DO NOTHING;

