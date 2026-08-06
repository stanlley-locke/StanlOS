import asyncio
import os
from pyrogram import Client
from dotenv import load_dotenv

load_dotenv()

async def main():
    api_id = os.environ.get("API_ID")
    api_hash = os.environ.get("API_HASH")
    phone_number = os.environ.get("PHONE_NUMBER")

    if not api_id or not api_hash or not phone_number:
        print("[!] ERROR: Please set API_ID, API_HASH, and PHONE_NUMBER in your .env file.")
        print("You can get these from https://my.telegram.org")
        return

    print("Starting Pyrogram authentication...")
    
    # This will prompt for the login code in the terminal
    app = Client(
        "my_account",
        api_id=int(api_id),
        api_hash=api_hash,
        phone_number=phone_number
    )
    
    await app.start()
    
    print("\n[OK] Authentication successful!")
    print("[OK] A 'my_account.session' file has been created in your directory.")
    print("[OK] StanlOS can now control your personal account as a Userbot.")
    
    me = await app.get_me()
    print(f"Logged in as: {me.first_name} (@{me.username})")
    
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
