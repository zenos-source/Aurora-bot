import sys
import os

# ============================================================
# FIX: audioop module missing on Render (Python 3.11+)
# ============================================================
class AudioopModule:
    def lin2lin(self, fragment, width, newwidth):
        return fragment
    def add(self, fragment1, fragment2, width):
        return fragment1
    def bias(self, fragment, width, bias):
        return fragment
    def cross(self, fragment, width):
        return b''
    def findfactor(self, fragment, referenced):
        return 1.0
    def findfit(self, fragment, referenced):
        return (0, 1.0, fragment)
    def findmax(self, fragment, length):
        return 0
    def getsample(self, fragment, width, index):
        return 0
    def max(self, fragment, width):
        return 0
    def maxpp(self, fragment, width):
        return 0
    def minmax(self, fragment, width):
        return (0, 0)
    def mul(self, fragment, width, factor):
        return fragment
    def ratecv(self, fragment, width, nchannels, inrate, outrate, state, weightA, weightB):
        return (fragment, state)
    def reverse(self, fragment, width):
        return fragment
    def rms(self, fragment, width):
        return 0
    def tomono(self, fragment, width, lfactor, rfactor):
        return fragment
    def tostereo(self, fragment, width, lfactor, rfactor):
        return fragment

if 'audioop' not in sys.modules:
    sys.modules['audioop'] = AudioopModule()

# ============================================================
# NOW import discord
# ============================================================
import discord
from discord import Webhook
from discord.ext import commands
import json
import aiohttp
import asyncio
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================
TOKEN = os.environ.get("DISCORD_TOKEN")

# ============================================================
# WEBHOOK URLS FOR EACH TIER
# ============================================================
WEBHOOKS = {
    "og": "https://discord.com/api/webhooks/1524937313870680156/T-OLDr7VHEX2tGddOdYrEhBcvgfDsOoU9ujcizXOsIGAbHJaeGeyhVmyc9o-QFxtKDmO",
    "peak": "https://discord.com/api/webhooks/1524937630633037864/J5AviqbG51snENQhv_T2zXOqAVO91ZtDDzn7oPRO7HdROAb6WT1xysHzghQaWODfvya8",
    "ultralight": "https://discord.com/api/webhooks/1524937630633037864/J5AviqbG51snENQhv_T2zXOqAVO91ZtDDzn7oPRO7HdROAb6WT1xysHzghQaWODfvya8",
    "high": "https://discord.com/api/webhooks/1524937674392080517/6xCMCuTNbOefOOO6ArdsU0eKv19mGnaFUiYfLK0t-ZX2IWnhHIFYaAeZ6RKDtpBOdnAW",
    "mid": "https://discord.com/api/webhooks/1524937724144914564/Ku_E7hfdP0wc05JgIkSxR7VD35K5IHUAErsZH8fNWWJ2nqYMgHGlgx4jORwhyz-Q6rOt",
    "farmer": "https://discord.com/api/webhooks/1524937788909158410/LbVEVEADq2Qdoc66Ad4EeoxhlJuET5zAuHyGtB8_uIEAQDGH-z2KuOx8umN8tOykvxaL",
    "low": "https://discord.com/api/webhooks/1524937724144914564/Ku_E7hfdP0wc05JgIkSxR7VD35K5IHUAErsZH8fNWWJ2nqYMgHGlgx4jORwhyz-Q6rOt",
    "steal": "https://discord.com/api/webhooks/1525187027040206950/VS9dVJI6QCTOibyZbLBRbYjc70cI5w4FgRtADT09jQP3fIZvsze6FFMujSsSSdMb7izA",
    "rebirth": "https://discord.com/api/webhooks/1525124198161318018/mg18ITB78EOZb46DLH8qp2hNB8Vcp9HP5FtxvM1HP_GmiXw6_qyP04kRVREEx-vO5ilI",
    "default": "https://discord.com/api/webhooks/1524937313870680156/T-OLDr7VHEX2tGddOdYrEhBcvgfDsOoU9ujcizXOsIGAbHJaeGeyhVmyc9o-QFxtKDmO"
}

