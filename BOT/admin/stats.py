from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from FUNC.admin_auth import is_admin_or_owner


async def getallgc():
    from mongodb import gcdb
    return gcdb.find({}, {"_id": 0})

@Client.on_message(filters.command("stats", [".", "/"]))
async def stats(Client, message):
    try:
        user_id     = str(message.from_user.id)
        if not await is_admin_or_owner(user_id):
            resp = "<b>⛔ Access Denied — Admin only.</b>"
            await message.reply_text(resp, message.id)
            return

        chats         = 0
        total_gc      = 0
        redeemed      = 0
        total_user    = 0
        free_user     = 0
        premium_user  = 0
        paid_user     = 0
        get_all_chats = await getallchat()
        get_all_gc    = await getallgc() 
        get_all_user  = await getallusers()

        for item in get_all_chats:
            chats += 1

        for item in get_all_gc:
            total_gc += 1
            if item["status"] == "USED":
                redeemed += 1

        for item in get_all_user:
            total_user += 1
            if item["status"] == "FREE":
                free_user += 1
            elif item["status"] == "PREMIUM":
                premium_user += 1
            elif "N/A" not in item["plan"]:
                paid_user += 1

        done = f"""<b>
Lynix Core ⚡ @LynixCheckouter Statistics ✅
━━━━━━━━━━━━━━ 
Total Commands : 52
Database Type : MongoDB
Total Registered Users : {total_user}
Total Free Users : {free_user}
Total Premium Users : {premium_user}
Total Authorized Chat : {chats}
Total Giftcode Genarated : {total_gc}
Total Giftcode Redeemed : {redeemed}
Total Active Users Ratio : {premium_user * 3}

Status : Running
Checked On : {message.date}
    </b> """

        await message.reply_text(done, message.id)

    except:
        await log_cmd_error(message)
