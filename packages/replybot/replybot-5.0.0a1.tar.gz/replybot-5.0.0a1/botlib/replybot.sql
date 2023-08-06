CREATE TABLE entry (
    id INTEGER NOT NULL,
    address TEXT NOT NULL,
    last_sent TIMESTAMP NOT NULL,
    key TEXT NOT NULL,
    PRIMARY KEY (id)
    );


CREATE TABLE whitelist (
    id INTEGER NOT NULL,
    matcher TEXT NOT NULL,
    is_pattern INT NOT NULL,
    PRIMARY KEY (id)
    );


CREATE TABLE notice (
    id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    uri TEXT NOT NULL,
    retrieved TIMESTAMP NOT NULL,
    PRIMARY KEY (id)
    );


CREATE TABLE version (
    id INTEGER NOT NULL,
    component TEXT NOT NULL,
    version INT NOT NULL,
    PRIMARY KEY (id)
    );