# ============================================================
# BRAINROT IMAGE URLS (All 62 confirmed working)
# ============================================================
BRAINROT_IMAGES = {
    "Skibidi Toilet": "https://static.wikia.nocookie.net/stealabr/images/a/a7/Default_Skibidi_Toilet.png/revision/latest/scale-to-width-down/200?cb=20260528092806",
    "Strawberry Elephant": "https://static.wikia.nocookie.net/stealabr/images/5/58/Strawberryelephant.png/revision/latest/scale-to-width-down/192?cb=20260317001745",
    "John Pork": "https://static.wikia.nocookie.net/stealabr/images/d/d2/John_Pork.png/revision/latest/scale-to-width-down/200?cb=20260502233229",
    "Meowl": "https://static.wikia.nocookie.net/stealabr/images/b/b8/Clear_background_clear_meowl_image.png/revision/latest/scale-to-width-down/138?cb=20251022133154",
    "Headless Horseman": "https://static.wikia.nocookie.net/stealabr/images/2/2a/Horseman.webp/revision/latest/scale-to-width-down/186?cb=20260704043035",
    "Elefanto Frigo": "https://static.wikia.nocookie.net/stealabr/images/4/4b/Elefanto_Frigo.png/revision/latest/scale-to-width-down/200?cb=20260417150142",
    "Signore Carapace": "https://static.wikia.nocookie.net/stealabr/images/4/4a/Default_Signore_Carapace.png/revision/latest/scale-to-width-down/200?cb=20260417150408",
    "Dragon Gingerini": "https://static.wikia.nocookie.net/stealabr/images/a/a6/Dragon_Gingerini.png/revision/latest/scale-to-width-down/200?cb=20260528114017",
    "Arcadragon": "https://static.wikia.nocookie.net/stealabr/images/4/47/Arcadragon_Brainrot.png/revision/latest/scale-to-width-down/200?cb=20260412144930",
    "Love Love Bear": "https://static.wikia.nocookie.net/stealabr/images/b/bf/Love_Love_Bear.png/revision/latest/scale-to-width-down/200?cb=20260417150552",
    "Dragon Cannelloni": "https://static.wikia.nocookie.net/stealabr/images/a/a5/Dragon_Cannelloni.png/revision/latest/scale-to-width-down/200?cb=20260428162417",
    "Dragon Aquanini": "https://static.wikia.nocookie.net/stealabr/images/0/0c/Dragon_aquanini_but_high_graphism.png/revision/latest/scale-to-width-down/200?cb=20260610135509",
    "La Casa Boo": "https://static.wikia.nocookie.net/stealabr/images/8/8c/La_Casa_Boo.png/revision/latest/scale-to-width-down/195?cb=20260707155348",
    "Hydra Dragon Cannelloni": "https://static.wikia.nocookie.net/stealabr/images/e/ee/Hydra_Dragon_Cannelloni.png/revision/latest/scale-to-width-down/174?cb=20260207220000",
    "Griffin": "https://static.wikia.nocookie.net/stealabr/images/f/f8/Griffin.png/revision/latest/scale-to-width-down/200?cb=20260417151951",
    "Bunny and Eggy": "https://static.wikia.nocookie.net/stealabr/images/6/65/Bunny_and_Eggy.png/revision/latest/scale-to-width-down/200?cb=20260625235918",
    "Digi Narwhal": "https://static.wikia.nocookie.net/stealabr/images/7/7f/Digi_Narwhal.png/revision/latest/scale-to-width-down/200?cb=20260419152454",
    "Antonio": "https://static.wikia.nocookie.net/stealabr/images/f/f0/Antonio.png/revision/latest/scale-to-width-down/200?cb=20260327204416",
    "Jelly Moby": "https://static.wikia.nocookie.net/stealabr/images/a/ad/Jelly_Moby.png/revision/latest/scale-to-width-down/200?cb=20260626000342",
    "Kalika Bros": "https://static.wikia.nocookie.net/stealabr/images/f/f3/Kalika_Bros.png/revision/latest/scale-to-width-down/200?cb=20260419152541",
    "Kraken": "https://static.wikia.nocookie.net/stealabr/images/d/d3/Kraken.png/revision/latest/scale-to-width-down/200?cb=20260616235047",
    "Rico Dinero": "https://static.wikia.nocookie.net/stealabr/images/3/3b/Rico_Dinero.png/revision/latest/scale-to-width-down/200?cb=20260412144551",
    "Rubrikiko": "https://static.wikia.nocookie.net/stealabr/images/9/9f/Rubrikiko.png/revision/latest/scale-to-width-down/200?cb=20260510142334",
    "Venuspino": "https://static.wikia.nocookie.net/stealabr/images/0/0c/Venuspino.png/revision/latest/scale-to-width-down/200?cb=20260616235620",
    "Bearito Cabinito": "https://static.wikia.nocookie.net/stealabr/images/6/6e/Bearito_Cabinito.png/revision/latest/scale-to-width-down/200?cb=20260616234921",
    "Rosey and Teddy": "https://static.wikia.nocookie.net/stealabr/images/9/9b/Rosey_and_Teddy.png/revision/latest/scale-to-width-down/200?cb=20260208175726",
    "Cerberus": "https://static.wikia.nocookie.net/stealabr/images/4/45/Cerberus.png/revision/latest/scale-to-width-down/195?cb=20260217181804",
    "Hydra Bunny": "https://static.wikia.nocookie.net/stealabr/images/0/0b/Hydra_Bunny.png/revision/latest/scale-to-width-down/200?cb=20260626000309",
    "Cooki and Milki": "https://static.wikia.nocookie.net/stealabr/images/9/96/Cooki_and_Milki.png/revision/latest/scale-to-width-down/200?cb=20260417153501",
    "La Supreme Combinasion": "https://static.wikia.nocookie.net/stealabr/images/c/c8/La_Supreme_Combinasion.png/revision/latest/scale-to-width-down/135?cb=20250825130920",
    "Capitano Moby": "https://static.wikia.nocookie.net/stealabr/images/b/be/Capitano_Moby.png/revision/latest/scale-to-width-down/200?cb=20260428162232",
    "Popcuru and Fizzuru": "https://static.wikia.nocookie.net/stealabr/images/8/82/Popcuru_and_Fizzuru.png/revision/latest/scale-to-width-down/200?cb=20260425231747",
    "Spooky and Pumpky": "https://static.wikia.nocookie.net/stealabr/images/d/d6/Spookypumpky.png/revision/latest/scale-to-width-down/200?cb=20251012023638",
    "Ketupat Bros": "https://static.wikia.nocookie.net/stealabr/images/4/4d/Ketupat_Bros.png/revision/latest/scale-to-width-down/200?cb=20260207220106",
    "Abyssaloco": "https://static.wikia.nocookie.net/stealabr/images/1/10/Abyssaloco.png/revision/latest/scale-to-width-down/200?cb=20260510004641",
    "Avocadorilla": "https://static.wikia.nocookie.net/stealabr/images/8/85/Avocadorilla.png/revision/latest/scale-to-width-down/193?cb=20260708203602",
    "Brutto Gialutto": "https://static.wikia.nocookie.net/stealabr/images/6/64/Brutto_Gialutto_New.png/revision/latest/scale-to-width-down/200?cb=20260327015458",
    "Caylusaurus": "https://static.wikia.nocookie.net/stealabr/images/3/30/Caylusaurus.png/revision/latest/scale-to-width-down/200?cb=20260626000058",
    "Ganganzelli Trulala": "https://static.wikia.nocookie.net/stealabr/images/b/b4/Ganganzelli_Trulala.png/revision/latest/scale-to-width-down/139?cb=20260709005214",
    "Gorillo Subwoofero": "https://static.wikia.nocookie.net/stealabr/images/0/08/Dubstep_boy.png/revision/latest/scale-to-width-down/166?cb=20250909170929",
    "Los Fruits": "https://static.wikia.nocookie.net/stealabr/images/d/dc/Los_Fruits.png/revision/latest/scale-to-width-down/200?cb=20260616235111",
    "Pretzo Robo": "https://static.wikia.nocookie.net/stealabr/images/0/0d/Pretzo_Robo.png/revision/latest/scale-to-width-down/200?cb=20260419152740",
    "Rhino Helicopterino": "https://static.wikia.nocookie.net/stealabr/images/1/10/Rhino_Helicopterino.png/revision/latest/scale-to-width-down/200?cb=20260322225518",
    "Bacuru and Egguru": "https://static.wikia.nocookie.net/stealabr/images/b/b5/Bacuru_and_Egguru.png/revision/latest/scale-to-width-down/200?cb=20260417154056",
    "Bananito": "https://static.wikia.nocookie.net/stealabr/images/7/7e/Bananito.png/revision/latest/scale-to-width-down/200?cb=20260417152109",
    "Baskito": "https://static.wikia.nocookie.net/stealabr/images/e/e6/Baskito.png/revision/latest/scale-to-width-down/200?cb=20260625234705",
    "Camera Ramena": "https://static.wikia.nocookie.net/stealabr/images/4/46/Camera_Ramena.png/revision/latest/scale-to-width-down/200?cb=20260419152435",
    "John Doe": "https://static.wikia.nocookie.net/stealabr/images/3/33/John_Doe.png/revision/latest/scale-to-width-down/200?cb=20260425232401",
    "Sushi Inu": "https://static.wikia.nocookie.net/stealabr/images/5/5b/Sushi_Inu.png/revision/latest/scale-to-width-down/200?cb=20260616235531",
    "Boppin Bunny": "https://static.wikia.nocookie.net/stealabr/images/b/bc/Boppin_Bunny.png/revision/latest/scale-to-width-down/200?cb=20260405151129",
    "Gym Bros": "https://static.wikia.nocookie.net/stealabr/images/b/b7/Gym_Bros.png/revision/latest/scale-to-width-down/200?cb=20260419152519",
    "Fragrama and Chocrama": "https://static.wikia.nocookie.net/stealabr/images/5/56/Fragrama.png/revision/latest/scale-to-width-down/200?cb=20251109011733",
    "Cigno Fulgoro": "https://static.wikia.nocookie.net/stealabr/images/f/f7/Cigno_Fulgoro.png/revision/latest/scale-to-width-down/200?cb=20260417152643",
    "Money Money Puggy": "https://static.wikia.nocookie.net/stealabr/images/d/d6/Money_Money_Puggy.png/revision/latest/scale-to-width-down/177?cb=20260217180308",
    "DJ Panda": "https://static.wikia.nocookie.net/stealabr/images/3/38/DJ_Panda.png/revision/latest/scale-to-width-down/134?cb=20260306024631",
    "Tang Tang Keletang": "https://static.wikia.nocookie.net/stealabr/images/c/ce/TangTangVfx.png/revision/latest/scale-to-width-down/199?cb=20251014025849",
    "Ketupat Kepat": "https://static.wikia.nocookie.net/stealabr/images/a/ac/KetupatKepat.png/revision/latest/scale-to-width-down/200?cb=20260324191002",
    "Garama and Madundung": "https://static.wikia.nocookie.net/stealabr/images/1/12/Garama_and_Madundung.png/revision/latest/scale-to-width-down/200?cb=20260417153345",
    "Money Money Bros": "https://static.wikia.nocookie.net/stealabr/images/e/e0/Money_Money_Bros.png/revision/latest/scale-to-width-down/200?cb=20260417153843",
    "Celestial Pegasus": "https://static.wikia.nocookie.net/stealabr/images/b/b2/Celestial_Pegasus.png/revision/latest/scale-to-width-down/200?cb=20260417152449",
    "La Secret Combinasion": "https://static.wikia.nocookie.net/stealabr/images/4/4f/La_Secret_Combinasion.png/revision/latest/scale-to-width-down/200?cb=20260419152549"
}

