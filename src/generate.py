import base64
import json
import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

PROMPT_FILE = 'prompts/inputs.json'
ARTICLE_INSTRUCTIONS_FILE = 'prompts/article-instructions.txt'
IMAGE_INSTRUCTIONS_FILE = 'prompts/image-instructions.txt'
IMAGES_PATH = 'images/'
API_KEY = os.getenv("API_KEY")
client = OpenAI(api_key=API_KEY)


def get_prompt():
    with open(PROMPT_FILE, 'r') as file:
        data = json.load(file)
        return data.get('5')
    return False


def get_article_instructions():
    with open(ARTICLE_INSTRUCTIONS_FILE, 'r') as file:
        return file.read()
    return False


def get_image_instructions():
    with open('prompts/image-instructions.txt', 'r') as file:
        return file.read()
    return False


def create_article(article_header):
    prompt = get_prompt()
    instructions = get_article_instructions()

    if not prompt or not instructions:
        print("Error: Prompt or instructions not found.")
        return False

    prompt = f"{prompt}\n{article_header}"

    response = client.responses.create(
        model="gpt-5.6-terra",
        instructions=instructions,
        input=prompt,
    )
    return response.output_text


def create_image(article_title):
    instructions = get_image_instructions()

    if not instructions:
        print("Error: Image instructions not found.")
        return False

    prompt = f"{instructions}\n{article_title}"

    response = client.images.generate(
        model="gpt-image-2",
        prompt=prompt,
        size="1024x1024",
        quality="high",
        n=1,
    )
    print("Image created.\n")
    return response.data[0].b64_json


def save_image(image_b64, filename):
    if not image_b64:
        print("Failed to save image: no image data.\n")
        return

    with open(os.path.join(IMAGES_PATH, filename), 'wb') as file:
        file.write(base64.b64decode(image_b64))
    print(f"Image saved as {filename}\n")

