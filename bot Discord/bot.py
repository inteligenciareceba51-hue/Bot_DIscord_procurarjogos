import discord
from discord.ext import commands, tasks
import requests
import os
from dotenv import load_dotenv
from keep_alive import keep_alive

# Carrega o token do arquivo .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# ID do canal onde o bot vai postar (substitua pelo seu ID)
CANAL_ID = 1006918028346269737 

# CONFIGURAÇÃO DE INTENTS (ESSENCIAL PARA NÃO DAR ERRO)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix='!', intents=intents)

def buscar_jogos():
    url = "https://www.gamerpower.com/api/giveaways"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Erro ao buscar na API: {e}")
    return []

@tasks.loop(hours=6)
async def checar_jogos():
    # Espera o bot estar pronto antes de tentar enviar
    await bot.wait_until_ready()
    try:
        canal = await bot.fetch_channel(CANAL_ID)
    except discord.NotFound:
        print(f"Erro: Canal com ID {CANAL_ID} não encontrado (Verifique se o ID está certo e se o bot está no servidor).")
        return
    except discord.Forbidden:
        print(f"Erro: O bot não tem permissão para ver o canal com ID {CANAL_ID}.")
        return
    except Exception as e:
        print(f"Erro inesperado ao buscar canal: {e}")
        return

    jogos = buscar_jogos()
    # Filtra apenas jogos da Epic ou Steam
    filtrados = [j for j in jogos if "Epic Games" in j['platforms'] or "Steam" in j['platforms']]
    
    if not filtrados:
        return

    for game in filtrados[:3]: 
        embed = discord.Embed(
            title=game['title'], 
            url=game['open_giveaway_url'], 
            color=0x00ff00
        )
        embed.set_thumbnail(url=game['thumbnail'])
        embed.add_field(name="Plataforma", value=game['platforms'], inline=True)
        embed.add_field(name="Preço Original", value=game['worth'], inline=True)
        await canal.send(embed=embed)

@bot.event
async def on_ready():
    print(f'Bot logado com sucesso como {bot.user}')
    if not checar_jogos.is_running():
        checar_jogos.start()

@bot.command()
async def checar(ctx):
    """Comando manual para forçar uma verificação"""
    await ctx.send("🔍 Procurando ofertas na Epic Games e Steam...")
    await checar_jogos()

keep_alive()
bot.run(TOKEN)