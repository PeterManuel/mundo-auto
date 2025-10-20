-- Add admin and demo users
INSERT INTO users (id, email, hashed_password, first_name, last_name, is_superuser) 
VALUES 
    ('00000000-0000-0000-0000-000000000001', 'admin@mundoauto.com', '$2b$12$QjwBGxYYC52.kTbh4woMeOgK1KLQuXtkxz9yN6Vd4eBJQ3aQ9A3A2', 'Admin', 'User', TRUE)
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (id, email, hashed_password, first_name, last_name, phone_number, address) 
VALUES 
    ('00000000-0000-0000-0000-000000000002', 'demo@mundoauto.com', '$2b$12$QjwBGxYYC52.kTbh4woMeOgK1KLQuXtkxz9yN6Vd4eBJQ3aQ9A3A2', 'Demo', 'User', '123456789', '123 Main St, Demo City')
ON CONFLICT (email) DO NOTHING;

-- Add system settings
INSERT INTO system_settings (key, value, description)
VALUES 
    ('store_name', 'MundoAuto', 'Nome da loja'),
    ('store_email', 'info@mundoauto.com', 'Email de contacto'),
    ('store_phone', '+244 923 456 789', 'Telefone de contacto'),
    ('store_address', 'Av. 21 de Janeiro, Luanda, Angola', 'Endereço físico'),
    ('currency', 'AOA', 'Moeda utilizada na loja'),
    ('tax_rate', '14', 'Taxa de IVA em percentagem'),
    ('shipping_fee', '2500', 'Taxa de envio padrão em AOA'),
    ('free_shipping_threshold', '50000', 'Valor mínimo para envio gratuito')
ON CONFLICT (key) DO NOTHING;

-- Note: The passwords for both users are 'password123'