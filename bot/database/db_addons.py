import aiosqlite

DB_NAME = 'data/addons.db'

async def create_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS addons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                version TEXT,
                category TEXT,
                photo_id TEXT,
                file_id TEXT NOT NULL
            )
        ''')
        await db.commit()

async def get_all_categories():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT DISTINCT category FROM addons') as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

async def get_addons_by_category(category: str):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            'SELECT * FROM addons WHERE category = ?', (category,)
        ) as cursor:
            return await cursor.fetchall()

async def add_addon(name, description, version, category, photo_id, file_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO addons (name, description, version, category, photo_id, file_id) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, description, version, category, photo_id, file_id))
        await db.commit()

async def get_all_addons():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM addons') as cursor:
            return await cursor.fetchall()

async def get_addon(addon_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM addons WHERE id = ?', (addon_id,)) as cursor:
            return await cursor.fetchone()

async def delete_addon(addon_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM addons WHERE id = ?', (addon_id,))
        await db.commit()


async def download_addon(bot, addon_id, chat_id):
    addon = await get_addon(addon_id)
    if not addon:
        return None

    await bot.send_document(
        chat_id=chat_id,
        document=addon['file_id'],
        caption=f"📦 <b>{addon['name']}</b>\n"
                f"📝 {addon['description'] or 'Без описания'}\n"
                f"🔢 Версия: {addon['version'] or 'Не указана'}",
        parse_mode='HTML'
    )
    return addon