# ============================================================
# TIER MAPPING
# ============================================================
TIER_COLORS = {
    "og": 0xFFD700,
    "peak": 0x7C3AED,
    "ultralight": 0x7C3AED,
    "high": 0x10B981,
    "mid": 0xF59E0B,
    "farmer": 0xFB923C,
    "low": 0xEF4444,
    "steal": 0xFF6B6B,
    "rebirth": 0xF472B6
}

TIER_NAMES = {
    "og": "★ OG LIGHTS",
    "peak": "✦ PEAK",
    "ultralight": "✦ ULTRALIGHT",
    "high": "✦ HIGHLIGHT",
    "mid": "✦ MIDLIGHT",
    "farmer": "✦ FARMER LIGHT",
    "low": "✦ LOWLIGHT",
    "steal": "🎯 STEAL TRACKER",
    "rebirth": "🔄 REBIRTHING"
}

def get_tier_key(tier_name):
    tier_name = tier_name.upper().strip()
    if tier_name in ["OG"]: return "og"
    elif tier_name in ["PEAK", "ULTRALIGHT"]: return "peak"
    elif tier_name in ["HIGH", "HIGHLIGHT"]: return "high"
    elif tier_name in ["MID", "MIDLIGHT"]: return "mid"
    elif tier_name in ["FARMER", "FARMER LIGHT"]: return "farmer"
    elif tier_name in ["LOW", "LOWLIGHT"]: return "low"
    elif tier_name == "STEAL": return "steal"
    elif tier_name == "REBIRTH": return "rebirth"
    return "default"

