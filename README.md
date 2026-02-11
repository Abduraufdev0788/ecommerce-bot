#ecommerce_bot/
#├── app/
#│   ├── __init__.py
#│   │
#│   ├── core/
#│   │   ├── config.py          # ENV, settings
#│   │   └── database.py        # SQLAlchemy engine, Session
#│   │
#│   ├── models/
#│   │   ├── __init__.py
#│   │   ├── base.py            # Declarative Base
#│   │   ├── user.py            # User modeli
#│   │   ├── product.py         # Product modeli
#│   │   └── order.py           # Order + OrderItem
#│   │
#│   ├── repositories/
#│   │   ├── user_repo.py       # DB CRUD logic
#│   │   ├── product_repo.py
#│   │   └── order_repo.py
#│   │
#│   ├── services/
#│   │   ├── user_service.py    # Business logic
#│   │   ├── product_service.py
#│   │   └── order_service.py
#│   │
#│   ├── bot/
#│   │   ├── handlers/
#│   │   │   ├── start.py
#│   │   │   ├── catalog.py
#│   │   │   └── order.py
#│   │   └── keyboards/
#│   │       └── inline.py
#│   │
#│   └── main.py                # Bot entry point
#│
#├── alembic/                   # Migratsiya (keyin qo‘shiladi)
#├── .env
#├── requirements.txt
#└── README.md
