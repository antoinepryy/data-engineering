-- Script d'initialisation de la base de données PostgreSQL pour DBT
-- Module 3 - Formation Data Engineering

-- Création des schémas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS intermediate;
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS dev;
CREATE SCHEMA IF NOT EXISTS prod;
CREATE SCHEMA IF NOT EXISTS snapshots;

-- Permissions
GRANT ALL ON SCHEMA raw TO dbt_user;
GRANT ALL ON SCHEMA staging TO dbt_user;
GRANT ALL ON SCHEMA intermediate TO dbt_user;
GRANT ALL ON SCHEMA marts TO dbt_user;
GRANT ALL ON SCHEMA dev TO dbt_user;
GRANT ALL ON SCHEMA prod TO dbt_user;
GRANT ALL ON SCHEMA snapshots TO dbt_user;

-- ============================================================================
-- TABLES SOURCE (RAW DATA)
-- ============================================================================

-- Table des clients
CREATE TABLE IF NOT EXISTS raw.customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des produits
CREATE TABLE IF NOT EXISTS raw.products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(100),
    brand VARCHAR(100),
    price DECIMAL(10, 2),
    cost DECIMAL(10, 2),
    weight DECIMAL(10, 3),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    discontinued_at TIMESTAMP
);

-- Table des commandes
CREATE TABLE IF NOT EXISTS raw.orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER,
    order_date TIMESTAMP,
    status VARCHAR(50),
    total_amount DECIMAL(10, 2),
    payment_method VARCHAR(50),
    shipping_address TEXT,
    shipping_city VARCHAR(100),
    shipping_country VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des lignes de commande
CREATE TABLE IF NOT EXISTS raw.order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    unit_price DECIMAL(10, 2),
    discount_amount DECIMAL(10, 2),
    tax_amount DECIMAL(10, 2),
    total_amount DECIMAL(10, 2)
);