def get_image_url(name):
    return BRAINROT_IMAGES.get(name, None)

def format_num(n):
    if n >= 1e12: return f"{n/1e12:.1f}T"
    if n >= 1e9: return f"{n/1e9:.1f}B"
    if n >= 1e6: return f"{n/1e6:.1f}M"
    if n >= 1e3: return f"{n/1e3:.1f}K"
    return str(n)

def parse_gen(gen_str):
    try:
        if isinstance(gen_str, (int, float)):
            return int(gen_str)
        s = str(gen_str).replace("/s", "").strip()
        num = float(''.join(c for c in s if c.isdigit() or c == '.'))
        if 'T' in s or 't' in s: return int(num * 1e12)
        if 'B' in s or 'b' in s: return int(num * 1e9)
        if 'M' in s or 'm' in s: return int(num * 1e6)
        if 'K' in s or 'k' in s: return int(num * 1e3)
        return int(num)
    except:
        return 0

# ============================================================
# STATE (Pause/Resume)
# ============================================================
PAUSED = False
STATS_FILE = "stats.json"

def load_stats():
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"logCount": 0, "totalGen": 0, "stealCount": 0, "lastBrainrot": "None", "lastTier": "None"}

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)

stats = load_stats()

# ============================================================
# DISCORD BOT SETUP
# ============================================================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def send_to_webhook(webhook_url, embed):
    if not webhook_url:
        return
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(webhook_url, session=session)
        await webhook.send(embed=embed, wait=True)

