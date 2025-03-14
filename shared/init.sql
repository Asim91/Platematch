-- Create tables based on schema
CREATE TABLE IF NOT EXISTS auctions (
    auction_id VARCHAR(10) PRIMARY KEY,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS registrations (
    id SERIAL PRIMARY KEY,
    auction_id VARCHAR(10) REFERENCES auctions(auction_id),
    lot_number INTEGER NOT NULL,
    registration VARCHAR(50) NOT NULL,
    starting_price DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);