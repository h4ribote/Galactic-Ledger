
-- Users Table
CREATE TABLE users (
    id INTEGER NOT NULL AUTO_INCREMENT,
    discord_id VARCHAR(50) NOT NULL,
    username VARCHAR(100),
    avatar_url VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_users_discord_id ON users (discord_id);
CREATE INDEX ix_users_id ON users (id);

-- Planets Table
CREATE TABLE planets (
    id INTEGER NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    x FLOAT NOT NULL,
    y FLOAT NOT NULL,
    slots INTEGER NOT NULL,
    temperature FLOAT NOT NULL,
    gravity FLOAT NOT NULL,
    owner_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    PRIMARY KEY (id),
    FOREIGN KEY(owner_id) REFERENCES users (id)
);

CREATE INDEX ix_planets_id ON planets (id);
CREATE INDEX ix_planets_name ON planets (name);

-- Items Table
CREATE TABLE items (
    id INTEGER NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    tier INTEGER NOT NULL,
    volume FLOAT NOT NULL,
    PRIMARY KEY (id)
);

CREATE INDEX ix_items_id ON items (id);
CREATE UNIQUE INDEX ix_items_name ON items (name);

-- Fleets Table
CREATE TABLE fleets (
    id INTEGER NOT NULL AUTO_INCREMENT,
    owner_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    location_planet_id INTEGER,
    destination_planet_id INTEGER,
    arrival_time DATETIME,
    status VARCHAR(20) DEFAULT 'IDLE',
    cargo_capacity FLOAT DEFAULT 100.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    PRIMARY KEY (id),
    FOREIGN KEY(owner_id) REFERENCES users (id),
    FOREIGN KEY(location_planet_id) REFERENCES planets (id),
    FOREIGN KEY(destination_planet_id) REFERENCES planets (id)
);

CREATE INDEX ix_fleets_id ON fleets (id);
CREATE INDEX ix_fleets_owner ON fleets (owner_id);

-- Inventories Table
CREATE TABLE inventories (
    id INTEGER NOT NULL AUTO_INCREMENT,
    planet_id INTEGER,
    fleet_id INTEGER,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(item_id) REFERENCES items (id),
    FOREIGN KEY(planet_id) REFERENCES planets (id),
    FOREIGN KEY(fleet_id) REFERENCES fleets (id)
);

CREATE INDEX ix_inventories_id ON inventories (id);

-- Wallets Table
CREATE TABLE wallets (
    id INTEGER NOT NULL AUTO_INCREMENT,
    user_id INTEGER NOT NULL,
    balance FLOAT NOT NULL,
    updated_at DATETIME,
    PRIMARY KEY (id),
    FOREIGN KEY(user_id) REFERENCES users (id),
    UNIQUE (user_id)
);

CREATE INDEX ix_wallets_id ON wallets (id);

-- Buildings Table
CREATE TABLE buildings (
    id INTEGER NOT NULL AUTO_INCREMENT,
    planet_id INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    finished_at DATETIME,
    PRIMARY KEY (id),
    FOREIGN KEY(planet_id) REFERENCES planets (id)
);

CREATE INDEX ix_buildings_id ON buildings (id);

-- Contracts Table
CREATE TABLE contracts (
    id INTEGER NOT NULL AUTO_INCREMENT,
    issuer_id INTEGER NOT NULL,
    contractor_id INTEGER,
    origin_planet_id INTEGER NOT NULL,
    destination_planet_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    reward_amount FLOAT NOT NULL,
    collateral_amount FLOAT NOT NULL,
    duration_seconds INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    accepted_at DATETIME,
    deadline DATETIME,
    status VARCHAR(20) DEFAULT 'OPEN',
    PRIMARY KEY (id),
    FOREIGN KEY(issuer_id) REFERENCES users (id),
    FOREIGN KEY(contractor_id) REFERENCES users (id),
    FOREIGN KEY(origin_planet_id) REFERENCES planets (id),
    FOREIGN KEY(destination_planet_id) REFERENCES planets (id),
    FOREIGN KEY(item_id) REFERENCES items (id)
);

CREATE INDEX ix_contracts_id ON contracts (id);
CREATE INDEX ix_contracts_issuer ON contracts (issuer_id);
CREATE INDEX ix_contracts_contractor ON contracts (contractor_id);
