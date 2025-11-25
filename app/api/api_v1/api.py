from fastapi import APIRouter

from app.api.endpoints import users, auth, products, cart, orders, admin, activity_logs, shops, shop_products, shop_orders, banners, analytics

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(shops.router, prefix="/shops", tags=["shops"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(shop_products.router, prefix="/shop-products", tags=["shop_products"])
api_router.include_router(cart.router, prefix="/cart", tags=["cart"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(shop_orders.router, prefix="/shops", tags=["shop_orders"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(activity_logs.router, prefix="/logs", tags=["activity_logs"])
api_router.include_router(banners.router, prefix="/banners", tags=["banners"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])