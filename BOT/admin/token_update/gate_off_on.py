import json
from pyrogram import Client, filters
from FUNC.defs import error_log
from FUNC.admin_auth import is_admin_or_owner

@Client.on_message(filters.command("gateoff", [".", "/"]))
async def update_dead_amount(Client, message):
    try:
        user_id = str(message.from_user.id)
        if not await is_admin_or_owner(user_id):
            resp = "<b>⛔ Access Denied — Admin only.</b>"
            await message.reply_text(resp)
            return

        try:
            new_command = str(message.text.split(" ")[1])
        except IndexError:
            new_command = str(message.reply_to_message.text)

        with open("FILES/deadsk.json", "r", encoding="UTF-8") as f:
            data = json.load(f)

        if "gate_active" not in data:
            data["gate_active"] = []

        if f"/{new_command}" in data["gate_active"] or f".{new_command}" in data["gate_active"]:
            resp = f"""<b>
The /{new_command} gate is already off.⚠️
    </b>"""
            await message.reply_text(resp)
            return

        commands_to_add = [
            f"/{new_command}", f".{new_command}", f"/m{new_command}",
            f".m{new_command}", f"/{new_command}txt", f".{new_command}txt"
        ]
        data["gate_active"].extend(commands_to_add)

        with open("FILES/deadsk.json", "w", encoding="UTF-8") as f:
            json.dump(data, f, indent=4)

        resp = f"""<b>
Now /{new_command} gate not available.⚠️
    </b>"""
        await message.reply_text(resp)

    except Exception as e:
        await log_cmd_error(message)

@Client.on_message(filters.command("gateon", [".", "/"]))
async def remove_command(Client, message):
    try:
        user_id = str(message.from_user.id)
        if not await is_admin_or_owner(user_id):
            resp = "<b>⛔ Access Denied — Admin only.</b>"
            await message.reply_text(resp)
            return

        try:
            command_to_remove = str(message.text.split(" ")[1])
        except IndexError:
            command_to_remove = str(message.reply_to_message.text)

        with open("FILES/deadsk.json", "r", encoding="UTF-8") as f:
            data = json.load(f)

        if "gate_active" in data:
            commands_to_remove = [
                f"/{command_to_remove}", f".{command_to_remove}", f"/m{command_to_remove}",
                f".m{command_to_remove}", f"/{command_to_remove}txt", f".{command_to_remove}txt"
            ]
            original_length = len(data["gate_active"])
            data["gate_active"] = [command for command in data["gate_active"] if command not in commands_to_remove]
            new_length = len(data["gate_active"])

            if original_length == new_length:
                resp = f"<b>maybe already active this /{command_to_remove}.</b>"
            else:
                with open("FILES/deadsk.json", "w", encoding="UTF-8") as f:
                    json.dump(data, f, indent=4)

                resp = f"""<b>
{command_to_remove} gate has been reactivated✅
    </b>"""
        else:
            resp = f"<b>maybe already active this /{command_to_remove}.</b>"

        await message.reply_text(resp)

    except Exception as e:
        await log_cmd_error(message)
