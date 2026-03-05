import httpx
from pyrogram import Client, filters
from faker import Faker
from FUNC.usersdb_func import *
from TOOLS.check_all_func import *

# Map of supported country codes to Faker locales
COUNTRY_LOCALES = {
    'us': 'en_US', 'uk': 'en_GB', 'gb': 'en_GB', 'ca': 'en_CA',
    'au': 'en_AU', 'de': 'de_DE', 'fr': 'fr_FR', 'es': 'es_ES',
    'it': 'it_IT', 'br': 'pt_BR', 'mx': 'es_MX', 'in': 'en_IN',
    'jp': 'ja_JP', 'kr': 'ko_KR', 'cn': 'zh_CN', 'ru': 'ru_RU',
    'nl': 'nl_NL', 'se': 'sv_SE', 'no': 'no_NO', 'dk': 'da_DK',
    'fi': 'fi_FI', 'pl': 'pl_PL', 'pt': 'pt_PT', 'at': 'de_AT',
    'ch': 'de_CH', 'be': 'fr_BE', 'ie': 'en_IE', 'nz': 'en_NZ',
    'za': 'en_ZA', 'ar': 'es_AR', 'co': 'es_CO', 'cl': 'es_CL',
    'ke': 'en_US', 'ng': 'en_US', 'ph': 'en_PH', 'th': 'th_TH',
    'tr': 'tr_TR', 'ua': 'uk_UA', 'cz': 'cs_CZ', 'hu': 'hu_HU',
    'ro': 'ro_RO', 'bg': 'bg_BG', 'hr': 'hr_HR', 'sk': 'sk_SK',
}


@Client.on_message(filters.command("fake", [".", "/"]))
async def cmd_fake(Client, message):
    try:
        checkall = await check_all_thing(Client, message)
        if not checkall[0]:
            return

        role = checkall[1]

        try:
            if len(message.text.split(" ")) > 1:
                country_code = message.text.split(" ")[1].lower()
            else:
                country_code = 'us'

            locale = COUNTRY_LOCALES.get(country_code, 'en_US')
            fake = Faker(locale)

            fake_name = fake.name()
            fake_address = fake.street_address()
            fake_city = fake.city()
            fake_state = fake.state() if hasattr(fake, 'state') else fake.city()
            fake_country = country_code.upper()
            fake_zipcode = fake.postcode()
            fake_gender = fake.random_element(elements=('Male', 'Female'))
            fake_phone = fake.phone_number()

            resp = f"""
<b>Fake Info Created Successfully ✅</b>
━━━━━━━━━━━━━━
🆔 <b>Full Name:</b> <code>{fake_name}</code>
👤 <b>Gender:</b> <code>{fake_gender}</code>
🏠 <b>Street:</b> <code>{fake_address}</code>
🏙️ <b>City/Town/Village:</b> <code>{fake_city}</code>
🌍 <b>State/Province/Region:</b> <code>{fake_state}</code>
📮 <b>Postal Code:</b> <code>{fake_zipcode}</code>
📞 <b>Phone Number:</b> <code>{fake_phone}</code>
🌏 <b>Country:</b> <code>{fake_country}</code>
━━━━━━━━━━━━━━
<b>Checked By:</b> <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a> [ {role} ]
<b>Owned by:</b> <a href="tg://user?id=8239967579">KaiZen﹒ ⁺</a> [ @bhaskargg ]
"""
            await message.reply_text(resp)

        except Exception as e:
            await log_cmd_error(message)

    except Exception as outer_exception:
        await log_cmd_error(message)
