-- do we need to abstract away the tokens as an organization so multiple users can use the same tokens?
-- TODO should we force email to be unique?
CREATE TABLE IF NOT EXISTS users (
    email TEXT UNIQUE NOT NULL,
    password TEXT
);

-- DROP INDEX IF EXISTS users_index;
CREATE INDEX IF NOT EXISTS users_index ON users(email,password);


CREATE TABLE IF NOT EXISTS pw_reset (
    email TEXT UNIQUE NOT NULL,
    token TEXT NOT NULL,
    reset_time INT NOT NULL
);
