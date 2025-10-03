import telebot
from telebot import types

TOKEN = '8478425052:AAEWtD19dGdCsGMnV2M9TJzzlAX_gl2txBs'
bot = telebot.TeleBot(TOKEN)

# ID менеджеров для уведомлений (замени на реальные ID)
MANAGER_IDS = [500016247, 832104985]  # Узнай ID через @userinfobot

# Функция отправки заказа всем менеджерам
def send_order_to_managers(order_data):
    order_text = (
        f"🆕 **НОВЫЙ ЗАКАЗ!**\n\n"
        f"🧵 **Тип ткани:** {order_data['fabric_name']}\n"
        f"🎨 **Цвет:** {order_data['color']}\n"
        f"📏 **Метраж:** {order_data['quantity']} м\n"
        f"💰 **Стоимость:** {order_data.get('total_price', 0)} руб\n"
        f"👤 **ФИО:** {order_data['fio']}\n"
        f"📱 **Телефон:** {order_data['phone']}\n"
        f"📍 **ПВЗ СДЭК:** {order_data['address']}\n"
        f"👤 **ID клиента:** {order_data.get('user_id', 'Неизвестно')}"
    )

    # Простая кнопка для связи с клиентом
    markup = types.InlineKeyboardMarkup()
    btn_contact = types.InlineKeyboardButton(
        '📞 Написать клиенту',
        url=f"tg://user?id={order_data.get('user_id')}"
    )
    markup.add(btn_contact)

    success_count = 0
    for manager_id in MANAGER_IDS:
        try:
            bot.send_message(
                manager_id,
                order_text,
                reply_markup=markup,
                parse_mode='Markdown'
            )
            success_count += 1
            print(f"✅ Заказ отправлен менеджеру {manager_id}")
        except Exception as e:
            print(f"❌ Ошибка отправки менеджеру {manager_id}: {e}")

    return success_count > 0  # True если хотя бы одному отправилось

# Ссылки на посты в вашем канале (ЗАМЕНИТЕ на реальные)
POST_LINKS = {
    'california_viscose': 'https://t.me/ya_shveyaa/566',
    'len_crash': 'https://t.me/ya_shveyaa/771',
    'jersey': 'https://t.me/ya_shveyaa/572',
    'euro_angora': 'https://t.me/ya_shveyaa/946',
    'lapsha': 'https://t.me/ya_shveyaa/575'
}

@bot.message_handler(commands=['start'])
def start_command(message):
    # Главное меню с одной кнопкой
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(
        text='🎯 Отрезы тканей',
        callback_data='show_fabric_types'
    )
    markup.add(btn)

    bot.send_message(
        message.chat.id,
        "Добро пожаловать в мир качественных тканей! 🧵\n\nВыберите действие:",
        reply_markup=markup
    )

# Обработчик кнопки "Отрезы тканей"
@bot.callback_query_handler(func=lambda call: call.data == 'show_fabric_types')
def show_fabric_types(call):
    # Меню с типами тканей
    markup = types.InlineKeyboardMarkup(row_width=1)

    btn1 = types.InlineKeyboardButton('🧵 Калифорнийская вискоза', callback_data='fabric_california_viscose')
    btn2 = types.InlineKeyboardButton('🌿 Лен-крэш', callback_data='fabric_len_crash')
    btn3 = types.InlineKeyboardButton('👕 Джерси', callback_data='fabric_jersey')
    btn4 = types.InlineKeyboardButton('🐰 Евроангора', callback_data='fabric_euro_angora')
    btn5 = types.InlineKeyboardButton('🍜 Лапша', callback_data='fabric_lapsha')
    btn_back = types.InlineKeyboardButton('◀️ Назад', callback_data='back_to_main')

    markup.add(btn1, btn2, btn3, btn4, btn5, btn_back)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Выберите тип ткани:",
        reply_markup=markup
    )

# ОБНОВЛЕННЫЙ обработчик для каждой ткани - с кнопкой ЗАКАЗАТЬ
@bot.callback_query_handler(func=lambda call: call.data.startswith('fabric_'))
def send_fabric_post(call):
    fabric_type = call.data.replace('fabric_', '')

    # Получаем ссылку на пост
    post_link = POST_LINKS.get(fabric_type, 'https://t.me/ваш_канал')

    # Тексты для каждой ткани
    fabric_names = {
        'california_viscose': 'Калифорнийская вискоза',
        'len_crash': 'Лен-крэш',
        'jersey': 'Джерси',
        'euro_angora': 'Евроангора',
        'lapsha': 'Лапша'
    }

    fabric_name = fabric_names.get(fabric_type, 'ткани')

    # СОЗДАЕМ КНОПКУ "ЗАКАЗАТЬ"
    markup = types.InlineKeyboardMarkup()
    btn_post = types.InlineKeyboardButton('📖 Перейти к посту', url=post_link)
    btn_order = types.InlineKeyboardButton('🛒 Заказать', callback_data=f'order_{fabric_type}')  # НОВАЯ КНОПКА
    btn_back = types.InlineKeyboardButton('◀️ К выбору тканей', callback_data='show_fabric_types')

    markup.add(btn_post, btn_order)  # Две кнопки в одном ряду
    markup.add(btn_back)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"🎊 {fabric_name.upper()} 🎊\n\n✨ Отрезы готовы к просмотру!\n\nВы можете посмотреть отрезы в канале или сразу оформить заказ:",
        reply_markup=markup
    )

   # Хранилище для данных заказа
