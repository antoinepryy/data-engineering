-- Script d'initialisation de la base de données POI
-- Module 3 - Formation Data Engineering

-- Extension pour les fonctions géographiques
CREATE EXTENSION IF NOT EXISTS postgis;

-- Table principale des POI
CREATE TABLE IF NOT EXISTS pois (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(100),
    name_fr VARCHAR(500) NOT NULL,
    name_en VARCHAR(500),
    name_es VARCHAR(500),
    name_de VARCHAR(500),
    
    -- Statut
    closed BOOLEAN DEFAULT FALSE,
    display BOOLEAN DEFAULT TRUE,
    
    -- Classification
    types TEXT[],
    tags TEXT[],
    
    -- Localisation
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    geom GEOMETRY(Point, 4326),
    
    -- Adresse
    city VARCHAR(200),
    zip_code VARCHAR(10),
    department VARCHAR(100),
    region VARCHAR(100),
    country VARCHAR(100) DEFAULT 'France',
    street_address TEXT,
    
    -- Métadonnées
    source_name VARCHAR(100),
    source_reference VARCHAR(100),
    sourcing_level INTEGER DEFAULT 1,
    
    -- Données JSON complètes
    raw_data JSONB,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_sync_at TIMESTAMP
);

-- Index pour les recherches
CREATE INDEX IF NOT EXISTS idx_pois_name ON pois(name_fr);
CREATE INDEX IF NOT EXISTS idx_pois_source ON pois(source_name, source_reference);
CREATE INDEX IF NOT EXISTS idx_pois_region ON pois(region);
CREATE INDEX IF NOT EXISTS idx_pois_types ON pois USING GIN(types);
CREATE INDEX IF NOT EXISTS idx_pois_tags ON pois USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_pois_geom ON pois USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_pois_raw_data ON pois USING GIN(raw_data);

-- Table des sources
CREATE TABLE IF NOT EXISTS poi_sources (
    id SERIAL PRIMARY KEY,
    poi_id INTEGER REFERENCES pois(id) ON DELETE CASCADE,
    source_name VARCHAR(100) NOT NULL,
    source_reference VARCHAR(100) NOT NULL,
    last_update TIMESTAMP,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(poi_id, source_name, source_reference)
);

-- Table de l'historique des agrégations
CREATE TABLE IF NOT EXISTS poi_aggregations (
    id SERIAL PRIMARY KEY,
    poi_id INTEGER REFERENCES pois(id) ON DELETE CASCADE,
    merged_poi_ids INTEGER[],
    aggregation_method VARCHAR(50),
    similarity_score DOUBLE PRECISION,
    aggregation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSONB
);

-- Table des métriques ETL
CREATE TABLE IF NOT EXISTS etl_metrics (
    id SERIAL PRIMARY KEY,
    run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dag_id VARCHAR(100),
    run_id VARCHAR(100),
    
    -- Métriques d'extraction
    extracted_count INTEGER,
    extraction_errors INTEGER,
    
    -- Métriques de transformation
    normalized_count INTEGER,
    normalization_errors INTEGER,
    
    -- Métriques de validation
    validated_count INTEGER,
    validation_errors INTEGER,
    validation_rate DOUBLE PRECISION,
    
    -- Métriques de chargement
    loaded_count INTEGER,
    load_errors INTEGER,
    
    -- Métriques de déduplication
    duplicates_detected INTEGER,
    duplicates_merged INTEGER,
    reduction_rate DOUBLE PRECISION,
    
    -- Détails par source
    source_metrics JSONB,
    
    -- Durée
    duration_seconds INTEGER,
    status VARCHAR(50)
);

-- Vue pour les statistiques globales
CREATE OR REPLACE VIEW poi_stats AS
SELECT 
    COUNT(*) as total_pois,
    COUNT(DISTINCT source_name) as total_sources,
    COUNT(DISTINCT region) as total_regions,
    COUNT(*) FILTER (WHERE closed = TRUE) as closed_pois,
    COUNT(*) FILTER (WHERE display = FALSE) as hidden_pois,
    AVG(array_length(types, 1)) as avg_types_per_poi,
    AVG(array_length(tags, 1)) as avg_tags_per_poi
FROM pois;

-- Vue pour les statistiques par source
CREATE OR REPLACE VIEW poi_stats_by_source AS
SELECT 
    source_name,
    COUNT(*) as poi_count,
    COUNT(*) FILTER (WHERE closed = TRUE) as closed_count,
    COUNT(DISTINCT region) as regions_count,
    MIN(last_sync_at) as oldest_sync,
    MAX(last_sync_at) as latest_sync
FROM pois
GROUP BY source_name
ORDER BY poi_count DESC;

-- Vue pour les statistiques par région
CREATE OR REPLACE VIEW poi_stats_by_region AS
SELECT 
    region,
    COUNT(*) as poi_count,
    COUNT(DISTINCT source_name) as sources_count,
    array_agg(DISTINCT unnest(types)) as types
FROM pois
WHERE region IS NOT NULL
GROUP BY region
ORDER BY poi_count DESC;

-- Fonction pour mettre à jour le timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour mettre à jour updated_at
DROP TRIGGER IF EXISTS trigger_pois_updated_at ON pois;
CREATE TRIGGER trigger_pois_updated_at
    BEFORE UPDATE ON pois
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Fonction pour mettre à jour le point géographique
CREATE OR REPLACE FUNCTION update_geom()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.latitude IS NOT NULL AND NEW.longitude IS NOT NULL THEN
        NEW.geom = ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour le point géographique
DROP TRIGGER IF EXISTS trigger_pois_geom ON pois;
CREATE TRIGGER trigger_pois_geom
    BEFORE INSERT OR UPDATE OF latitude, longitude ON pois
    FOR EACH ROW
    EXECUTE FUNCTION update_geom();

-- Données d'exemple pour les tests
INSERT INTO pois (name_fr, types, tags, latitude, longitude, city, region, source_name, source_reference)
VALUES 
    ('Tour Eiffel', ARRAY['sites'], ARRAY['sites_monument'], 48.8584, 2.2945, 'Paris', 'Ile-de-France', 'Datatourisme', 'DT12345'),
    ('Château de Versailles', ARRAY['sites'], ARRAY['sites_monument_castle'], 48.8049, 2.1204, 'Versailles', 'Ile-de-France', 'Datatourisme', 'DT12346'),
    ('Parc Disneyland', ARRAY['activities'], ARRAY['activities_sites_recreationpark_themepark'], 48.8673, 2.7810, 'Coupvray', 'Ile-de-France', 'Apidae', 'AP98765')
ON CONFLICT DO NOTHING;

-- Message de confirmation
DO $$
BEGIN
    RAISE NOTICE 'Database POI initialized successfully!';
END $$;