@bot.event
async def on_ready():
    print(f"✅ Aurora Bot online: {bot.user}")
    print(f"📡 Webhooks configured: {len([k for k,v in WEBHOOKS.items() if v])} channels")
    print(f"🖼️ Loaded {len(BRAINROT_IMAGES)} brainrot images")
    print(f"⏸ Paused: {PAUSED}")
    print(f"📊 Stats: {stats}")

# ============================================================
# !PAUSE COMMAND
# ============================================================
@bot.command(name="pause")
async def pause_logs(ctx):
    global PAUSED
    if PAUSED:
        embed = discord.Embed(
            title="⏸ Already Paused",
            description="Logging is already paused.\nUse `!resume` to start logging again.",
            color=0xF59E0B,
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Total logs: {stats['logCount']}")
        await ctx.send(embed=embed)
        return
    
    PAUSED = True
    
    embed = discord.Embed(
        title="⏸ Logging Paused",
        description="All brainrot logs will now be ignored.\nUse `!resume` to start logging again.",
        color=0xF59E0B,
        timestamp=datetime.now()
    )
    embed.add_field(name="📊 Stats", value=f"Total Logs: {stats['logCount']}\nTotal Gen: ${format_num(stats['totalGen'])}/s", inline=False)
    embed.set_footer(text="Aurora Finder • discord.gg/gf22vrzQ7")
    await ctx.send(embed=embed)

# ============================================================
# !RESUME COMMAND
# ============================================================
@bot.command(name="resume")
async def resume_logs(ctx):
    global PAUSED
    if not PAUSED:
        embed = discord.Embed(
            title="▶ Already Active",
            description="Logging is already active.\nUse `!pause` to pause logging.",
            color=0x10B981,
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Total logs: {stats['logCount']}")
        await ctx.send(embed=embed)
        return
    
    PAUSED = False
    
    embed = discord.Embed(
        title="▶ Logging Resumed",
        description="Brainrot logs are now active.\nUse `!pause` to pause logging.",
        color=0x10B981,
        timestamp=datetime.now()
    )
    embed.add_field(name="📊 Stats", value=f"Total Logs: {stats['logCount']}\nTotal Gen: ${format_num(stats['totalGen'])}/s", inline=False)
    embed.set_footer(text="Aurora Finder • discord.gg/gf22vrzQ7")
    await ctx.send(embed=embed)

# ============================================================
# !SEND COMMAND
# ============================================================
@bot.command(name="send")
async def send_log(ctx, *, json_data=None):
    global PAUSED, stats
    
    if PAUSED:
        embed = discord.Embed(
            title="⏸ Logging Paused",
            description="All logs are currently paused.\nUse `!resume` to start logging again.",
            color=0xF59E0B,
            timestamp=datetime.now()
        )
        await ctx.send(embed=embed)
        return
    
    if json_data is None:
        await ctx.send("❌ No data provided. Example: `!send {\"name\":\"Skibidi Toilet\",\"gen\":\"450M/s\",\"tier\":\"OG\"}`")
        return
    
    try:
        data = json.loads(json_data)
    except json.JSONDecodeError:
        await ctx.send("❌ Invalid JSON format")
        return
    
    name = data.get("name", "Unknown")
    gen = data.get("gen", "0")
    tier_display = data.get("tier", "Unknown")
    log_type = data.get("type", "brainrot")
    items = data.get("items", [])
    user = data.get("user", None)
    priority = data.get("priority", None)
    rebirth_num = data.get("rebirth", None)
    
    # Update stats
    stats["logCount"] += 1
    stats["lastBrainrot"] = name
    stats["lastTier"] = tier_display
    if log_type == "steal":
        stats["stealCount"] += 1
    else:
        stats["totalGen"] += parse_gen(gen)
    save_stats(stats)
    
    # Get tier key and webhook
    tier_key = get_tier_key(tier_display)
    webhook_url = WEBHOOKS.get(tier_key, WEBHOOKS.get("default"))
    
    image_url = get_image_url(name)
    color = TIER_COLORS.get(tier_key, 0x5865F2)
    tier_name = TIER_NAMES.get(tier_key, tier_display)
    
    # Build embed
    embed = discord.Embed(
        title=f"🔍 Aurora Finder • {tier_name}",
        color=color,
        timestamp=datetime.now()
    )
    
    if log_type == "steal":
        embed.title = f"🎯 {name} Stolen!"
        embed.description = f"**{tier_name}**"
        embed.add_field(name="💰 Generation", value=f"${gen}/s", inline=True)
    elif log_type == "batch" and items:
        list_text = ""
        for item in items:
            list_text += f"**{item['name']}** — ${item['gen']}/s\n"
        embed.description = f"**Batch of {len(items)} Brainrots Found**"
        embed.add_field(name="📋 Brainrots Found", value=list_text, inline=False)
    elif log_type == "rebirth":
        embed.title = "🔄 Rebirth Update"
        embed.description = f"**{user}** is rebirthing!"
        embed.color = 0xF472B6
        if rebirth_num:
            embed.add_field(name="🔄 Rebirth", value=f"#{rebirth_num}", inline=True)
        if priority:
            embed.add_field(name="🎯 Priority", value=priority, inline=True)
        embed.set_footer(text="Aurora Finder • discord.gg/gf22vrzQ7")
        await send_to_webhook(webhook_url, embed)
        return
    else:
        embed.add_field(name="🧠 Brainrot", value=f"**{name}** — **${gen}/s**", inline=False)
    
    if image_url:
        embed.set_thumbnail(url=image_url)
    
    embed.set_footer(text="Aurora Finder • discord.gg/gf22vrzQ7")
    
    await send_to_webhook(webhook_url, embed)

# ============================================================
# !STATUS COMMAND
# ============================================================
@bot.command(name="status")
async def status_cmd(ctx):
    status = "⏸ Paused" if PAUSED else "▶ Active"
    embed = discord.Embed(
        title="📊 Aurora Status",
        color=0x7C3AED,
        timestamp=datetime.now()
    )
    embed.add_field(name="Status", value=status, inline=True)
    embed.add_field(name="Total Brainrots", value=str(stats["logCount"]), inline=True)
    embed.add_field(name="Total Generation", value=f"${format_num(stats['totalGen'])}/s", inline=True)
    embed.add_field(name="Steals Detected", value=str(stats["stealCount"]), inline=True)
    embed.add_field(name="Last Brainrot", value=f"{stats['lastBrainrot']} ({stats['lastTier']})", inline=True)
    embed.set_footer(text="Aurora Finder • discord.gg/gf22vrzQ7")
    await ctx.send(embed=embed)

# ============================================================
# !STATS COMMAND
# ============================================================
@bot.command(name="stats")
async def stats_cmd(ctx):
    status = "⏸ Paused" if PAUSED else "▶ Active"
    embed = discord.Embed(
        title="📈 Aurora Statistics",
        color=0x7C3AED,
        timestamp=datetime.now()
    )
    embed.add_field(name="Brainrots Found", value=str(stats["logCount"]), inline=True)
    embed.add_field(name="Total Generation", value=f"${format_num(stats['totalGen'])}/s", inline=True)
    embed.add_field(name="Steals Detected", value=str(stats["stealCount"]), inline=True)
    embed.add_field(name="Last Found", value=stats["lastBrainrot"], inline=True)
    embed.add_field(name="Tier", value=stats["lastTier"], inline=True)
    embed.add_field(name="Status", value=status, inline=True)
    embed.set_footer(text="Aurora Finder • discord.gg/gf22vrzQ7")
    await ctx.send(embed=embed)

# ============================================================
# !CLEARLOGS COMMAND
# ============================================================
@bot.command(name="clearlogs")
async def clear_logs(ctx):
    global stats
    stats["logCount"] = 0
    stats["totalGen"] = 0
    stats["stealCount"] = 0
    stats["lastBrainrot"] = "None"
    stats["lastTier"] = "None"
    save_stats(stats)
    embed = discord.Embed(
        title="🗑 Logs Cleared",
        description="All statistics have been reset.",
        color=0xEF4444,
        timestamp=datetime.now()
    )
    embed.set_footer(text="Aurora Finder • discord.gg/gf22vrzQ7")
    await ctx.send(embed=embed)

# ============================================================
# !RESET COMMAND
# ============================================================
@bot.command(name="reset")
async def reset_bot(ctx):
    global stats, PAUSED
    stats["logCount"] = 0
    stats["totalGen"] = 0
    stats["stealCount"] = 0
    stats["lastBrainrot"] = "None"
    stats["lastTier"] = "None"
    PAUSED = False
    save_stats(stats)
    embed = discord.Embed(
        title="🔄 Aurora Reset",
        description="Everything has been reset to default.\nLogging is now **active**.",
        color=0x7C3AED,
        timestamp=datetime.now()
    )
    embed.set_footer(text="Aurora Finder • discord.gg/gf22vrzQ7")
    await ctx.send(embed=embed)

# ============================================================
# !TEST COMMAND
# ============================================================
@bot.command(name="test")
async def test_webhooks(ctx):
    await ctx.send("📡 Testing all webhook channels...")
    
    for tier_key, webhook_url in WEBHOOKS.items():
        if webhook_url and tier_key != "default":
            try:
                embed = discord.Embed(
                    title=f"🧪 Test: {tier_key.upper()}",
                    description=f"This is a test message for {TIER_NAMES.get(tier_key, tier_key)}",
                    color=TIER_COLORS.get(tier_key, 0x5865F2),
                    timestamp=datetime.now()
                )
                embed.set_footer(text="Aurora Finder • Test")
                await send_to_webhook(webhook_url, embed)
                await asyncio.sleep(0.5)
            except Exception as e:
                await ctx.send(f"❌ Failed to send to {tier_key}: {e}")
    
    await ctx.send("✅ Test complete!")

# ============================================================
# RUN BOT
# ============================================================
if __name__ == "__main__":
    if not TOKEN:
        print("❌ DISCORD_TOKEN environment variable not set!")
        exit(1)
    bot.run(TOKEN)
