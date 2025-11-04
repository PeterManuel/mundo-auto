"""
Initialize database with sample data.
"""
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.models.product import Category, Product, ProductImage
from app.models.admin import SystemSetting
from app.models.banner import Banner
from app.db.session import SessionLocal


def init_db() -> None:
    db = SessionLocal()
    
    # Check if database is already initialized
    if db.query(User).filter(User.email == "admin@mundoauto.com").first():
        print("Database already initialized, skipping...")
        return
    
    # Create default admin user
    admin_user = User(
        email="admin@mundoauto.com",
        hashed_password=get_password_hash("admin123"),
        first_name="Admin",
        last_name="User",
        is_superuser=True
    )
    db.add(admin_user)
    
    # Create demo user
    demo_user = User(
        email="demo@mundoauto.com",
        hashed_password=get_password_hash("demo123"),
        first_name="Demo",
        last_name="User",
        phone_number="123456789",
        address="123 Main St, Demo City"
    )
    db.add(demo_user)
    
    # Create categories
    categories = []
    
    # Parent categories
    engine = Category(
        name="Motor",
        slug="motor",
        description="Peças para o motor do seu carro"
    )
    db.add(engine)
    categories.append(engine)
    
    brakes = Category(
        name="Travões",
        slug="travoes",
        description="Sistema de travagem"
    )
    db.add(brakes)
    categories.append(brakes)
    
    suspension = Category(
        name="Suspensão",
        slug="suspensao",
        description="Sistema de suspensão"
    )
    db.add(suspension)
    categories.append(suspension)
    
    body = Category(
        name="Carroçaria",
        slug="carrocaria",
        description="Peças de carroçaria"
    )
    db.add(body)
    categories.append(body)
    
    electrical = Category(
        name="Sistema Elétrico",
        slug="sistema-eletrico",
        description="Componentes elétricos e eletrónicos"
    )
    db.add(electrical)
    categories.append(electrical)
    
    # Create some subcategories for Motor
    oil_filters = Category(
        name="Filtros de Óleo",
        slug="filtros-de-oleo",
        description="Filtros de óleo para diferentes marcas e modelos",
        parent_id=engine.id
    )
    db.add(oil_filters)
    
    air_filters = Category(
        name="Filtros de Ar",
        slug="filtros-de-ar",
        description="Filtros de ar para diferentes marcas e modelos",
        parent_id=engine.id
    )
    db.add(air_filters)
    
    pistons = Category(
        name="Pistões",
        slug="pistoes",
        description="Pistões para motores",
        parent_id=engine.id
    )
    db.add(pistons)
    
    # Create some subcategories for Brakes
    brake_pads = Category(
        name="Pastilhas de Travão",
        slug="pastilhas-de-travao",
        description="Pastilhas de travão para diferentes marcas e modelos",
        parent_id=brakes.id
    )
    db.add(brake_pads)
    
    brake_discs = Category(
        name="Discos de Travão",
        slug="discos-de-travao",
        description="Discos de travão para diferentes marcas e modelos",
        parent_id=brakes.id
    )
    db.add(brake_discs)
    
    # Commit to get IDs
    db.commit()
    
    # Create some products
    oil_filter = Product(
        name="Filtro de Óleo Bosch F026407006",
        slug="filtro-de-oleo-bosch-f026407006",
        description="Filtro de óleo Bosch para motores a gasolina e diesel.",
        technical_details="Diâmetro: 76mm, Altura: 85mm, Rosca: 3/4\"-16 UNF",
        price=12.99,
        sku="F026407006",
        stock_quantity=100,
        brand="Bosch",
        manufacturer="Robert Bosch GmbH",
        compatible_vehicles=["VW Golf 1.6", "VW Passat 2.0 TDI", "Audi A3 1.9 TDI"]
    )
    oil_filter.categories.append(oil_filters)
    db.add(oil_filter)
    
    # Add image to oil filter
    oil_filter_img = ProductImage(
        product_id=oil_filter.id,
        image_url="/static/images/products/oil-filter.jpg",
        alt_text="Filtro de Óleo Bosch F026407006",
        is_primary=True
    )
    db.add(oil_filter_img)
    
    # Create brake pads product
    brake_pad = Product(
        name="Pastilhas de Travão Ferodo FDB4456",
        slug="pastilhas-de-travao-ferodo-fdb4456",
        description="Pastilhas de travão de alta qualidade para veículos de passageiros.",
        technical_details="Sistema: Bosch, Comprimento: 131mm, Altura: 66mm, Espessura: 19mm",
        price=45.50,
        sku="FDB4456",
        stock_quantity=50,
        brand="Ferodo",
        manufacturer="Federal-Mogul Corporation",
        compatible_vehicles=["BMW Série 3 E90", "BMW Série 5 E60", "Mercedes Classe C W204"]
    )
    brake_pad.categories.append(brake_pads)
    db.add(brake_pad)
    
    # Add image to brake pad
    brake_pad_img = ProductImage(
        product_id=brake_pad.id,
        image_url="/static/images/products/brake-pad.jpg",
        alt_text="Pastilhas de Travão Ferodo FDB4456",
        is_primary=True
    )
    db.add(brake_pad_img)
    
    # Create brake disc product
    brake_disc = Product(
        name="Disco de Travão Brembo 09.5802.21",
        slug="disco-de-travao-brembo-09-5802-21",
        description="Disco de travão ventilado Brembo para máxima eficiência de travagem.",
        technical_details="Diâmetro: 300mm, Espessura: 28mm, Altura: 49.5mm, Furos: 5",
        price=89.99,
        sku="09.5802.21",
        stock_quantity=30,
        brand="Brembo",
        manufacturer="Brembo S.p.A.",
        compatible_vehicles=["Audi A4 B8", "Audi A5 8T", "VW Passat B6"]
    )
    brake_disc.categories.append(brake_discs)
    db.add(brake_disc)
    
    # Add image to brake disc
    brake_disc_img = ProductImage(
        product_id=brake_disc.id,
        image_url="/static/images/products/brake-disc.jpg",
        alt_text="Disco de Travão Brembo 09.5802.21",
        is_primary=True
    )
    db.add(brake_disc_img)
    
    # Create air filter product
    air_filter = Product(
        name="Filtro de Ar Mann C 2433",
        slug="filtro-de-ar-mann-c-2433",
        description="Filtro de ar Mann-Filter para máxima filtragem de poeiras e partículas.",
        technical_details="Comprimento: 213mm, Largura: 125mm, Altura: 30mm",
        price=18.50,
        sku="C 2433",
        stock_quantity=75,
        brand="Mann-Filter",
        manufacturer="Mann+Hummel GmbH",
        compatible_vehicles=["Mercedes Classe C W203", "Mercedes Classe E W211", "Mercedes CLK C209"]
    )
    air_filter.categories.append(air_filters)
    db.add(air_filter)
    
    # Add image to air filter
    air_filter_img = ProductImage(
        product_id=air_filter.id,
        image_url="/static/images/products/air-filter.jpg",
        alt_text="Filtro de Ar Mann C 2433",
        is_primary=True
    )
    db.add(air_filter_img)
    
    # Add system settings
    settings = [
        SystemSetting(key="store_name", value="MundoAuto", description="Nome da loja"),
        SystemSetting(key="store_email", value="info@mundoauto.com", description="Email de contacto"),
        SystemSetting(key="store_phone", value="+244 923 456 789", description="Telefone de contacto"),
        SystemSetting(key="store_address", value="Av. 21 de Janeiro, Luanda, Angola", description="Endereço físico"),
        SystemSetting(key="currency", value="AOA", description="Moeda utilizada na loja"),
        SystemSetting(key="tax_rate", value="14", description="Taxa de IVA em percentagem"),
        SystemSetting(key="shipping_fee", value="2500", description="Taxa de envio padrão em AOA"),
        SystemSetting(key="free_shipping_threshold", value="50000", description="Valor mínimo para envio gratuito")
    ]
    db.add_all(settings)
    

    # Create sample banners
    banners = [
        Banner(title="Summer Sale", image_url="/static/images/summer-sale.jpg", description="Big discounts for summer!"),
        Banner(title="Winter Deals", image_url="/static/images/winter-deals.jpg", description="Hot deals for winter!")
    ]
    db.add_all(banners)

    # Commit all changes
    db.commit()
    db.close()
    print("Database initialized successfully!")


if __name__ == "__main__":
    init_db()