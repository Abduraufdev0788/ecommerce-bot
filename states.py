from telegram.ext import ConversationHandler

NAME, DESCRIPTION, PRICE, QUANTITY, IMAGE = range(5)


# Checkout states
FULLNAME = 20
PHONE = 21
LOCATION = 22
CONFIRM = 23
QUANTITY_SELECT = 24
EDIT_CART_QTY = 30
