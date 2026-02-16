from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from config import BOT_TOKEN
from database import db

# Handlers
from handlers.start import start
from handlers.admin import (
    add_product_start,
    get_name,
    get_description,
    get_price,
    get_quantity,
    get_image,
    cancel
)
from handlers.products import show_products, add_to_cart
from handlers.cart import show_cart, edit_cart_quantity_start, update_cart_quantity
from handlers.payments import receive_payment
from handlers.checkout import (
    start_checkout_cart,
    start_checkout_single,
    get_fullname,
    get_phone,
    get_location,
    confirm_order,
    edit_fullname,
    edit_phone,
    edit_location,
    cancel_order,
    get_single_quantity
)
from handlers.admin_payment import admin_confirm, admin_cancel
from handlers.orders import show_orders, order_detail

# States
from states import (
    NAME, DESCRIPTION, PRICE, QUANTITY, IMAGE,
    FULLNAME, PHONE, LOCATION, CONFIRM, QUANTITY_SELECT, EDIT_CART_QTY
)
from handlers.help import show_help

from handlers.admin_panel import (
    admin_panel,
    admin_stats,
    admin_orders,
    admin_products
)
from handlers.payment_timeout import payment_timeout_checker

from handlers.admin_orders import (
    admin_orders_menu,
    admin_orders_list,
    admin_order_detail
)
from handlers.ads import send_random_ad






# =========================
# STARTUP
# =========================

async def on_startup(app):
    await db.connect()
    await db.create_tables()
    print("Database connected ✅")

    # 🔥 Background timeout task
    app.create_task(payment_timeout_checker(app))



# =========================
# MAIN
# =========================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.post_init = on_startup

    # =========================
    # START
    # =========================
    app.add_handler(CommandHandler("start", start))

    # =========================
    # ADMIN PRODUCT ADD
    # =========================
    admin_conv = ConversationHandler(
        entry_points=[CommandHandler("add_product", add_product_start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_price)],
            QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_quantity)],
            IMAGE: [MessageHandler(filters.PHOTO, get_image)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(admin_conv)

    # =========================
    # MENU BUTTONS
    # =========================

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📦 Mahsulotlar$"), show_products))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^🛒 Savatcham$"),show_cart))


    # =========================
    # CART ADD
    # =========================
    app.add_handler(
        CallbackQueryHandler(add_to_cart, pattern="^add:")
    )

    # =========================
    # CHECKOUT CONVERSATION
    # =========================
    checkout_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_checkout_cart, pattern="^checkout$"),
            CallbackQueryHandler(start_checkout_single, pattern="^buy:")
        ],
        states={
            QUANTITY_SELECT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_single_quantity)
            ],


            FULLNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_fullname)
            ],
            PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)
            ],
            LOCATION: [
                MessageHandler(filters.LOCATION, get_location)
            ],
            CONFIRM: [
                CallbackQueryHandler(confirm_order, pattern="^confirm_order$"),
                CallbackQueryHandler(edit_fullname, pattern="^edit_fullname$"),
                CallbackQueryHandler(edit_phone, pattern="^edit_phone$"),
                CallbackQueryHandler(edit_location, pattern="^edit_location$"),
                CallbackQueryHandler(cancel_order, pattern="^cancel_order$")
            ],
        },
        fallbacks=[]
    )

    app.add_handler(checkout_conv)

    # =========================
    # PAYMENT SCREENSHOT
    # =========================
    app.add_handler(
        MessageHandler(filters.PHOTO, receive_payment)
    )

    # =========================
    # ADMIN CONFIRM PAYMENT
    # =========================
    app.add_handler(CallbackQueryHandler(admin_confirm, pattern="^admin_confirm:"))
    app.add_handler(CallbackQueryHandler(admin_cancel, pattern="^admin_cancel:"))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📦 Buyurtmalarim$"), show_orders))
    app.add_handler(CallbackQueryHandler(order_detail, pattern="^order_detail:"))

    cart_edit_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(edit_cart_quantity_start, pattern="^edit_cart:")
    ],
    states={
        EDIT_CART_QTY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, update_cart_quantity)
        ]
    },
    fallbacks=[]
)

    app.add_handler(cart_edit_conv)

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^ℹ️ Yordam$"), show_help))

    app.add_handler(CommandHandler("admin", admin_panel))

    app.add_handler(CallbackQueryHandler(admin_stats, pattern="^admin_stats$"))
    app.add_handler(CallbackQueryHandler(admin_orders, pattern="^admin_orders$"))
    app.add_handler(CallbackQueryHandler(admin_products, pattern="^admin_products$"))

    app.add_handler(CallbackQueryHandler(admin_orders_menu, pattern="^admin_orders$"))
    app.add_handler(CallbackQueryHandler(admin_orders_list, pattern="^orders_"))
    app.add_handler(CallbackQueryHandler(admin_order_detail, pattern="^order_detail_admin:"))





    print("Bot ishga tushdi 🚀")
    app.run_polling()


if __name__ == "__main__":
    main()
