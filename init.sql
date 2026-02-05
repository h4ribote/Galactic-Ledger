
-- Users Table
CREATE TABLE users (
    id BIGINT NOT NULL,
    username VARCHAR(100),
    avatar_url VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    PRIMARY KEY (id)
);

CREATE INDEX ix_users_id ON users (id);

-- Planets Table
CREATE TABLE planets (
    id INTEGER NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    slots INTEGER NOT NULL,
    temperature INTEGER NOT NULL,
    gravity INTEGER NOT NULL,
    owner_id BIGINT,
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
    volume INTEGER NOT NULL,
    PRIMARY KEY (id)
);

CREATE INDEX ix_items_id ON items (id);
CREATE UNIQUE INDEX ix_items_name ON items (name);

-- Fleets Table
CREATE TABLE fleets (
    id INTEGER NOT NULL AUTO_INCREMENT,
    owner_id BIGINT NOT NULL,
    name VARCHAR(100) NOT NULL,
    location_planet_id INTEGER,
    destination_planet_id INTEGER,
    arrival_time DATETIME,
    status VARCHAR(20) DEFAULT 'IDLE',
    cargo_capacity INTEGER DEFAULT 100000,
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
-- Balances Table
CREATE TABLE balances (
    id INTEGER NOT NULL AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    currency_type VARCHAR(10) NOT NULL, -- CRED, IND, TECH, MIL, VOID
    amount DECIMAL(26, 0) DEFAULT 0,
    PRIMARY KEY (id),
    FOREIGN KEY(user_id) REFERENCES users (id),
    UNIQUE (user_id, currency_type)
);

CREATE INDEX ix_balances_user ON balances (user_id);

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
    issuer_id BIGINT NOT NULL,
    contractor_id BIGINT,
    origin_planet_id INTEGER NOT NULL,
    destination_planet_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    currency_type VARCHAR(10) DEFAULT 'CRED',
    reward_amount DECIMAL(26, 0) NOT NULL,
    collateral_amount DECIMAL(26, 0) NOT NULL,
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
