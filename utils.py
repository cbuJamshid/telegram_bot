from telebot import types
from Models.main import Option
from telebot import TeleBot


# Helper function to generate inline keyboard markup
def generate_markup_languages():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton(f"O'zbek Tili", callback_data=f"uzlatin")
    btn2 = types.InlineKeyboardButton(f"Ўзбек тили", callback_data=f"uzkiril")
    btn3 = types.InlineKeyboardButton(f"Русский язык", callback_data=f"ru")
    markup.add(btn1, btn2, btn3)
    return markup


# Helper function to generate inline keyboard markup
def generate_option_markup(options: list[Option], question_number: int, question_id: int, is_single_option: bool) -> types.InlineKeyboardMarkup:
    select_symbol = "⚪️"
    if is_single_option:
        select_symbol = "◻️"

    markup = types.InlineKeyboardMarkup(row_width=2)
    for option in options:
        markup.add(types.InlineKeyboardButton(text=f"{select_symbol} {option.option_text}", callback_data=f"{question_id}_{question_number}_{option.id}_{is_single_option}_questions"))
    return markup


def generate_next_markup(lang, number):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_text = "Следующий вопрос"
    if lang == "uzlatin":
        description = "Keyingi savolga o'tish"
        btn_text = "Keyingi savol"
    elif lang == "uzkiril":
        description = "Кейинги саволга ўтиш"
        btn_text = "Кейинги савол"

    button = types.InlineKeyboardButton(text=f">> {btn_text}", callback_data=f"next_{number}")
    markup.add(button)
    return markup


def str_to_bool(text) -> bool:
    if text == "False":
        return False
    else:
        return True


def extract_values_from_callback_data(callback_data: str) -> tuple[int, int, int, bool]:
    question_id, question_number, option_id, is_single_option, _ = callback_data.split("_")
    return int(question_id), int(question_number), int(option_id), str_to_bool(is_single_option)

# finish
def send_survey_finish_message(chat_id, lang, bot: TeleBot) -> None:
    if lang == "uzkiril":
        return bot.send_message(chat_id, f"<b>Сўровномамизда иштирок этганингиз учун ташаккур! Сизнинг фикрингиз биз учун қадрлидир.</b>", parse_mode='HTML')
    elif lang == "uzlatin":
        return bot.send_message(chat_id, f"<b>So'rovnomada ishtiroq etganingiz uchun tashakkur! Sizning fikringiz biz uchun qadrlidir</b>", parse_mode='HTML')
    else:
        return bot.send_message(chat_id, f"<b>Благодарим вас за участие в нашем опросе! Ваше мнение для нас ценно. </b>", parse_mode='HTML')

def send_error_message_to_user(chat_id, bot: TeleBot):
    return bot.send_message(chat_id, f"Кутилмаган хатолик! Ботимизда сўровномани бошлаш учун /start буйруғини юборинг. \n\nНеожиданная ошибка! Отправьте команду /start чтобы начать опрос на нашем боте.")

def send_survey_already_done_message(chat_id, lang, bot: TeleBot) -> None:
    if lang == "uzkiril":
        return bot.send_message(chat_id, f"<b>Сиз сўровномамизда олдин иштирок этгансиз!</b>", parse_mode='HTML')
    elif lang == "uzlatin":
        return bot.send_message(chat_id, f"<b>Siz so'rovnomamizda oldin ishtiroq etgansiz!</b>", parse_mode='HTML')
    else:
        return bot.send_message(chat_id, f"<b>Вы уже участвовали в нашем опросе! </b>", parse_mode='HTML')
