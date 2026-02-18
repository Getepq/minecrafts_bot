import os
import json
import zipfile
import tempfile
import shutil

from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.state import State, StatesGroup
from bot.database.db_addons import add_addon, delete_addon
from bot.keyboard.addon_kb import all_addons_for_delete

ADMIN_ID = int(os.getenv('ADMIN_ID'))

rt = Router()


class AddAddonState(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_version = State()
    waiting_for_category = State()
    waiting_for_photo = State()
    waiting_for_file = State()
    waiting_for_bulk_zip = State()


def is_admin(user_id):
    return user_id in ADMIN_ID


@rt.message(Command('del_addon'))
async def process_del_addon(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        'АДДОН УДАЛЯЕТСЯ СРАЗУ ПРИ НАЖАТИИ!\nНажмите на кнопку, чтобы удалить аддон:',
        reply_markup=await all_addons_for_delete()
    )


@rt.callback_query(F.data.startswith("delete_addon_"))
async def delete_addon_handler(callback: CallbackQuery):
    addon_id = callback.data.split("_")[2]
    try:
        await delete_addon(addon_id)
        await callback.message.edit_text("Аддон удален.")
        await callback.answer("Удалено")
    except Exception as e:
        await callback.answer(f"Ошибка: {e}", show_alert=True)


@rt.message(Command("add_addon"))
async def start_add_addon(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Добавление аддона.\n\nВведите название:")
    await state.set_state(AddAddonState.waiting_for_name)


@rt.message(AddAddonState.waiting_for_name)
async def process_addon_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите описание:")
    await state.set_state(AddAddonState.waiting_for_description)


@rt.message(AddAddonState.waiting_for_description)
async def process_addon_desc(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите версию:")
    await state.set_state(AddAddonState.waiting_for_version)


@rt.message(AddAddonState.waiting_for_version)
async def process_addon_version(message: types.Message, state: FSMContext):
    await state.update_data(version=message.text)
    await message.answer("Введите категорию:")
    await state.set_state(AddAddonState.waiting_for_category)


@rt.message(AddAddonState.waiting_for_category)
async def process_addon_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("Отправьте фото для аддона:")
    await state.set_state(AddAddonState.waiting_for_photo)


@rt.message(AddAddonState.waiting_for_photo, F.photo)
async def process_addon_photo(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    await message.answer("Отправьте ZIP-файл с аддоном:")
    await state.set_state(AddAddonState.waiting_for_file)


@rt.message(AddAddonState.waiting_for_file, F.document)
async def process_addon_file(message: types.Message, state: FSMContext):
    if 'zip' not in message.document.mime_type and not message.document.file_name.endswith('.zip'):
        await message.answer("Отправьте именно ZIP архив!")
        return

    file_id = message.document.file_id
    data = await state.get_data()

    try:
        await add_addon(
            name=data['name'],
            description=data['description'],
            version=data['version'],
            category=data['category'],
            photo_id=data['photo_id'],
            file_id=file_id
        )
        await message.answer(f"Аддон {data['name']} добавлен!")
    except Exception as e:
        await message.answer(f"Ошибка при сохранении: {e}")

    await state.clear()


@rt.message(Command("import_addon"))
async def start_import_addon(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await message.answer("""Отправьте ZIP-архив со структурой:
archive.zip
├── Addon1/
│   ├── config.json
│   ├── preview.png
│   └── addon1.mcaddon
└── ...

config.json:
{
  "name": "Название",
  "description": "Описание",
  "version": "1.0",
  "category": "Категория",
  "photo_filename": "preview.png",
  "mod_filename": "addon1.mcaddon"
}""")
    await state.set_state(AddAddonState.waiting_for_bulk_zip)


@rt.message(AddAddonState.waiting_for_bulk_zip, F.document)
async def process_bulk_zip_addon(message: types.Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    if 'zip' not in message.document.mime_type and not message.document.file_name.endswith('.zip'):
        await message.answer("Отправьте ZIP архив!")
        return

    status_msg = await message.answer("Скачивание архива...")

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "upload.zip")

    try:
        await bot.download(message.document, destination=zip_path)
        await status_msg.edit_text("Распаковка...")

        extract_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_dir)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        added = []
        errors = []

        for folder_name in os.listdir(extract_dir):
            folder_path = os.path.join(extract_dir, folder_name)
            if not os.path.isdir(folder_path) or folder_name.startswith('__'):
                continue

            await status_msg.edit_text(f"Обработка: {folder_name}...")

            config_path = os.path.join(folder_path, "config.json")
            if not os.path.exists(config_path):
                errors.append(f"{folder_name}: config.json не найден")
                continue

            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception as e:
                errors.append(f"{folder_name}: Ошибка чтения JSON - {e}")
                continue

            required = ['name', 'description', 'version', 'category', 'photo_filename', 'mod_filename']
            missing = [f for f in required if f not in config]
            if missing:
                errors.append(f"{folder_name}: Отсутствуют поля: {', '.join(missing)}")
                continue

            photo_path = os.path.join(folder_path, config['photo_filename'])
            addon_path = os.path.join(folder_path, config['mod_filename'])

            if not os.path.exists(photo_path):
                errors.append(f"{folder_name}: Фото не найдено")
                continue

            if not os.path.exists(addon_path):
                errors.append(f"{folder_name}: Файл аддона не найден")
                continue

            try:
                photo_msg = await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=FSInputFile(photo_path)
                )
                photo_id = photo_msg.photo[-1].file_id
                await bot.delete_message(message.chat.id, photo_msg.message_id)
            except Exception as e:
                errors.append(f"{folder_name}: Ошибка загрузки фото - {e}")
                continue

            try:
                doc_msg = await bot.send_document(
                    chat_id=message.chat.id,
                    document=FSInputFile(addon_path)
                )
                file_id = doc_msg.document.file_id
                await bot.delete_message(message.chat.id, doc_msg.message_id)
            except Exception as e:
                errors.append(f"{folder_name}: Ошибка загрузки файла - {e}")
                continue

            try:
                await add_addon(
                    name=config['name'],
                    description=config['description'],
                    version=config['version'],
                    category=config['category'],
                    photo_id=photo_id,
                    file_id=file_id
                )
                added.append(config['name'])
            except Exception as e:
                errors.append(f"{folder_name}: Ошибка БД - {e}")

        report = f"Добавлено: {len(added)}, Ошибок: {len(errors)}"
        if added:
            report += f"\n\nУспешно:\n" + "\n".join(added)
        if errors:
            report += f"\n\nОшибки:\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                report += f"\n...и еще {len(errors) - 10}"

        await status_msg.edit_text(report)

    except zipfile.BadZipFile:
        await status_msg.edit_text("Неверный формат ZIP архива!")
    except Exception as e:
        await status_msg.edit_text(f"Ошибка: {e}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        await state.clear()