user_orders = {}

# НОВЫЙ умный обработчик для кнопки "Заказать"
@bot.callback_query_handler(func=lambda call: call.data.startswith('order_'))
def handle_order(call):
    fabric_type = call.data.replace('order_', '')

    # Тексты для каждой ткани
    fabric_names = {
        'california_viscose': 'Калифорнийская вискоза',
        'len_crash': 'Лен-крэш',
        'jersey': 'Джерси',
        'euro_angora': 'Евроангора',
        'lapsha': 'Лапша'
    }

    fabric_name = fabric_names.get(fabric_type, 'ткани')

    # Сохраняем начало заказа
    user_id = call.from_user.id
    user_orders[user_id] = {
        'fabric_type': fabric_type,
        'fabric_name': fabric_name,
        'step': 'fabric_type_confirm'  # Первый шаг - подтверждение типа ткани
    }

    # Задаем первый вопрос - подтверждение типа ткани
    markup = types.InlineKeyboardMarkup()
    btn_confirm = types.InlineKeyboardButton('✅ Да, верно', callback_data='confirm_fabric')
    btn_change = types.InlineKeyboardButton('🔄 Выбрать другую', callback_data='show_fabric_types')
    markup.add(btn_confirm, btn_change)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"🛒 **ОФОРМЛЕНИЕ ЗАКАЗА**\n\n"
             f"🧵 **Шаг 1 из 6:** Выбранная ткань: **{fabric_name.upper()}**\n\n"
             f"Подтвердите выбор ткани или выберите другую:",
        reply_markup=markup,
        parse_mode='Markdown'
    )

# Обработчик подтверждения ткани
@bot.callback_query_handler(func=lambda call: call.data == 'confirm_fabric')
def confirm_fabric(call):
    user_id = call.from_user.id
    order_data = user_orders.get(user_id)

    if not order_data:
        return

    # Переходим к вопросу о цвете
    order_data['step'] = 'color'

    markup = types.InlineKeyboardMarkup()
    btn_cancel = types.InlineKeyboardButton('❌ Отменить заказ', callback_data='cancel_order')
    markup.add(btn_cancel)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"🛒 **ОФОРМЛЕНИЕ ЗАКАЗА: {order_data['fabric_name'].upper()}**\n\n"
             f"🎨 **Шаг 2 из 6:** Какой цвет ткани вас интересует?\n"
             f"(опишите желаемый цвет)",
        reply_markup=markup,
        parse_mode='Markdown'
    )

# НОВЫЙ обработчик для ниточек
@bot.callback_query_handler(func=lambda call: call.data.startswith('threads_'))
def handle_threads_selection(call):
    user_id = call.from_user.id
    order_data = user_orders.get(user_id)

    if not order_data:
        return

    if call.data == 'threads_yes':
        order_data['threads'] = 'Да'
        order_data['threads_price'] = 50
        response_text = "✅ Ниточки добавлены к заказу (+50 руб)"
    else:
        order_data['threads'] = 'Нет' 
        order_data['threads_price'] = 0
        response_text = "❌ Ниточки не выбраны"

    order_data['step'] = 'fio'

    markup = types.InlineKeyboardMarkup()
    btn_cancel = types.InlineKeyboardButton('❌ Отменить заказ', callback_data='cancel_order')
    markup.add(btn_cancel)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"{response_text}\n\n"
             f"👤 **Шаг 5 из 7:** Ваше ФИО (полностью):",
        reply_markup=markup,
        parse_mode='Markdown'
    )

