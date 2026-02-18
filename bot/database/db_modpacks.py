import aiosqlite

DB_NAME = 'data/modpacks.db'

async def create_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS modpacks (
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
        async with db.execute('SELECT DISTINCT category FROM modpacks') as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

async def get_modpacks_by_category(category: str):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            'SELECT * FROM modpacks WHERE category = ?', (category,)
        ) as cursor:
            return await cursor.fetchall()

async def add_modpack(name, description, version, category, photo_id, file_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO modpacks (name, description, version, category, photo_id, file_id) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, description, version, category, photo_id, file_id))
        await db.commit()

async def get_all_modpacks():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM modpacks') as cursor:
            return await cursor.fetchall()

async def get_modpack(pack_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM modpacks WHERE id = ?', (pack_id,)) as cursor:
            return await cursor.fetchone()

async def delete_modpack(pack_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM modpacks WHERE id = ?', (pack_id,))
        await db.commit()

async def download_modpack(bot, pack_id, chat_id):
    modpack = await get_modpack(pack_id)
    if not modpack:
        return None

    await bot.send_document(
        chat_id=chat_id,
        document=modpack['file_id'],
        caption=f"📦 <b>{modpack['name']}</b>\n"
                f"📝 {modpack['description'] or 'Без описания'}\n"
                f"🔢 Версия: {modpack['version'] or 'Не указана'}",
        parse_mode='HTML'
    )
    return modpack