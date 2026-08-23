import random
from decimal import Decimal
from faker import Faker
from sqlalchemy import text

from app.database import SessionLocal, engine
from app.models import Base, Product, SexEnum, Color, Store, StoreInventory

fake = Faker('en_US')
db = SessionLocal()

def seed_database(limit: int = 50):
    # 1. ЖЕСТКАЯ ОЧИСТКА: Удаляем все таблицы, чтобы схема обновилась
    print("Удаление старых таблиц со старой схемой...")
    Base.metadata.drop_all(bind=engine)

    # 2. СОЗДАЕМ ТАБЛИЦЫ ЗАНОВО (теперь они точно будут иметь sub_category)
    print("Создание таблиц с актуальной структурой...")
    Base.metadata.create_all(bind=engine)

    # Блок TRUNCATE можно оставить для совместимости, хотя сейчас таблицы уже пустые
    try:
        db.execute(text("TRUNCATE TABLE products, stores, colors, users CASCADE"))
        db.commit()
    except Exception as e:
        db.rollback()
        print("TRUNCATE пропущен (таблицы только что созданы).")

    try:
        # 1. СОЗДАЕМ РЕАЛИСТИЧНЫЕ МАГАЗИНЫ В СЛОВАКИИ
        stores_data = [
            {"name": "X-PRESS Eurovea Bratislava", "city": "Bratislava", "address": "Pribinova 8",
             "postal_code": "811 09", "lat": 48.140649, "lng": 17.120043},
            {"name": "X-PRESS Aupark Bratislava", "city": "Bratislava", "address": "Einsteinova 18",
             "postal_code": "851 01", "lat": 48.132801, "lng": 17.107609},
            {"name": "X-PRESS Aupark Košice", "city": "Košice", "address": "Námestie osloboditeľov 1",
             "postal_code": "040 01", "lat": 48.717746, "lng": 21.263212},
            {"name": "X-PRESS Optima Košice", "city": "Košice", "address": "Moldavská cesta 32",
             "postal_code": "040 11", "lat": 48.694736, "lng": 21.238448},
            {"name": "X-PRESS Aupark Žilina", "city": "Žilina", "address": "Veľká Okružná 59A",
             "postal_code": "010 01", "lat": 49.221474, "lng": 18.740054},
        ]

        db_stores = []
        for s_info in stores_data:
            store = Store(
                name=s_info["name"],
                city=s_info["city"],
                address=s_info["address"],
                postal_code=s_info["postal_code"],
                latitude=s_info["lat"],
                longitude=s_info["lng"]
            )
            db.add(store)
            db_stores.append(store)

        db.commit()
        print("Магазины в Словакии успешно созданы.")

        # 2. ПУЛЫ ДЛЯ ГЕНЕРАЦИИ
        materials_pool = [
            "100% Cotton", "95% Cotton, 5% Elastane", "100% Polyester",
            "Genuine Leather", "Denim", "Wool Blend", "Recycled Nylon", "Linen"
        ]

        COLORS_POOL = {
            "Black": "#1C1C1C", "White": "#F8F8F8", "Navy": "#1B263B",
            "Olive": "#4A5D23", "Beige": "#D5C8A0", "Burgundy": "#670A0A",
            "Grey": "#7D7D7D", "Mustard": "#E1AD01", "Khaki": "#867E36", "Light Blue": "#A4B8C4"
        }
        color_names = list(COLORS_POOL.keys())

        clothes_sizes = ["XS", "S", "M", "L", "XL", "XXL"]
        shoes_sizes = ["36", "37", "38", "39", "40", "41", "42", "43", "44", "45"]
        one_size = ["One Size"]

        catalog_logic = {
            "HATS": {"types": ["Cap", "Beanie", "Hat", "Bucket Hat"],
                     "sexes": [SexEnum.men, SexEnum.women, SexEnum.unisex], "sizes": one_size},
            "JACKETS": {"types": ["Jacket", "Windbreaker", "Bomber"],
                        "sexes": [SexEnum.men, SexEnum.women, SexEnum.unisex], "sizes": clothes_sizes},
            "HOODIES": {"types": ["Hoodie", "Zip-up Hoodie"], "sexes": [SexEnum.men, SexEnum.women, SexEnum.unisex],
                        "sizes": clothes_sizes},
            "SHIRTS": {"types": ["Shirt", "Flannel Shirt", "Oxford Shirt"], "sexes": [SexEnum.men, SexEnum.women],
                       "sizes": clothes_sizes},
            "JEANS": {"types": ["Jeans", "Denim Pants", "Slim Fit Jeans"], "sexes": [SexEnum.men, SexEnum.women],
                      "sizes": clothes_sizes},
            "TROUSERS": {"types": ["Chinos", "Trousers", "Cargo Pants"], "sexes": [SexEnum.men, SexEnum.women],
                         "sizes": clothes_sizes},
            "SHORTS": {"types": ["Shorts", "Boardshorts", "Sweatshorts"], "sexes": [SexEnum.men, SexEnum.women],
                       "sizes": clothes_sizes},
            "UNDERWEAR": {"types": ["Briefs", "Boxers", "Trunks"], "sexes": [SexEnum.men], "sizes": clothes_sizes},
            "DRESSES": {"types": ["Dress", "Sundress", "Evening Gown"], "sexes": [SexEnum.women],
                        "sizes": clothes_sizes},
            "SKIRTS": {"types": ["Skirt", "Mini Skirt", "Maxi Skirt"], "sexes": [SexEnum.women],
                       "sizes": clothes_sizes},
            "BLOUSES & SHIRTS": {"types": ["Blouse", "Silk Blouse"], "sexes": [SexEnum.women], "sizes": clothes_sizes},
            "LINGERIE": {"types": ["Bra", "Panties", "Lingerie Set"], "sexes": [SexEnum.women], "sizes": clothes_sizes},
            "SHOES": {"types": ["Sneakers", "Boots", "Sandals", "Loafers"],
                      "sexes": [SexEnum.men, SexEnum.women, SexEnum.unisex], "sizes": shoes_sizes},
            "BAGS": {"types": ["Backpack", "Tote Bag", "Messenger Bag"],
                     "sexes": [SexEnum.men, SexEnum.women, SexEnum.unisex], "sizes": one_size},
            "ACCESSORIES": {"types": ["Belt", "Wallet", "Sunglasses"],
                            "sexes": [SexEnum.men, SexEnum.women, SexEnum.unisex], "sizes": one_size},
        }

        # 3. СОЗДАЕМ ЦВЕТА
        db_colors = []
        for name, hex_code in COLORS_POOL.items():
            new_color = Color(name=name, hex_code=hex_code)
            db.add(new_color)
            db_colors.append(new_color)
        db.commit()

        # 4. ГЕНЕРИРУЕМ ТОВАРЫ И РАСПРЕДЕЛЯЕМ ПО МАГАЗИНАМ
        products_to_insert = []
        for _ in range(limit):
            category_name = random.choice(list(catalog_logic.keys()))
            logic = catalog_logic[category_name]

            sex = random.choice(logic["sexes"])
            item_type = random.choice(logic["types"])
            sizes_pool = logic["sizes"]

            primary_color_obj = random.choice(db_colors)
            title = f"{primary_color_obj.name} {item_type}"

            selected_color_objects = [primary_color_obj]
            extra_colors = random.sample(db_colors, k=random.randint(0, 2))
            for c_obj in extra_colors:
                if c_obj not in selected_color_objects:
                    selected_color_objects.append(c_obj)

            selected_sizes = one_size if sizes_pool == one_size else random.sample(sizes_pool, k=random.randint(2,
                                                                                                                min(5,
                                                                                                                    len(sizes_pool))))

            product = Product(
                title=title[:255],
                description=fake.catch_phrase(),
                price=Decimal(random.uniform(15.0, 300.0)).quantize(Decimal("0.00")),
                sex=sex,
                category=category_name,

                sub_category=item_type.upper(),
                sizes=selected_sizes,
                colors=selected_color_objects,
                brand=fake.company(),
                material=random.choice(materials_pool),
                country_of_origin=fake.country(),
                image_url=fake.image_url(width=800, height=1000),
                is_active=fake.boolean(chance_of_getting_true=95)
            )

            db.add(product)
            db.flush()

            # Для каждого товара прописываем остатки в случайных магазинах
            for store in db_stores:
                # Пусть в каких-то магазинах товар будет в наличии, а где-то 0 (или не продается)
                has_stock = random.choice([True, True, False])
                qty = random.randint(1, 35) if has_stock else 0

                inventory_item = StoreInventory(
                    product_id=product.id,
                    store_id=store.id,
                    quantity=qty
                )
                db.add(inventory_item)

        db.commit()
        print(f"Успех! База данных заполнена: {limit} товаров распределены по магазинам Словакии.")

    except Exception as e:
        db.rollback()
        print(f"Ошибка при сидировании: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database(limit=50)