-- Table des paiements
CREATE TABLE IF NOT EXISTS raw.payments (
    payment_id SERIAL PRIMARY KEY,
    order_id INTEGER,
    payment_date TIMESTAMP,
    payment_method VARCHAR(50),
    amount DECIMAL(10, 2),
    status VARCHAR(50),
    transaction_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des événements web
CREATE TABLE IF NOT EXISTS raw.web_events (
    event_id SERIAL PRIMARY KEY,
    session_id VARCHAR(100),
    customer_id INTEGER,
    event_type VARCHAR(50),
    event_timestamp TIMESTAMP,
    page_url TEXT,
    referrer_url TEXT,
    device_type VARCHAR(50),
    browser VARCHAR(50),
    ip_address VARCHAR(45),
    country VARCHAR(100),
    properties JSONB
);

-- Table des campagnes marketing
CREATE TABLE IF NOT EXISTS raw.marketing_campaigns (
    campaign_id SERIAL PRIMARY KEY,
    campaign_name VARCHAR(255),
    channel VARCHAR(50),
    start_date DATE,
    end_date DATE,
    budget DECIMAL(10, 2),
    target_audience TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des attributions marketing
CREATE TABLE IF NOT EXISTS raw.marketing_attributions (
    attribution_id SERIAL PRIMARY KEY,
    order_id INTEGER,
    campaign_id INTEGER,
    attribution_type VARCHAR(50),
    attribution_weight DECIMAL(3, 2),
    touchpoint_date TIMESTAMP
);

-- ============================================================================
-- INSERTION DE DONNÉES DE DÉMONSTRATION
-- ============================================================================

-- Insertion de clients
INSERT INTO raw.customers (first_name, last_name, email, phone, address, city, country) VALUES
('Jean', 'Dupont', 'jean.dupont@email.com', '+33612345678', '123 Rue de la Paix', 'Paris', 'France'),
('Marie', 'Martin', 'marie.martin@email.com', '+33687654321', '456 Avenue des Champs', 'Lyon', 'France'),
('Pierre', 'Bernard', 'pierre.bernard@email.com', '+33611223344', '789 Boulevard Victor Hugo', 'Marseille', 'France'),
('Sophie', 'Thomas', 'sophie.thomas@email.com', '+33699887766', '321 Rue de la République', 'Toulouse', 'France'),
('Luc', 'Robert', 'luc.robert@email.com', '+33655443322', '654 Place Bellecour', 'Lyon', 'France'),
('Emma', 'Petit', 'emma.petit@email.com', '+33677889900', '987 Rue Saint-Honoré', 'Paris', 'France'),
('Paul', 'Durand', 'paul.durand@email.com', '+33644556677', '147 Quai de Seine', 'Paris', 'France'),
('Julie', 'Leroy', 'julie.leroy@email.com', '+33633221100', '258 Cours Mirabeau', 'Aix-en-Provence', 'France'),
('Marc', 'Moreau', 'marc.moreau@email.com', '+33666778899', '369 Rue de la Liberté', 'Nantes', 'France'),
('Laura', 'Simon', 'laura.simon@email.com', '+33622334455', '741 Avenue Jean Jaurès', 'Lille', 'France');

-- Insertion de produits
INSERT INTO raw.products (product_name, category, brand, price, cost, weight, status) VALUES
('Ordinateur Portable Pro', 'Électronique', 'TechBrand', 1299.99, 850.00, 2.500, 'active'),
('Smartphone X12', 'Électronique', 'PhoneCorp', 899.99, 450.00, 0.200, 'active'),
('Casque Bluetooth Premium', 'Audio', 'SoundMax', 199.99, 75.00, 0.350, 'active'),
('Tablette Ultra', 'Électronique', 'TechBrand', 599.99, 320.00, 0.500, 'active'),
('Montre Connectée Sport', 'Wearables', 'FitTech', 299.99, 120.00, 0.080, 'active'),
('Enceinte Intelligente', 'Audio', 'SmartHome', 149.99, 65.00, 1.200, 'active'),
('Clavier Mécanique RGB', 'Accessoires', 'GameGear', 129.99, 55.00, 0.900, 'active'),
('Souris Gaming Pro', 'Accessoires', 'GameGear', 79.99, 30.00, 0.120, 'active'),
('Webcam 4K', 'Accessoires', 'StreamTech', 149.99, 60.00, 0.200, 'active'),
('Chargeur Sans Fil', 'Accessoires', 'PowerPlus', 39.99, 15.00, 0.150, 'active'),
('Écouteurs Sport', 'Audio', 'FitTech', 89.99, 35.00, 0.050, 'discontinued'),
('Hub USB-C 7-en-1', 'Accessoires', 'ConnectPro', 69.99, 25.00, 0.100, 'active');

-- Insertion de commandes
INSERT INTO raw.orders (customer_id, order_date, status, total_amount, payment_method, shipping_address, shipping_city, shipping_country) VALUES
(1, '2024-01-15 10:30:00', 'completed', 1599.98, 'credit_card', '123 Rue de la Paix', 'Paris', 'France'),
(2, '2024-01-16 14:45:00', 'completed', 899.99, 'paypal', '456 Avenue des Champs', 'Lyon', 'France'),
(3, '2024-01-17 09:15:00', 'completed', 329.98, 'credit_card', '789 Boulevard Victor Hugo', 'Marseille', 'France'),
(1, '2024-01-18 16:20:00', 'completed', 149.99, 'credit_card', '123 Rue de la Paix', 'Paris', 'France'),
(4, '2024-01-19 11:30:00', 'processing', 1899.98, 'bank_transfer', '321 Rue de la République', 'Toulouse', 'France'),
(5, '2024-01-20 13:45:00', 'completed', 269.98, 'credit_card', '654 Place Bellecour', 'Lyon', 'France'),
(6, '2024-01-21 10:00:00', 'completed', 599.99, 'paypal', '987 Rue Saint-Honoré', 'Paris', 'France'),
(7, '2024-01-22 15:30:00', 'cancelled', 199.99, 'credit_card', '147 Quai de Seine', 'Paris', 'France'),
(8, '2024-01-23 12:15:00', 'completed', 449.97, 'credit_card', '258 Cours Mirabeau', 'Aix-en-Provence', 'France'),
(9, '2024-01-24 14:00:00', 'processing', 1299.99, 'bank_transfer', '369 Rue de la Liberté', 'Nantes', 'France');

-- Insertion de lignes de commande
INSERT INTO raw.order_items (order_id, product_id, quantity, unit_price, discount_amount, tax_amount, total_amount) VALUES
(1, 1, 1, 1299.99, 0.00, 260.00, 1559.99),
(1, 10, 1, 39.99, 0.00, 8.00, 47.99),
(2, 2, 1, 899.99, 0.00, 180.00, 1079.99),
(3, 3, 1, 199.99, 20.00, 36.00, 215.99),
(3, 7, 1, 129.99, 0.00, 26.00, 155.99),
(4, 6, 1, 149.99, 0.00, 30.00, 179.99),
(5, 1, 1, 1299.99, 0.00, 260.00, 1559.99),
(5, 5, 1, 299.99, 0.00, 60.00, 359.99),
(6, 3, 1, 199.99, 0.00, 40.00, 239.99),
(6, 12, 1, 69.99, 0.00, 14.00, 83.99),
(7, 4, 1, 599.99, 0.00, 120.00, 719.99),
(8, 3, 1, 199.99, 0.00, 40.00, 239.99),
(9, 6, 2, 149.99, 0.00, 60.00, 359.98),
(9, 8, 1, 79.99, 0.00, 16.00, 95.99),
(10, 1, 1, 1299.99, 0.00, 260.00, 1559.99);

-- Insertion de paiements
INSERT INTO raw.payments (order_id, payment_date, payment_method, amount, status, transaction_id) VALUES
(1, '2024-01-15 10:35:00', 'credit_card', 1599.98, 'completed', 'TXN001'),
(2, '2024-01-16 14:50:00', 'paypal', 899.99, 'completed', 'TXN002'),
(3, '2024-01-17 09:20:00', 'credit_card', 329.98, 'completed', 'TXN003'),
(4, '2024-01-18 16:25:00', 'credit_card', 149.99, 'completed', 'TXN004'),
(5, '2024-01-19 11:35:00', 'bank_transfer', 1899.98, 'pending', 'TXN005'),
(6, '2024-01-20 13:50:00', 'credit_card', 269.98, 'completed', 'TXN006'),
(7, '2024-01-21 10:05:00', 'paypal', 599.99, 'completed', 'TXN007'),
(8, '2024-01-22 15:35:00', 'credit_card', 199.99, 'refunded', 'TXN008'),
(9, '2024-01-23 12:20:00', 'credit_card', 449.97, 'completed', 'TXN009'),
(10, '2024-01-24 14:05:00', 'bank_transfer', 1299.99, 'pending', 'TXN010');

-- Insertion d'événements web
INSERT INTO raw.web_events (session_id, customer_id, event_type, event_timestamp, page_url, device_type, browser) VALUES
('SES001', 1, 'page_view', '2024-01-15 10:00:00', '/products/laptop-pro', 'desktop', 'Chrome'),
('SES001', 1, 'add_to_cart', '2024-01-15 10:15:00', '/products/laptop-pro', 'desktop', 'Chrome'),
('SES001', 1, 'checkout', '2024-01-15 10:25:00', '/checkout', 'desktop', 'Chrome'),
('SES002', 2, 'page_view', '2024-01-16 14:30:00', '/products/smartphone-x12', 'mobile', 'Safari'),
('SES002', 2, 'add_to_cart', '2024-01-16 14:40:00', '/products/smartphone-x12', 'mobile', 'Safari'),
('SES003', 3, 'search', '2024-01-17 09:00:00', '/search?q=headphones', 'desktop', 'Firefox'),
('SES003', 3, 'page_view', '2024-01-17 09:05:00', '/products/bluetooth-headphones', 'desktop', 'Firefox'),
('SES004', NULL, 'page_view', '2024-01-18 11:00:00', '/home', 'tablet', 'Safari'),
('SES005', 4, 'page_view', '2024-01-19 11:15:00', '/categories/electronics', 'desktop', 'Chrome'),
('SES005', 4, 'add_to_cart', '2024-01-19 11:25:00', '/products/laptop-pro', 'desktop', 'Chrome');

-- Insertion de campagnes marketing
INSERT INTO raw.marketing_campaigns (campaign_name, channel, start_date, end_date, budget, target_audience, status) VALUES
('Soldes d\'Hiver 2024', 'email', '2024-01-01', '2024-01-31', 10000.00, 'Tous les clients', 'active'),
('Promo Électronique', 'social_media', '2024-01-15', '2024-02-15', 5000.00, 'Tech enthusiasts', 'active'),
('Black Friday', 'display', '2023-11-24', '2023-11-27', 15000.00, 'Tous segments', 'completed'),
('Rentrée 2024', 'search', '2024-08-15', '2024-09-15', 8000.00, 'Étudiants', 'planned'),
('Saint-Valentin', 'email', '2024-02-01', '2024-02-14', 3000.00, 'Couples', 'planned');

-- Insertion d'attributions marketing
INSERT INTO raw.marketing_attributions (order_id, campaign_id, attribution_type, attribution_weight, touchpoint_date) VALUES
(1, 1, 'first_touch', 0.40, '2024-01-10 08:00:00'),
(1, 2, 'last_touch', 0.60, '2024-01-15 09:00:00'),
(2, 2, 'linear', 1.00, '2024-01-16 12:00:00'),
(3, 1, 'linear', 0.50, '2024-01-15 08:00:00'),
(3, 2, 'linear', 0.50, '2024-01-17 08:00:00');

-- Permissions sur toutes les tables
GRANT ALL ON ALL TABLES IN SCHEMA raw TO dbt_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA raw TO dbt_user;