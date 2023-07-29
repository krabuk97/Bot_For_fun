import telebot
import time
import random
from bs4 import BeautifulSoup
import requests
from PIL import Image
from io import BytesIO
from background import keep_alive

bot = telebot.TeleBot('6168208647:AAHSPXVdAIF-Rgp08NZkW3eRtuSb95IlxcU')

last_mem_image_url = None

def get_random_mem_image_url():
    url = 'https://www.anekdot.ru/random/mem/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
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

@bot.message_handler(commands=['start', 'play'])
@bot.message_handler(func=lambda message: message.text == "Граємо!!!")
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

@bot.message_handler(commands=['mem'])
def send_random_mem(message):
    global last_mem_image_url
    random_mem_image_url = get_random_mem_image_url()
    if random_mem_image_url:
        # Если URL нового мема равен URL предыдущего мема, получаем новый мем
        while random_mem_image_url == last_mem_image_url:
            random_mem_image_url = get_random_mem_image_url()

        last_mem_image_url = random_mem_image_url
        try:
            # Используем Pillow для загрузки изображения
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

keep_alive()
bot.polling(non_stop=True, interval=0)
