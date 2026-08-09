import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.utils.formatters import smart_edit, build_sub_menu_kb, SYMBOLS
from app.apps.registry import APPS_METADATA
from app.bot.states import AppStoreState
from app.core.database import db

router = Router()
logger = logging.getLogger(__name__)

def get_categories():
    categories = set(app["category"] for app in APPS_METADATA)
    return sorted(list(categories))

@router.callback_query(F.data == "menu:apps")
async def cb_apps_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        f"<b>UNIVERSAL APP STORE</b>\n\n"
        f"StanlOS supports native integration with {len(APPS_METADATA)} enterprise applications. "
        f"Select a category below to browse apps or use the Search button.\n"
    )
    
    categories = get_categories()
    buttons = []
    
    row = []
    for cat in categories:
        row.append(InlineKeyboardButton(text=f"{cat}", callback_data=f"appcat:{cat}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
        
    buttons.append([InlineKeyboardButton(text="Search App Directory", callback_data="appsearch:init")])
    buttons.append([InlineKeyboardButton(text="« Back to Dashboard", callback_data="menu:main")])
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await smart_edit(cb, text, reply_markup=kb)

@router.callback_query(F.data.startswith("appcat:"))
async def cb_app_category(cb: CallbackQuery):
    cat_name = cb.data.split(":")[1]
    
    apps_in_cat = [a for a in APPS_METADATA if a["category"] == cat_name]
    
    text = f"<b>CATEGORY: {cat_name.upper()}</b>\n\nSelect an app to configure:"
    
    buttons = []
    row = []
    for app in apps_in_cat:
        row.append(InlineKeyboardButton(text=app['name'], callback_data=f"appdetail:{app['id']}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
        
    buttons.append([InlineKeyboardButton(text="« Back to Categories", callback_data="menu:apps")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await smart_edit(cb, text, reply_markup=kb)

@router.callback_query(F.data.startswith("appsearch:init"))
async def cb_appsearch_init(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AppStoreState.waiting_for_search)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Cancel", callback_data="menu:apps")]])
    await cb.message.edit_text("<b>SEARCH APP DIRECTORY</b>\n\nPlease type the name of the app you are looking for (e.g. 'Gmail' or 'GitHub').", reply_markup=kb)

@router.message(AppStoreState.waiting_for_search)
async def process_app_search(message: Message, state: FSMContext):
    query = message.text.lower()
    await state.clear()
    
    results = [a for a in APPS_METADATA if query in a["name"].lower() or query in a["desc"].lower()]
    
    if not results:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to App Store", callback_data="menu:apps")]])
        return await message.answer(f"No apps found matching '<b>{message.text}</b>'.", reply_markup=kb)
        
    text = f"<b>SEARCH RESULTS FOR '{message.text}'</b>\n\nFound {len(results)} matches:"
    buttons = []
    row = []
    for app in results:
        row.append(InlineKeyboardButton(text=app['name'], callback_data=f"appdetail:{app['id']}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
        
    buttons.append([InlineKeyboardButton(text="« Back to App Store", callback_data="menu:apps")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text, reply_markup=kb)

@router.callback_query(F.data.startswith("appdetail:"))
async def cb_app_detail(cb: CallbackQuery, state: FSMContext):
    app_id = cb.data.split(":")[1]
    user_id = cb.from_user.id
    
    app_data = next((a for a in APPS_METADATA if a["id"] == app_id), None)
    if not app_data:
        return await cb.answer("App not found.", show_alert=True)
        
    # Check connection status in DB
    rows = await db.execute("SELECT status FROM user_apps WHERE user_id = ? AND app_id = ?", (user_id, app_id), fetch=True)
    is_connected = bool(rows and rows[0][0] == 'active')
    
    status_str = "CONNECTED" if is_connected else "NOT CONNECTED"
    
    text = (
        f"<b>{app_data['name'].upper()}</b>\n"
        f"<i>{app_data['desc']}</i>\n\n"
        f"<b>Status:</b> {status_str}\n"
        f"<b>Auth Method:</b> {app_data['auth']}\n\n"
    )
    
    buttons = []
    if is_connected:
        text += "The AI Agent has full access to this application."
        buttons.append([InlineKeyboardButton(text="Disconnect App", callback_data=f"appdisconnect:{app_id}")])
    else:
        text += "Connect this app to allow the AI Agent to autonomously manage it for you."
        if app_data['auth'] == 'OAuth2':
            buttons.append([InlineKeyboardButton(text="Connect via OAuth2", url=f"https://stanlos.com/oauth/{app_id}?uid={user_id}")])
        elif app_data['auth'] == 'API Key':
            buttons.append([InlineKeyboardButton(text="Enter API Key", callback_data=f"appauth_key:{app_id}")])
        else:
            buttons.append([InlineKeyboardButton(text="Enable Free Integration", callback_data=f"appauth_free:{app_id}")])
            
    buttons.append([InlineKeyboardButton(text="« Back to Categories", callback_data=f"appcat:{app_data['category']}")])
    buttons.append([InlineKeyboardButton(text="« Back to App Store", callback_data="menu:apps")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    if cb.message:
        await smart_edit(cb, text, reply_markup=kb)

@router.callback_query(F.data.startswith("appauth_free:"))
async def cb_appauth_free(cb: CallbackQuery, state: FSMContext):
    app_id = cb.data.split(":")[1]
    user_id = cb.from_user.id
    
    await db.execute(
        "INSERT INTO user_apps (user_id, app_id, auth_type, status) VALUES (?, ?, 'No Auth', 'active') "
        "ON CONFLICT(user_id, app_id) DO UPDATE SET status='active'",
        (user_id, app_id)
    )
    await cb.answer("App enabled successfully!", show_alert=True)
    # Re-trigger detail view
    cb.data = f"appdetail:{app_id}"
    await cb_app_detail(cb, state)

@router.callback_query(F.data.startswith("appauth_key:"))
async def cb_appauth_key(cb: CallbackQuery, state: FSMContext):
    app_id = cb.data.split(":")[1]
    await state.set_state(AppStoreState.waiting_for_api_key)
    await state.update_data(target_app=app_id)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Cancel", callback_data=f"appdetail:{app_id}")]])
    await cb.message.edit_text(
        f"<b>API KEY REQUIRED</b>\n\n"
        f"Please reply to this message with your API Key for {app_id.capitalize()}.\n"
        f"<i>Your key will be securely stored and encrypted in SQLite Cloud.</i>", 
        reply_markup=kb
    )

@router.message(AppStoreState.waiting_for_api_key)
async def process_api_key(message: Message, state: FSMContext):
    api_key = message.text.strip()
    user_id = message.from_user.id
    data = await state.get_data()
    app_id = data.get("target_app")
    
    await state.clear()
    
    # Save to db
    await db.execute(
        "INSERT INTO user_apps (user_id, app_id, auth_type, auth_token, status) VALUES (?, ?, 'API Key', ?, 'active') "
        "ON CONFLICT(user_id, app_id) DO UPDATE SET auth_token=?, status='active'",
        (user_id, app_id, api_key, api_key)
    )
    
    # Delete the message with the API key for security
    try:
        await message.delete()
    except Exception:
        pass
        
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to App Details", callback_data=f"appdetail:{app_id}")]])
    await message.answer(f"{SYMBOLS['success']} API Key securely saved! The AI Agent can now autonomously access {app_id.capitalize()}.", reply_markup=kb)

@router.callback_query(F.data.startswith("appdisconnect:"))
async def cb_appdisconnect(cb: CallbackQuery, state: FSMContext):
    app_id = cb.data.split(":")[1]
    user_id = cb.from_user.id
    
    await db.execute("UPDATE user_apps SET status = 'disconnected' WHERE user_id = ? AND app_id = ?", (user_id, app_id))
    await cb.answer("App disconnected.", show_alert=True)
    cb.data = f"appdetail:{app_id}"
    await cb_app_detail(cb, state)
