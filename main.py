import difflib
import json
import os
import random
import threading
from pathlib import Path
import customtkinter as ctk
import discord
from discord.ext import commands
from dotenv import load_dotenv
import time

MOODS_FILE = Path("moods.json")

def save_moods():
    # convert tuples to lists automatically through JSON
    with open(MOODS_FILE, "w", encoding="utf-8") as f:
        json.dump(moods, f, indent=4, ensure_ascii=False)


def load_moods():
    global moods

    if not MOODS_FILE.exists():
        return

    with open(MOODS_FILE, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    # convert JSON lists back into tuples where needed
    for mood_name, config in loaded.items():
        config["extend_range"] = tuple(config["extend_range"])
        config["words_per_sentence_range"] = tuple(config["words_per_sentence_range"])

    moods.update(loaded)

moods = {}
load_moods()

def get_similar_moods():
    query = search.get().lower().strip()

    reload(list(moods.keys()))

    names = list(moods.keys())

    # get close matches
    matches = difflib.get_close_matches(query, names, n=50, cutoff=0.3)

    # also include substring matches (so short queries still work)
    substring = [m for m in names if query in m.lower()]

    # combine + remove duplicates
    reload(list(dict.fromkeys(substring + matches)))

def set_mood(mood_to_set):
    global mood
    if mood_to_set == mood:
        return
    mood = mood_to_set
    print(f"Setting mood to {mood}")
    button = ctk.CTkButton(
        frame2,
        text=mood_to_set,
        command=lambda j=mood_to_set: set_mood(j)
    )
    button.pack()

def reload(keys):
    for widget in frame.winfo_children():
        widget.destroy()

    cols = 3
    for idx, mood_name in enumerate(keys):
        row = idx // cols
        col = idx % cols

        button = ctk.CTkButton(
            frame,
            text=mood_name,
            command=lambda j=mood_name: set_mood(j)
        )
        button.grid(row=row, column=col, padx=5, pady=5)

root = ctk.CTk()

root.geometry("500x400")

search = ctk.CTkEntry(root, placeholder_text="Search")
search.bind("<KeyRelease>", lambda e: get_similar_moods())
search.pack()

# ai_gen = ctk.CTkEntry(root, placeholder_text="Search")
# ai_gen.pack()
# ai_gen_button = ctk.CTkButton(root, text="Generate", command=lambda j=ai_gen.get(): generate_ai_mood(j))
# ai_gen_button.pack()

frame = ctk.CTkScrollableFrame(root)
frame.pack(fill="both", expand=True)

root2 = ctk.CTkToplevel(root)
root2.geometry("200x400")
frame2 = ctk.CTkScrollableFrame(root2)
frame2.pack(fill="both", expand=True)

mood = ""
set_mood("happy")

reload(moods.keys())

def random_cat_sound():
    parts = []
    sounds = moods[mood]["sounds"]
    punctuation = moods[mood]["punctuation"]
    upper_chance_per_letter = moods[mood]["upper_chance_per_letter"]
    extend_range = moods[mood]["extend_range"]
    words_per_sentence_range = moods[mood]["words_per_sentence_range"]
    extend_chance = moods[mood]["extend_chance"]
    upper_chance_per_word = moods[mood]["upper_chance_per_word"]
    stutter_chance = moods[mood]["stutter_chance"]

    for _ in range(random.randint(*words_per_sentence_range)):
        s = random.choice(sounds)

        if random.random() < extend_chance:
            for char in ["o", "r", "w"]:
                if char in s:
                    s = s.replace(char, char * random.randint(*extend_range))

        if random.random() < upper_chance_per_word:
            s = "".join(c.upper() if random.random() < upper_chance_per_letter else c for c in s)

        if random.random() < stutter_chance and len(s) > 1:
            s = s[0] + "-" + s

        parts.append(s)

    return " ".join(parts) + random.choice(punctuation)

def different_mood():
    while 1:
        other_moods = moods[mood]["other_moods"]
        chance_to_change_mood = moods[mood]["chance_to_change_mood"]
        if random.random() < chance_to_change_mood:
            set_mood(random.choices(
                list(other_moods.keys()),
                weights=list(other_moods.values()),
                k=1
            )[0])
        time.sleep(1)

class Client(commands.Bot):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.lower().startswith("trixie"):
            await message.channel.send("Meow!")
            await message.channel.send("Pu"+"r"*random.randint(6, 12)+"...")
        else:
            if random.random() > 0.1:
                await message.channel.send(
                    random_cat_sound()
                )


intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents)

GUILD_ID = discord.Object(id=1500274236386836590)

print(moods.keys())

threadchangemood = threading.Thread(target=different_mood)
threadchangemood.start()
load_dotenv()
thread = threading.Thread(target=client.run, args=(os.getenv("BOT_TOKEN"),))
thread.start()
root.mainloop()

