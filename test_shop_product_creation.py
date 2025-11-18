from app.db.session import SessionLocal
from app.crud.shop_product import create_shop_product
from app.schemas.shop_product import ShopProductCreate
import uuid

def test_shop_product_creation():
    db = SessionLocal()
    try:
        # Test data
        test_shop_id = "1b02f554-f093-4182-9dca-27289c53a9fd"  # From the error message
        
        shop_product_data = ShopProductCreate(
            shop_id=uuid.UUID(test_shop_id),
            name="Test Product",
            description="Test product description",
            technical_details="Test technical details",
            price=100.0,
            sale_price=80.0,
            sku="TEST-001",
            oe_number="TEST123",
            brand="Test Brand",
            manufacturer="Test Manufacturer",
            model="Test Model",
            manufacturer_year=2023,
            compatible_vehicles=["Test Vehicle"],
            weight=1.5,
            dimensions="10x5x3",
            image="test_image_data",
            is_featured=False,
            is_on_sale=True,
            stock_quantity=10
        )
        
        print("Creating test shop product...")
        created_product = create_shop_product(db, shop_product_data)
        
        print(f"✅ Success! Created shop product with ID: {created_product.id}")
        print(f"   Name: {created_product.name}")
        print(f"   Shop ID: {created_product.shop_id}")
        print(f"   Price: {created_product.price}")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating shop product: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_shop_product_creation()