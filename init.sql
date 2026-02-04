
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

-- Inventories Table
CREATE TABLE inventories (
    id INTEGER NOT NULL AUTO_INCREMENT,
    planet_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(item_id) REFERENCES items (id),
    FOREIGN KEY(planet_id) REFERENCES planets (id)
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
