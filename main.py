import telebot
from config import BOT_TOKEN
from telebot.types import Message, CallbackQuery
from utils import generate_markup_languages, extract_values_from_callback_data, generate_option_markup, send_error_message_to_user, send_survey_already_done_message
from DAL.Repository.UserRepository import UserRepository
from DAL.Repository.OptionRepository import OptionRepository
from DAL.Repository.ResponseRepository import ResponseRepository
from DAL.Repository.QuestionRepository import QuestionRepository
from DAL.Handlers.question import QuestionHandler
from Models.main import *
from datetime import datetime
from constants import (
    SINGLE_OPTION_SELECTED_SYMBOL,
    MULTIPLE_OPTION_SELECTED_SYMBOL,
)
from data.options import jump_options_question4, jump_options_question9

bot = telebot.TeleBot(BOT_TOKEN)


# Message handlers
@bot.message_handler(commands=["start"])
def handle_start_command(message: Message):
    user_id = message.chat.id
    try:
        user = UserRepository.get(user_id)
        if not user:
            user_data = User(
                id=user_id,
                language="ru",
                join_date=datetime.fromtimestamp(message.date),
                current_question_number=1,
                is_survey_finished=False
            )
            UserRepository.create(user_data)
        bot.send_message(
            message.chat.id,
            f"<b>{message.from_user.first_name},</b> Аҳоли қарз юкини аниқлаш бўйича сўровномага хуш келибсиз!\nИлтимос, тилни танланг<b>\n\n{message.from_user.first_name},</b> Добро пожаловать в опросник по определению долговой нагрузки населения!\nПожалуйста, выберите язык",
            parse_mode='HTML',
            reply_markup=generate_markup_languages()
        )
    except Exception as _ex:
        print(f"Unhandled Error occured in start command {_ex}")
        return send_error_message_to_user(user_id, bot)
# Callback handlers
@bot.callback_query_handler(func=lambda call: call.data in ["ru", "uzlatin", "uzkiril"])
def handle_language_change_callback(call: CallbackQuery):
    user_id = call.message.chat.id
    try:
        user = UserRepository.get(user_id)
        if user.is_survey_finished:
            return send_survey_already_done_message(user_id, user.language, bot)
        UserRepository.set_language(user_id, call.data)
        UserRepository.set_question_number(user_id, 1)
        QuestionHandler.get_instance().send_question(bot, user_id)
    except Exception as _ex:
        print(f"Unhandled Error occured while clicking language callback {_ex}")
        return send_error_message_to_user(user_id, bot)


@bot.callback_query_handler(func=lambda call: "questions" in call.data)
def handle_response_callback(call: CallbackQuery):
    user_id = call.message.chat.id
    try:
        user = UserRepository.get(user_id)
        if user.is_survey_finished:
            return send_survey_already_done_message(user_id, user.language, bot)

        question_id, question_number, option_id, is_multiple_option = extract_values_from_callback_data(
            call.data
        )
        options = OptionRepository.getByQuestionId(question_id)
        markup = generate_option_markup(options, question_number, question_id, is_multiple_option)

        if is_multiple_option:
            ResponseRepository.delete_or_create(user_id, question_id, option_id)
            users_responses = ResponseRepository.get_by_question_and_user_id(user_id, question_id)
            selected_option_ids = [response.option_id for response in users_responses]
            # Showing selected options with 'selected_symbol'
            for row in markup.keyboard:
                for button in row:
                    _, _, response_option_id, _, _ = button.callback_data.split("_")
                    if int(response_option_id) in selected_option_ids:
                        button.text = MULTIPLE_OPTION_SELECTED_SYMBOL + button.text[1:]
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        else:
            ResponseRepository.update_or_create(user_id, question_id, option_id)
            # Showing selected options with 'selected_symbol'
            for row in markup.keyboard:
                for button in row:
                    _, _, response_option_id, _, _ = button.callback_data.split("_")
                    if int(response_option_id) == option_id:
                        button.text = SINGLE_OPTION_SELECTED_SYMBOL + button.text[1:]
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)


            # bot.send_message(user_id, f"Q_NUMBER: {user.current_question_number}")
            # check if last question in users options
            if question_number in range(5, 17):
                third_question_id = QuestionRepository.getByLanguageNumber(user.language, 3).id
                responses_asc_order = ResponseRepository.get_by_question_and_user_id(user.id, third_question_id)
                last_reponse_option = OptionRepository.getById(responses_asc_order[-1].option_id)
                last_reponse_question_number = jump_options_question4[user.language][last_reponse_option.option_text]
                if question_number == last_reponse_question_number:
                    QuestionHandler.get_instance().send_question(bot, user.id)
            elif question_number in range(25, 35):
                ninth_question_id = QuestionRepository.getByLanguageNumber(user.language, 22).id
                responses_asc_order_9 = ResponseRepository.get_by_question_and_user_id(user.id, ninth_question_id)
                last_reponse_option_9 = OptionRepository.getById(responses_asc_order_9[-1].option_id)
                last_reponse_question_number_9 = jump_options_question9[user.language][last_reponse_option_9.option_text] + 1
                # bot.send_message(user_id, f"{question_number}, last: {last_reponse_question_number_9}")
                if question_number == last_reponse_question_number_9:
                    QuestionHandler.get_instance().send_question(bot, user.id)
            elif user.current_question_number - 1 == question_number:
                QuestionHandler.get_instance().send_question(bot, user.id)
    except Exception as _ex:
        print(f"Unhandled Error occured while clicking questions (options) callback {_ex}")
        return send_error_message_to_user(user_id, bot)

@bot.callback_query_handler(func=lambda call: "next" in call.data)
def handle_next_question_callback(call: CallbackQuery):
    user_id = call.message.chat.id
    try:
        user = UserRepository.get(user_id)
        _, question_number = call.data.split("_")
        question_number = int(question_number)
        if user.current_question_number - 1 == question_number:
            QuestionHandler.get_instance().send_question(bot, user.id)
        return
    except Exception as _ex:
        print(f"Unhandled Error occured while clicking next callback {_ex}")
        return send_error_message_to_user(user_id, bot)


bot.infinity_polling()
