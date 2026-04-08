import discord
from discord.ext import commands
import aiohttp
import time

TOKEN = 'MTQ5MTA5MTY3MDYxODM0MTQxNg.Gw1WNg.d2lybQ9KGVpgg1G_DqpboTssPQCMUqgtT6YMsE'
PREFIX = '!' 

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

session = None

@bot.event
async def on_ready():
    global session
    if session is None:
        session = aiohttp.ClientSession()
    print(f'🚀 บอทสายฟ้า (โหมดละเอียดพิเศษ) พร้อมใช้งาน!')

@bot.command()
async def check(ctx, phone: str):
    start_time = time.time()
    url = f"https://apitu.psnw.xyz/index.php?type=phone&value={phone}&mode=sff"

    try:
        async with session.get(url, timeout=10) as response:
            if response.status != 200:
                await ctx.send("⚠️ เซิร์ฟเวอร์ API ขัดข้อง")
                return

            full_data = await response.json()
            results = full_data.get('results') or {}
            resp_data = results.get('response-data') or {}
            
            if not resp_data:
                await ctx.send(f"❌ ไม่พบข้อมูลสำหรับเบอร์ `{phone}`")
                return

            # --- เจาะข้อมูลที่อยู่ ---
            addr_root = resp_data.get('address-list') or {}
            addr = addr_root.get('CUSTOMER_ADDRESS') or {}

            # --- ฟังก์ชันช่วยจัดการข้อมูลว่าง/วันที่ ---
            def clean(val): return val if val and str(val).strip() not in ["", "None", "NONE"] else "-"
            def fmt_date(d): return str(d).split('T')[0] if d and 'T' in str(d) else clean(d)

            # --- สร้าง Embed ---
            embed = discord.Embed(
                title=f"🔎 ข้อมูลลงทะเบียน: {phone}",
                color=0x2f3136 # สีเทาเข้มแบบ Discord Luxury
            )

            # 1. ข้อมูลส่วนบุคคล (เน้นรายละเอียด)
            name = f"{resp_data.get('title','')}{resp_data.get('firstname','')} {resp_data.get('lastname','')}".strip()
            personal_info = (
                f"👤 **ชื่อ-นามสกุล:** `{name}`\n"
                f"🆔 **เลขบัตร:** `{clean(resp_data.get('id-number'))}`\n"
                f"📅 **วันเกิด:** `{fmt_date(resp_data.get('birthdate'))}`\n"
                f"💳 **บัตรหมดอายุ:** `{fmt_date(resp_data.get('id-expire-date'))}`\n"
                f"🚻 **เพศ:** `{clean(resp_data.get('gender'))}` | **ภาษา:** `{clean(resp_data.get('language'))}`"
            )
            embed.add_field(name="📋 ข้อมูลเจ้าของเบอร์", value=personal_info, inline=False)

            # 2. ข้อมูลที่อยู่ (จัดเรียงใหม่ให้สวยงาม)
            address_full = (
                f"🏠 **บ้านเลขที่:** {clean(addr.get('number'))} **หมู่บ้าน:** {clean(addr.get('building-name'))}\n"
                f"🛣️ **ถนน:** {clean(addr.get('street'))} **ตำบล:** {clean(addr.get('sub-district'))}\n"
                f"🏙️ **อำเภอ:** {clean(addr.get('district'))} **จังหวัด:** {clean(addr.get('province'))}\n"
                f"📮 **รหัสไปรษณีย์:** {clean(addr.get('zip'))}"
            )
            embed.add_field(name="📍 ที่อยู่จดทะเบียน", value=address_full, inline=False)

            # 3. ข้อมูลซิมและสถานะ (ข้อมูลระบบที่เพิ่มมา)
            system_info = (
                f"🔹 **Customer ID:** `{clean(resp_data.get('customer-id'))}`\n"
                f"🔹 **ประเภทลูกค้า:** `{clean(resp_data.get('customer-type'))}`\n"
                f"🔹 **ระดับ:** `{clean(resp_data.get('customer-level'))}` (`{clean(resp_data.get('customer-sublevel'))}`)\n"
                f"📞 **เบอร์ติดต่อ:** `{clean(resp_data.get('contact-number'))}`"
            )
            embed.add_field(name="⚙️ ข้อมูลเชิงลึกระบบ", value=system_info, inline=False)

            # ฟุตเตอร์บอกเวลาประมวลผล
            elapsed = round(time.time() - start_time, 3)
            embed.set_footer(text=f"⚡ ดึงข้อมูลสำเร็จภายใน {elapsed} วินาที ้")

            await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"🚨 บอท Error: `{str(e)}`")

bot.run(MTQ5MTA5MTY3MDYxODM0MTQxNg.Gw1WNg.d2lybQ9KGVpgg1G_DqpboTssPQCMUqgtT6YMsE)
