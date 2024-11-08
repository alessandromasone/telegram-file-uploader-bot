import asyncio
import json
import os
from utils.telegram_client import create_telegram_client, upload_file
from utils.file_manager import load_uploaded_files, is_supported_file

# Caricamento configurazione
with open('config.json') as config_file:
    config = json.load(config_file)

api_id = config['api_id']
api_hash = config['api_hash']
bot_token = config['bot_token']
group_link = config['group_link']
thread_id = config['thread_id']
folders = config['folders']

async def main():
    client = await create_telegram_client(api_id, api_hash, bot_token)
    uploaded_files = load_uploaded_files()

    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv']
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

    for folder_path in folders:
        if not os.path.exists(folder_path):
            print(f"Folder {folder_path} does not exist, skipping.")
            continue

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if is_supported_file(file_path, uploaded_files, video_extensions, image_extensions):
                await upload_file(client, file_path, group_link, thread_id, video_extensions, image_extensions)
            else:
                print(f"File {filename} already uploaded or unsupported, skipping...")

    await client.disconnect()

asyncio.run(main())
