from aiogram.fsm.state import StatesGroup, State

class AppStoreState(StatesGroup):
    waiting_for_search = State()
    waiting_for_api_key = State()
