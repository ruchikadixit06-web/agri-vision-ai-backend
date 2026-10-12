-- 1. Users Table (Authentication & Roles)
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'farmer' CHECK (role IN ('farmer', 'government', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Farms Table
CREATE TABLE IF NOT EXISTS farms (
    farm_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    farm_name VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    district VARCHAR(50) NOT NULL,
    area_acres NUMERIC(8, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Yield Predictions & Historical Data Table
CREATE TABLE IF NOT EXISTS yield_records (
    record_id SERIAL PRIMARY KEY,
    farm_id INT REFERENCES farms(farm_id) ON DELETE CASCADE,
    crop_type VARCHAR(50) NOT NULL,
    predicted_yield NUMERIC(10, 2),
    actual_yield NUMERIC(10, 2),
    season VARCHAR(20),
    year INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Crop Insurance Table
CREATE TABLE IF NOT EXISTS insurance_policies (
    policy_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    farm_id INT REFERENCES farms(farm_id) ON DELETE CASCADE,
    policy_number VARCHAR(50) UNIQUE NOT NULL,
    crop_type VARCHAR(50) NOT NULL,
    coverage_amount NUMERIC(12, 2) NOT NULL,
    claim_status VARCHAR(20) DEFAULT 'Pending' CHECK (claim_status IN ('Pending', 'Approved', 'Rejected')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);