import config
import botogram
import mojangapi

bot = botogram.create(config.TELEGRAM_TOKEN)
bot.about = "This bot gives you information from the mojang api"
bot.owner = "@Paolo565"
bot.after_help = [
    "This bot is Open Source!",
    "github.com/paolo565/McTelegram",
]


def color_to_service_status(color):
    if color == 'green':
        return "<strong>Healthy</strong>"
    elif color == 'yellow':
        return "<strong>Unstable</strong>"
    else:
        return "<strong>Unavailable</strong>"


def log_request(command, chat, args):
    print((str(chat.id) if chat.username is None else "@" + chat.username) + " - /" + command + " " + ' '.join(args))


@bot.command("status")
def status_command(chat, args):
    """Tells you the status of mojang services"""
    log_request("status", chat, args)

    success, status = mojangapi.check_mojang_status()

    if not success:
        chat.send("Failed to check the mojang status :(")
        return

    text = '<a href="https://minecraft.net/en/">Minecraft.net</a>: ' + color_to_service_status(status['minecraft.net']) + "\n"
    text += '<a href="https://mojang.com/">Mojang Website</a>: ' + color_to_service_status(status['mojang.com']) + "\n"
    text += '<a href="https://accounts.mojang.com/">Mojang Accounts Website</a>: ' + color_to_service_status(status['account.mojang.com']) + "\n"
    text += 'Authentication Service: ' + color_to_service_status(status['auth.mojang.com']) + "\n"
    text += 'Multiplayer Session: ' + color_to_service_status(status['sessionserver.mojang.com']) + "\n"
    text += 'Skins: ' + color_to_service_status(status['skins.minecraft.net']) + "\n"
    text += 'Textures: ' + color_to_service_status(status['textures.minecraft.net']) + "\n"
    text += 'Public API: ' + color_to_service_status(status['api.mojang.com'])

    text += '\n\nMore Information: <a href="https://twitter.com/mojangstatus">twitter.com/mojangstatus</a>'

    chat.send(text, preview=False, syntax="html")


@bot.command("playerinfo")
def playerinfo_command(chat, args):
    """Tells you info about a user"""
    log_request("playerinfo", chat, args)

    if len(args) == 0:
        chat.send("Ok, now tell me the username or the uuid", reply_to=chat, extra=botogram.ForceReply(data={
            'force_reply': True,
            'selective': True
        }))
        return

    reply_to_playerinfo(chat, args[0])


@bot.message_matches("[\s\S]*")
def on_message(chat, message):
    reply_to_playerinfo(chat, message.text)


def reply_to_playerinfo(chat, username_or_uuid):
    username = None
    premium = True
    if len(username_or_uuid) == 36:
        uid = username_or_uuid.replace('-', '')
    elif len(username_or_uuid) == 32:
        uid = username_or_uuid
    elif len(username_or_uuid) <= 16:
        success, premium, username, uid = mojangapi.get_uid_from_username(username_or_uuid)
        if not success:
            chat.send("Failed to fetch data about the user, retry later.")
            return
    else:
        chat.send("Invalid Username or UUID.")
        return

    if premium:
        success, name_history = mojangapi.get_name_history_from_uid(uid)
        if not success:
            chat.send("Failed to fetch data about the user, retry later.")
            return

        if name_history is None:
            chat.send("Invalid Username or UUID.")
            return

        if username is None:
            username = name_history[-1]['name']
            premium = False
    else:
        chat.send("Invalid Username or UUID.")
        return

    uuid = uid[0:8] + '-' + uid[8:12] + '-' + uid[12:16] + '-' + uid[16:20] + '-' + uid[20:32]

    text = "Username: <b>" + username + "</b>\n"
    text += "UID: <b>" + uid + "</b>\n"
    text += "UUID: <b>" + uuid + "</b>\n"
    text += "Account Type: <b>" + ("Premium" if premium else "Cracked") + "</b>\n"
    text += "Head Command: <b>/give @p minecraft:skull 1 3 {SkullOwner:\"" + username + "\"}</b>\n"
    text += "More Info: <a href=\"https://namemc.com/profile/" + uuid + "\">namemc.com/profile/" + username + "</a>"

    chat.send(text, preview=False, syntax="html")


if __name__ == "__main__":
    bot.run()
