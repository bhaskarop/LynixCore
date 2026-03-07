import json
from mongodb import adminsdb


def _get_owner_id():
    """Read OWNER_ID from config.json."""
    data = json.loads(open("FILES/config.json", "r", encoding="utf-8").read())
    return str(data["OWNER_ID"])


def is_owner(user_id):
    """Return True if user_id matches the bot owner."""
    return str(user_id) == _get_owner_id()


async def is_admin(user_id):
    """Return True if user_id is in the admins database."""
    doc = adminsdb.find_one({"id": str(user_id)})
    return doc is not None


async def is_admin_or_owner(user_id):
    """Return True if user_id is the owner OR an admin."""
    uid = str(user_id)
    if uid == _get_owner_id():
        return True
    doc = adminsdb.find_one({"id": uid})
    return doc is not None


async def add_admin(user_id, added_by):
    """Add a user as admin. Returns True if new, False if already exists."""
    uid = str(user_id)
    if adminsdb.find_one({"id": uid}):
        return False
    adminsdb.insert_one({
        "id": uid,
        "added_by": str(added_by),
    })
    return True


async def remove_admin(user_id):
    """Remove an admin. Returns True if removed, False if not found."""
    result = adminsdb.delete_one({"id": str(user_id)})
    return result.deleted_count > 0


async def get_all_admins():
    """Return list of all admin documents."""
    return list(adminsdb.find({}, {"_id": 0}))