# Обработчик ответов пользователя
@bot.message_handler(func=lambda message: message.from_user.id in user_orders)
def handle_order_responses(message):
    user_id = message.from_user.id
    order_data = user_orders.get(user_id)

    if not order_data:
        return

    current_step = order_data['step']
    fabric_name = order_data['fabric_name']

    markup = types.InlineKeyboardMarkup()
    btn_cancel = types.InlineKeyboardButton('❌ Отменить заказ', callback_data='cancel_order')
    markup.add(btn_cancel)

    if current_step == 'color':
        order_data['color'] = message.text
        order_data['step'] = 'quantity'

        bot.send_message(
            user_id,
            f"📏 **Шаг 3 из 6:** Укажите желаемый метраж:\n"
            f"(например: 2.5 или 3)",
            reply_markup=markup,
            parse_mode='Markdown'
        )

    elif current_step == 'quantity':
        # Проверяем, что ввели число
        try:
            quantity = float(message.text.replace(',', '.'))
            if quantity <= 0:
                raise ValueError

            order_data['quantity'] = quantity
            order_data['step'] = 'threads'  # ← НОВЫЙ ШАГ: ниточки

            # Создаем кнопки для ниточек
            markup_threads = types.InlineKeyboardMarkup()
            btn_yes = types.InlineKeyboardButton('✅ Да, подобрать ниточки', callback_data='threads_yes')
            btn_no = types.InlineKeyboardButton('❌ Нет, спасибо', callback_data='threads_no')
            btn_cancel = types.InlineKeyboardButton('❌ Отменить заказ', callback_data='cancel_order')
            markup_threads.add(btn_yes, btn_no)
            markup_threads.add(btn_cancel)

            bot.send_message(
                user_id,
                f"🪡 **Шаг 4 из 7:** Хотите подобрать ниточки в тон?\n"
                f"💰 Стоимость: 50 руб/катушка",
                reply_markup=markup_threads,
                parse_mode='Markdown'
            )

        except ValueError:
            bot.send_message(
                user_id,
                "❌ Пожалуйста, введите корректное число (например: 2.5 или 3):",
                reply_markup=markup
            )
    elif current_step == 'fio':
        order_data['fio'] = message.text
        order_data['step'] = 'phone'

        bot.send_message(
            user_id,
            f"📱 **Шаг 5 из 6:** Ваш контактный телефон:",
            reply_markup=markup,
            parse_mode='Markdown'
        )

    elif current_step == 'phone':
        # Проверяем, что в телефоне есть цифры
        phone_digits = ''.join(filter(str.isdigit, message.text))
        if len(phone_digits) < 10:
            bot.send_message(
                user_id,
                "❌ Пожалуйста, введите корректный номер телефона (минимум 10 цифр):",
                reply_markup=markup
            )
            return

        order_data['phone'] = message.text
        order_data['step'] = 'address'

        bot.send_message(
            user_id,
            f"📍 **Шаг 6 из 6:** Адрес удобного пункта выдачи СДЭК:\n"
            f"(город, улица, номер пункта)",
            reply_markup=markup,
            parse_mode='Markdown'
        )

    elif current_step == 'address':
        order_data['address'] = message.text
        order_data['step'] = 'complete'

        # Заказ завершен - показываем итог
        show_order_summary(user_id, order_data)

# Функция показа итогов заказа
def show_order_summary(user_id, order_data):
    # Расчет стоимости
    prices = {
        'california_viscose': 616,
        'len_crash': 604,
        'jersey': 978,
        'euro_angora': 765,
        'lapsha': 632
    }

    price_per_meter = prices.get(order_data['fabric_type'], 800)
    total_price = price_per_meter * order_data['quantity']
    # ДОБАВЛЯЕМ СТОИМОСТЬ НИТОЧЕК
    total_price += order_data.get('threads_price', 0)
    order_data['total_price'] = total_price
    order_data['user_id'] = user_id

    # Отправляем заказ всем менеджерам
    send_success = send_order_to_managers(order_data)

    # Убираем Markdown разметку для клиента
    summary_text = (
        f"✅ ЗАКАЗ ОФОРМЛЕН!\n\n"
        f"🧵 Тип ткани: {order_data['fabric_name']}\n"
        f"🎨 Цвет: {order_data['color']}\n"
        f"📏 Метраж: {order_data['quantity']} м\n"
        f"🪡 Ниточки: {order_data.get('threads', 'Нет')}\n"
        f"💰 Стоимость: {total_price} руб\n"
        f"👤 ФИО: {order_data['fio']}\n"
        f"📱 Телефон: {order_data['phone']}\n"
        f"📍 ПВЗ СДЭК: {order_data['address']}\n\n"
    )

    if send_success:
        summary_text += "📞 Менеджер свяжется с вами для подтверждения заказа!"
    else:
        summary_text += "⚠️ Для подтверждения заказа напишите @Mafia_Dubna"

    markup = types.InlineKeyboardMarkup()
    btn_manager = types.InlineKeyboardButton(
        '📞 Написать менеджеру',
        url='https://t.me/YaShveyaRU'
    )
    btn_new_order = types.InlineKeyboardButton('🛍 Новый заказ', callback_data='show_fabric_types')
    markup.add(btn_manager)
    markup.add(btn_new_order)

    bot.send_message(
        user_id,
        summary_text,
        reply_markup=markup
        # Убираем parse_mode='Markdown'
    )

    # Очищаем данные заказа
    if user_id in user_orders:
        del user_orders[user_id]

# Обработчик отмены заказа
@bot.callback_query_handler(func=lambda call: call.data == 'cancel_order')
def cancel_order(call):
    user_id = call.from_user.id
    if user_id in user_orders:
        del user_orders[user_id]

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="❌ Заказ отменен",
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton('🛍 Новый заказ', callback_data='show_fabric_types')
        )
    )

# Обработчик кнопки "Назад"
@bot.callback_query_handler(func=lambda call: call.data == 'back_to_main')
def back_to_main(call):
    start_command(call)

print("🪡 Бот для тканей запущен! Работает меню с 5 типами тканей")

import os

if __name__ == '__main__':
    print("🚀 Запуск бота...")
    
    try:
        # Просто запускаем бота
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
