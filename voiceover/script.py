import argparse
from docx import Document
import re
import requests
from collections import defaultdict
import os
import json
import sys

# ElevenLabs API key (replace with your actual key)
API_KEY = 'ключ'

# Global settings (only output format remains)
global_settings = {
    'output_format': 'mp3_44100_128'
}

# Загрузка настроек персонажей из JSON-файла
try:
    with open('character_settings.json', 'r', encoding='utf-8') as f:
        character_settings = json.load(f)
except FileNotFoundError:
    print("Ошибка: файл character_settings.json не найден.")
    sys.exit(1)
except json.JSONDecodeError:
    print("Ошибка: неверный формат JSON в файле character_settings.json.")
    sys.exit(1)

# Counter for phrase numbers per character
phrase_counters = defaultdict(int)

def read_docx_file(input_file):
    """Читает .docx файл и возвращает список строк."""
    doc = Document(input_file)
    lines = []
    for para in doc.paragraphs:
        para_lines = para.text.split('\n')
        lines.extend(para_lines)
    return lines

def read_txt_file(input_file):
    """Читает .txt файл и возвращает список строк."""
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
    return lines

def extract_phrases(input_file):
    """Извлекает и очищает фразы из файла, возвращает список для озвучки и статистику."""
    file_extension = os.path.splitext(input_file)[1].lower()
    
    if file_extension == '.docx':
        lines = read_docx_file(input_file)
    elif file_extension == '.txt':
        lines = read_txt_file(input_file)
    else:
        print(f"Ошибка: неподдерживаемый формат файла '{file_extension}'. Поддерживаются .docx и .txt.")
        sys.exit(1)
    
    pattern = r'^([^(:]+)(?:\s*\(.*?\))?\s*:\s*(.*)$'
    phrases = []
    character_phrase_counts = defaultdict(int)
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        match = re.match(pattern, line)
        if match:
            character = match.group(1).strip()
            phrase = match.group(2).strip()
            character_key = ''.join(character.split())
            cleaned_phrase = re.sub(r'\s*\(.*?\)\s*', ' ', phrase).strip()
            
            if character_key in character_settings:
                phrases.append((character, character_key, cleaned_phrase))
                character_phrase_counts[character_key] += 1
            else:
                print(f"Warning: Character '{character_key}' not found in settings. Skipping.")
        else:
            print(f"Skipping non-dialogue: '{line}'")
    
    return phrases, character_phrase_counts

def print_phrase_statistics(character_phrase_counts):
    """Выводит статистику по количеству фраз для каждого персонажа."""
    print("\n=== Статистика по количеству фраз ===")
    if not character_phrase_counts:
        print("Фразы для озвучки отсутствуют.")
    else:
        for character, count in character_phrase_counts.items():
            print(f"{character}: {count} фраз(ы)")
    print("====================================\n")

def process_phrases_to_audio(phrases):
    """Озвучивает предварительно очищенные фразы."""
    for character, character_key, cleaned_phrase in phrases:
        phrase_counters[character_key] += 1
        number = phrase_counters[character_key]
        print(f"Processing phrase {number} for {character}: '{cleaned_phrase}'")
        generate_audio(character, character_key, number, cleaned_phrase)

def generate_audio(character_original, character_key, number, phrase):
    """Генерирует аудиофайл для заданной фразы и сохраняет его в папке персонажа."""
    settings = character_settings[character_key]
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings['voice_id']}"
    
    headers = {
        'xi-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    # Формируем voice_settings, включая только присутствующие параметры
    possible_voice_settings = ['speed', 'stability', 'similarity_boost', 'style', 'use_speaker_boost']
    voice_settings = {k: settings[k] for k in possible_voice_settings if k in settings}
    
    data = {
        'text': phrase,
        'model_id': settings['model_id'],  # Используем model_id из настроек персонажа
        'voice_settings': voice_settings
    }
    
    params = {
        'output_format': global_settings['output_format']
    }
    
    character_folder = character_original
    os.makedirs(character_folder, exist_ok=True)
    
    try:
        response = requests.post(url, headers=headers, json=data, params=params)
        if response.status_code == 200:
            filename = os.path.join(character_folder, f"{character_original}_{number}.mp3")
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"Saved '{filename}'")
        else:
            print(f"Error for phrase {number}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception occurred for phrase {number}: {str(e)}")

def process_docx_to_audio(input_file):
    """Обрабатывает файл, сначала извлекая фразы, затем озвучивая их."""
    phrases, character_phrase_counts = extract_phrases(input_file)
    print_phrase_statistics(character_phrase_counts)
    if not phrases:
        print("Нет фраз для озвучки. Завершаем работу.")
        sys.exit(0)
    process_phrases_to_audio(phrases)

def main():
    """Основная функция для парсинга аргументов и запуска процесса."""
    parser = argparse.ArgumentParser(description="Convert .docx or .txt character phrases to audio files.")
    parser.add_argument('input_file', help="Path to the input .docx or .txt file")
    args = parser.parse_args()
    
    try:
        process_docx_to_audio(args.input_file)
    except KeyboardInterrupt:
        print("\nСкрипт прерван пользователем.")
        sys.exit(0)

if __name__ == '__main__':
    main()
