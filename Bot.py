import discord
from discord.ext import commands
import json
import os
from flask import Flask, request, jsonify
import threading

# ---------- DATA ----------
DATA_FILE = "data.json"
data = {
    "paused": False,
    "logCount": 0,
    "totalGen": 0,
    "stealCount": 0,
    "lastBrainrot": "None",
    "lastTier": "None"
}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def load_data():
    global data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data.update(json.load(f))

load_data()

# ---------- DISCORD BOT ----------
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def pause(ctx):
    data["paused"] = True
    save_data()
    await ctx.send("⏸ **Logging Paused**\nUse `!resume` to start again.")

@bot.command()
async def resume(ctx):
    data["paused"] = False
    save_data()
    await ctx.send("▶ **Logging Resumed**")

@bot.command()
async def status(ctx):
    status = "⏸ Paused" if data["paused"] else "▶ Active"
    msg = (f"📊 **Aurora Status**\n"
           f"Status: {status}\n"
           f"Total Brainrots: {data['logCount']}\n"
           f"Total Generation: ${data['totalGen']}/s\n"
           f"Steals Detected: {data['stealCount']}\n"
           f"Last Brainrot: {data['lastBrainrot']} ({data['lastTier']})")
    await ctx.send(msg)

@bot.command()
async def stats(ctx):
    status = "⏸ Paused" if data["paused"] else "▶ Active"
    msg = (f"📈 **Aurora Statistics**\n"
           f"┌─────────────────────────\n"
           f"│ Brainrots Found: {data['logCount']}\n"
           f"│ Total Generation: ${data['totalGen']}/s\n"
           f"│ Steals Detected: {data['stealCount']}\n"
           f"│ Last Found: {data['lastBrainrot']}\n"
           f"│ Tier: {data['lastTier']}\n"
           f"│ Status: {status}\n"
           f"└─────────────────────────\n\n"
           f"Aurora Finder • discord.gg/gf22vrzQ7")
    await ctx.send(msg)

@bot.command()
async def clearlogs(ctx):
    data["logCount"] = 0
    data["totalGen"] = 0
    data["stealCount"] = 0
    data["lastBrainrot"] = "None"
    save_data()
    await ctx.send("🗑 **Logs Cleared**\nAll statistics have been reset.")

@bot.command()
async def reset(ctx):
    data["paused"] = False
    data["logCount"] = 0
    data["totalGen"] = 0
    data["stealCount"] = 0
    data["lastBrainrot"] = "None"
    data["lastTier"] = "None"
    save_data()
    await ctx.send("🔄 **Aurora Reset**\nEverything has been reset to default.")

# ---------- FLASK WEBHOOK RECEIVER ----------
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if data["paused"]:
        return jsonify({"status": "paused"}), 200

    payload = request.get_json()
    if not payload:
        return jsonify({"error": "No JSON"}), 400

    t = payload.get("type", "brainrot")
    
    if t == "steal":
        data["stealCount"] += 1
        data["logCount"] += 1
        data["lastBrainrot"] = payload.get("name", "Unknown")
        data["lastTier"] = payload.get("tier", "Unknown")
        print(f"🎯 STEAL: {payload.get('name')} — {payload.get('gen')}/s ({payload.get('tier')})")
    
    elif t == "batch":
        items = payload.get("items", [])
        total = 0
        for item in items:
            gen = str(item.get("gen", "0"))
            gen = gen.replace("M/s", "").replace("B/s", "").replace(",", "")
            try:
                total += int(float(gen))
            except:
                pass
        data["totalGen"] += total
        data["logCount"] += len(items)
        print(f"📦 BATCH: {len(items)} brainrots — Total: ${total}/s")
    
    elif t == "rebirth":
        user = payload.get("user", "Unknown")
        priority = payload.get("priority", "Unknown")
        rebirth_num = payload.get("rebirth", 0)
        print(f"🔄 REBIRTH: {user} — Priority: {priority}, Rebirth #{rebirth_num}")
    
    else:  # single brainrot
        gen = str(payload.get("gen", "0"))
        gen = gen.replace("M/s", "").replace("B/s", "").replace(",", "")
        try:
            gen = int(float(gen))
        except:
            gen = 0
        data["totalGen"] += gen
        data["logCount"] += 1
        data["lastBrainrot"] = payload.get("name", "Unknown")
        data["lastTier"] = payload.get("tier", "Unknown")
        print(f"✅ BRAINROT: {payload.get('name')} — ${payload.get('gen')}/s ({payload.get('tier')})")
    
    save_data()
    return jsonify({"status": "ok"}), 200

@app.route('/')
def home():
    return "Aurora Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# ---------- START BOTH ----------
if __name__ == "__main__":
    # Start Flask in a background thread
    threading.Thread(target=run_flask, daemon=True).start()
    # Start Discord bot
    bot.run(os.environ.get("DISCORD_TOKEN"))
