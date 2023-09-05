import discord
import requests
import config
from datetime import datetime
import json
import re


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

sc_info = "https://open.neis.go.kr/hub/schoolInfo"

service_key = config.service_key

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.content.startswith("$급식찾기"):
        school_name = message.content[len("$급식찾기 "):].strip()
        print(f'{message.author} 님이 검색한 학교 이름: {school_name}')

        params = {
            'KEY': service_key,
            'Type': 'json',
            'pIndex': '1',
            'pSize': '100',
            'SCHUL_NM': school_name
        }

        response = requests.get(sc_info, params=params)
        json_data = response.json()

        # ATPT_OFCDC_SC_CODE와 SD_SCHUL_CODE 추출 및 출력
        for item in json_data['schoolInfo'][1]['row']:
            # 시도교육청 코드
            atpt_ofcdc_sc_code = item['ATPT_OFCDC_SC_CODE']
            # 학교 코드
            sd_schul_code = item['SD_SCHUL_CODE']

        await message.channel.send("급식 찾는중...")
        today = datetime.today()
        today_date = today.strftime('%Y%m%d')

        meal = "https://open.neis.go.kr/hub/mealServiceDietInfo"

        params1 = {
            'KEY': service_key,
            'Type': 'json',
            'pIndex': '1',
            'pSize': '100',
            'ATPT_OFCDC_SC_CODE': atpt_ofcdc_sc_code,
            'SD_SCHUL_CODE': sd_schul_code,
            'MLSV_YMD': today_date
        }

        response = requests.get(meal, params=params1)
        json_data1 = response.json()

        if 'mealServiceDietInfo' in json_data1:
            for item in json_data1['mealServiceDietInfo'][1]['row']:
                ddish_nm = item['DDISH_NM']

                input_text = ddish_nm

                cleaned_text = re.sub(r'<br/>', '', input_text)
                cleaned_text = re.sub(r'\s*\(([^)]+)\)\s*', r' (\1) ', cleaned_text)

                data = cleaned_text

                formatted_data = data.replace(") ", ")\n").replace(")  (", ")\n(")

                await message.channel.send(formatted_data)
            
        else:
            await message.channel.send("급식 정보가 없습니다.")



client.run(config.BOT_TOKEN)
