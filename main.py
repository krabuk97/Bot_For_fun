import telebot
import time
import random
import os
import requests
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from background import keep_alive

bot = telebot.TeleBot('6168208647:AAHSPXVdAIF-Rgp08NZkW3eRtuSb95IlxcU')

# Folder z obrazkami
image_folder = './stick'  # Użyj './stick' dla względnej ścieżki w Repl.it

def get_random_image_path():
    try:
        if not os.path.exists(image_folder):
            print(f"Folder {image_folder} nie istnieje.")
            return None

        images = [os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.endswith(('png', 'jpg', 'jpeg', 'gif'))]
        if not images:
            print("Nie znaleziono obrazków w folderze.")
            return None
        return random.choice(images)
    except Exception as e:
        print(f"Błąd podczas pobierania losowego obrazka: {e}")
        return None

class MemHandler():
    @staticmethod
    def get_random_mem_image_url():
        url = 'https://www.anekdot.ru/random/mem/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            memes = soup.find_all('div', class_='topicbox')

            if memes:
                random_mem = random.choice(memes)
                img_tag = random_mem.find('img')
                if img_tag:
                    image_url = img_tag['src']
                    return image_url
                else:
                    return "Не удалось найти изображение мема."
            else:
                return "Не удалось найти мемы на странице."
        except requests.exceptions.RequestException as e:
            return f"Произошла ошибка при запросе: {e}"

    @bot.message_handler(commands=['mem'])
    def send_random_mem(message):
        random_mem_image_url = MemHandler.get_random_mem_image_url()
        if random_mem_image_url:
            try:
                response = requests.get(random_mem_image_url)
                img = Image.open(BytesIO(response.content))
                bio = BytesIO()
                img.save(bio, format='PNG')
                bio.seek(0)
                bot.send_photo(message.chat.id, bio)
            except requests.exceptions.RequestException as e:
                bot.send_message(message.chat.id, f"Ошибка при получении изображения: {e}")
        else:
            bot.send_message(message.chat.id, "Не удалось получить мем. Попробуйте позже.")

class MassageHandler():
    @bot.message_handler(commands=['start', 'play'])
    def handle_start(message):
        if message.text == "Граємо!!!":
            with open('alarm.gif', 'rb') as gif_file:
                bot.send_document(message.chat.id, gif_file)
                time.sleep(5)

    @bot.message_handler(func=lambda message: message.text == "Боже")
    def handle_bozhe(message):
        if message.text == "Боже":
            with open('jesus.gif', 'rb') as gif_file:
                bot.send_document(message.chat.id, gif_file)
                time.sleep(5)

    @bot.message_handler(func=lambda message: True)  # Odpowiada na każdą wiadomość
    def handle_all_messages(message):
        print(f"Otrzymano wiadomość: {message.text} od {message.chat.id}, typ czatu: {message.chat.type}")  # Dodaj debugowanie
        if message.chat.type in ['group', 'supergroup']:  # Sprawdzamy, czy wiadomość pochodzi z grupy
            random_image_path = get_random_image_path()
            if random_image_path:
                print(f"Wybrano obrazek: {random_image_path}")  # Dodaj debugowanie
                with open(random_image_path, 'rb') as png_file:
                    bot.send_photo(message.chat.id, png_file)
            else:
                bot.send_message(message.chat.id, "Nie udało się znaleźć obrazków w folderze.")
        else:
            print("Wiadomość nie pochodzi z grupy ani supergrupy.")

keep_alive()
print("Bot uruchomiony!")  # Informacja, że bot się uruchomił
bot.polling(non_stop=True, interval=0)
