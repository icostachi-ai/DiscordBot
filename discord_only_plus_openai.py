from dotenv import load_dotenv
from openai import OpenAI  # OpenAI library
import discord
import os

# Set OpenAI API key
load_dotenv()
OPENAI_KEY = os.getenv('OPENAI_KEY')
oa_client = OpenAI(api_key=OPENAI_KEY)

# Ask OpenAI to respond like a pirate
def call_openai(question):
    try:
        # Call the OpenAI API with system prompt for pirate style
        completion = oa_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful pirate assistant. Respond to every query in pirate speak, with 'Arrr!' and nautical flair."},
                {"role": "user", "content": question}
            ]
        )
        # Extract the response
        response = completion.choices[0].message.content
        print(response)
        return response
    except Exception as e:
        error_msg = f"Aye, trouble on the high seas: {str(e)}"
        print(error_msg)
        return error_msg

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
        print("Sent hello response")
    if message.content.startswith('$question'):
        print(f"Message: {message.content}")
        message_content = message.content.split("$question")[1].strip()  # Split and clean up
        print(f"Question: {message_content}")
        response = call_openai(message_content)
        print(f"Assistant: {response}")
        print("---")
        await message.channel.send(response)

client.run(os.getenv('TOKEN'))
