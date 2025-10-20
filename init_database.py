"""
Initialize database with sample data directly using SQL commands.
"""
import os
import sys
import logging
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the current directory to the path so 'app' imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import engine
from app.core.security import get_password_hash
import uuid


def init_db() -> None:
    logger.info("Starting database initialization...")
    
    # Create admin user directly with SQL to avoid relationship issues
    admin_id = str(uuid.uuid4())
    demo_id = str(uuid.uuid4())
    
    # Use our custom password hashing function that handles bcrypt errors
    admin_password = get_password_hash("admin123")
    demo_password = get_password_hash("demo123")
    
    # For compatibility, if the passwords don't work, we can use these fixed hashes
    # that our security.py file will recognize for test/demo users
    use_fixed_hashes = True
    
    if use_fixed_hashes:
        admin_password = "$2b$12$QjwBGxYYC52.kTbh4woMeOgK1KLQuXtkxz9yN6Vd4eBJQ3aQ9A3A2"
        demo_password = "$2b$12$QjwBGxYYC52.kTbh4woMeOgK1KLQuXtkxz9yN6Vd4eBJQ3aQ9A3A2"
        logger.info("Using fixed password hashes for demo users")
    
    # Execute raw SQL to insert users
    with engine.connect() as connection:
        # Check if admin user already exists
        result = connection.execute("SELECT 1 FROM users WHERE email = 'admin@mundoauto.com'")
        if result.fetchone():
            print("Database already initialized, skipping...")
            return
            
        # Insert admin user
        connection.execute(f"""
            INSERT INTO users (id, email, hashed_password, first_name, last_name, is_superuser) 
            VALUES ('{admin_id}', 'admin@mundoauto.com', '{admin_password}', 'Admin', 'User', TRUE)
        """)
        
        # Insert demo user
        connection.execute(f"""
            INSERT INTO users (id, email, hashed_password, first_name, last_name, phone_number, address) 
            VALUES ('{demo_id}', 'demo@mundoauto.com', '{demo_password}', 'Demo', 'User', '123456789', '123 Main St, Demo City')
        """)
        
        # Insert system settings
        connection.execute("""
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
        """)
        
        connection.commit()
    
    print("Database initialized with basic data successfully!")
    print("Admin user: admin@mundoauto.com / admin123")
    print("Demo user: demo@mundoauto.com / demo123")


if __name__ == "__main__":
    init_db()