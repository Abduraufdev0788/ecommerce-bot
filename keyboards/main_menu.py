from telegram import ReplyKeyboardMarkup

def main_menu():
    keyboard = [
        ["📦 Mahsulotlar", "🛒 Savatcham"],
        ["📦 Buyurtmalarim", "ℹ️ Yordam"]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        selective=True
    )
