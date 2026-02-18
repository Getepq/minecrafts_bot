import os
import json
import zipfile
import tempfile
import shutil
import traceback

from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile  # FSInputFile должен быть здесь!
from aiogram.fsm.state import State, StatesGroup
from bot.database.db_modpacks import add_modpack, delete_modpack
from bot.keyboard.mod_kb import all_modpacks_for_delete

ADMIN_ID = int(os.getenv('ADMIN_ID'))

rt = Router()


class AddModpackState(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_version = State()
    waiting_for_category = State()
    waiting_for_photo = State()
    waiting_for_file = State()
    waiting_for_bulk_zip = State()


def is_admin(user_id):
    return user_id in ADMIN_ID


@rt.message(Command('del'))
async def process_del(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        'МОДПАК УДАЛЯЕТСЯ СРАЗУ ПРИ НАЖАТИИ!\nНажмите на кнопку, чтобы удалить модпак:',
        reply_markup=await all_modpacks_for_delete()
    )


@rt.callback_query(F.data.startswith("delete_mod_"))
async def delete_pack_handler(callback: CallbackQuery):
    pack_id = callback.data.split("_")[2]
    try:
        await delete_modpack(pack_id)
        await callback.message.edit_text("Модпак удален.")
        await callback.answer("Удалено")
    except Exception as e:
        await callback.answer(f"Ошибка: {e}", show_alert=True)


@rt.message(Command("add"))
async def start_add(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Добавление модпака.\n\nВведите название:")
    await state.set_state(AddModpackState.waiting_for_name)


@rt.message(AddModpackState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите описание:")
    await state.set_state(AddModpackState.waiting_for_description)


@rt.message(AddModpackState.waiting_for_description)
async def process_desc(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите версию:")
    await state.set_state(AddModpackState.waiting_for_version)


@rt.message(AddModpackState.waiting_for_version)
async def process_version(message: types.Message, state: FSMContext):
    await state.update_data(version=message.text)
    await message.answer("Введите категорию:")
    await state.set_state(AddModpackState.waiting_for_category)


@rt.message(AddModpackState.waiting_for_category)
async def process_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("Отправьте фото для модпака:")
    await state.set_state(AddModpackState.waiting_for_photo)


@rt.message(AddModpackState.waiting_for_photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    await message.answer("Отправьте ZIP-файл с модпаком:")
    await state.set_state(AddModpackState.waiting_for_file)


@rt.message(AddModpackState.waiting_for_file, F.document)
async def process_file(message: types.Message, state: FSMContext):
    if 'zip' not in message.document.mime_type and not message.document.file_name.endswith('.zip'):
        await message.answer("Отправьте именно ZIP архив!")
        return

    file_id = message.document.file_id
    data = await state.get_data()

    try:
        await add_modpack(
            name=data['name'],
            description=data['description'],
            version=data['version'],
            category=data['category'],
            photo_id=data['photo_id'],
            file_id=file_id
        )
        await message.answer(f"Модпак {data['name']} добавлен!")
    except Exception as e:
        await message.answer(f"Ошибка при сохранении: {e}")

    await state.clear()


@rt.message(Command("import"))
async def start_import(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await message.answer("""Отправьте ZIP-архив со структурой:
archive.zip
├── Modpack1/
│   ├── config.json
│   ├── preview.png
│   └── modpack1.mcpack
└── ...

config.json:
{
  "name": "Название",
  "description": "Описание",
  "version": "1.0",
  "category": "Категория",
  "photo_filename": "preview.png",
  "mod_filename": "modpack1.mcpack"
}""")
    await state.set_state(AddModpackState.waiting_for_bulk_zip)


@rt.message(AddModpackState.waiting_for_bulk_zip, F.document)
async def process_bulk_zip(message: types.Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    if not message.document.file_name or not message.document.file_name.endswith('.zip'):
        await message.answer("Отправьте ZIP архив!")
        return

    status_msg = await message.answer("Скачивание архива...")

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "upload.zip")

    try:
        # Скачиваем файл
        await bot.download(message.document, destination=zip_path)
        await status_msg.edit_text("Распаковка...")

        # Создаем папку для распаковки
        extract_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)

        # Распаковываем
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # Проверяем что распаковалось
        contents = os.listdir(extract_dir)
        await status_msg.edit_text(f"Найдено папок: {len(contents)}")

        added = []
        errors = []
        processed = 0

        # Перебираем папки в корне архива
        for folder_name in contents:
            folder_path = os.path.join(extract_dir, folder_name)

            # Пропускаем если это не папка или служебная
            if not os.path.isdir(folder_path) or folder_name.startswith('__') or folder_name.startswith('.'):
                continue

            processed += 1
            await status_msg.edit_text(f"Обработка {processed}: {folder_name}...")

            config_path = os.path.join(folder_path, "config.json")

            # Проверяем наличие config.json
            if not os.path.exists(config_path):
                errors.append(f"{folder_name}: config.json не найден")
                continue

            # Читаем config
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except json.JSONDecodeError as e:
                errors.append(f"{folder_name}: Неверный JSON - {str(e)}")
                continue
            except Exception as e:
                errors.append(f"{folder_name}: Ошибка чтения файла - {str(e)}")
                continue

            # Проверяем обязательные поля
            required = ['name', 'description', 'version', 'category', 'photo_filename', 'mod_filename']
            missing = [f for f in required if f not in config or not config[f]]
            if missing:
                errors.append(f"{folder_name}: Отсутствуют поля: {', '.join(missing)}")
                continue

            # Проверяем файлы
            photo_path = os.path.join(folder_path, config['photo_filename'])
            mod_path = os.path.join(folder_path, config['mod_filename'])

            if not os.path.exists(photo_path):
                errors.append(f"{folder_name}: Фото '{config['photo_filename']}' не найдено")
                continue

            if not os.path.exists(mod_path):
                errors.append(f"{folder_name}: Файл '{config['mod_filename']}' не найден")
                continue

            # Загружаем фото в Telegram
            try:
                photo_msg = await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=FSInputFile(photo_path)
                )
                photo_id = photo_msg.photo[-1].file_id
                await bot.delete_message(message.chat.id, photo_msg.message_id)
            except Exception as e:
                errors.append(f"{folder_name}: Ошибка загрузки фото - {str(e)}")
                continue

            # Загружаем модпак в Telegram
            try:
                doc_msg = await bot.send_document(
                    chat_id=message.chat.id,
                    document=FSInputFile(mod_path)
                )
                file_id = doc_msg.document.file_id
                await bot.delete_message(message.chat.id, doc_msg.message_id)
            except Exception as e:
                errors.append(f"{folder_name}: Ошибка загрузки файла - {str(e)}")
                continue

            # Сохраняем в БД
            try:
                await add_modpack(
                    name=config['name'],
                    description=config['description'],
                    version=config['version'],
                    category=config['category'],
                    photo_id=photo_id,
                    file_id=file_id
                )
                added.append(f"{config['name']} ({folder_name})")
            except Exception as e:
                errors.append(f"{folder_name}: Ошибка базы данных - {str(e)}")

        # Формируем отчет
        report_lines = [f"Обработано папок: {processed}", f"Успешно: {len(added)}", f"Ошибок: {len(errors)}"]

        if added:
            report_lines.append("\nДобавлены:")
            report_lines.extend([f"✅ {name}" for name in added])

        if errors:
            report_lines.append("\nОшибки:")
            report_lines.extend(errors[:5])  # Показываем первые 5 ошибок
            if len(errors) > 5:
                report_lines.append(f"...и еще {len(errors) - 5} ошибок")

        final_report = "\n".join(report_lines)

        # Если отчет слишком длинный, обрезаем
        if len(final_report) > 4000:
            final_report = final_report[:3900] + "\n...текст обрезан"

        await status_msg.edit_text(final_report)

    except zipfile.BadZipFile:
        await status_msg.edit_text("Ошибка: Неверный формат ZIP архива (файл поврежден?)")
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"IMPORT ERROR: {error_details}")  # Вывод в консоль сервера
        await status_msg.edit_text(f"Ошибка: {str(e)}\n\nПодробности в консоли сервера")
    finally:
        # Очистка
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass
        await state.clear()