import requests
import time


API_URL: str = 'https://api.telegram.org/bot'
BOT_TOKEN: str = '5852909746:AAHIR3dTplmcrTwkVaCVgfJ7J23fTyImWQU'
TEXT: str = 'Ура! Классный апдейт!'
MAX_COUNTER: int = 100
GET_UPDATE_FROM_API: str = "https://api.telegram.org/bot5852909746:AAHIR3dTplmcrTwkVaCVgfJ7J23fTyImWQU/getUpdates"
offset: int = -2
counter: int = 0
chat_id: int
#https://api.telegram.org/bot5424991242:AAGwomxQz1p46bRi_2m3V7kvJlt5RjK9xr0/getMe
#https://api.telegram.org/bot5852909746:AAHIR3dTplmcrTwkVaCVgfJ7J23fTyImWQU/getUpdates
#https://api.telegram.org/bot/5852909746:AAHIR3dTplmcrTwkVaCVgfJ7J23fTyImWQU/getUpdates
while counter < MAX_COUNTER:

    print('attempt =', counter)  #Чтобы видеть в консоли, что код живет

    updates = requests.get(f'{API_URL}{BOT_TOKEN}/getUpdates?offset={offset + 1}').json()

    if updates['result']:
        for result in updates['result']:
            offset = result['update_id']
            chat_id = result['message']['from']['id']
            requests.get(f'{API_URL}{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={TEXT}')

    time.sleep(1)
    counter += 1