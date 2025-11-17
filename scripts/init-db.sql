-- Evid Flow Database Initialization

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';

-- Create initial admin user (optional)
-- INSERT INTO users (email, hashed_password, full_name, role, is_verified, is_active) 
-- VALUES (
--     'admin@evidflow.com',
--     -- Password: Admin123! (hashed)
--     '$2b$12$LQv3c1yqBWVHxkd0L8k4CuBv8zZ8YRcHjqZ2VcQFpDc6pQrZ6YbW',
--     'System Administrator',
--     'super_admin',
--     true,
--     true
-- );

COMMIT;
