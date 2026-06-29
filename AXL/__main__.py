import asyncio

from pytgcalls import filters as call_filters
from pytgcalls.types import Update

from AXL import app, assistant, calls, LOGGER
from AXL.utils.player import play_next

from AXL.modules import play, controls, auth, start  # noqa: F401


@calls.on_update(call_filters.stream_end)
async def on_stream_end(_, update: Update):
    chat_id = update.chat_id
    LOGGER.info(f"Stream ended in chat {chat_id}, advancing queue...")
    try:
        await play_next(chat_id)
    except Exception as e:
        LOGGER.error(f"Error advancing queue in {chat_id}: {e}")


async def main():
    LOGGER.info("Starting AXL Music Bot...")

    await app.start()
    LOGGER.info("✅ Bot client started")

    await assistant.start()
    LOGGER.info("✅ Assistant client started")

    await calls.start()
    LOGGER.info("✅ PyTgCalls started")

    me = await app.get_me()
    LOGGER.info(f"🎵 AXL MUSIC BOT is now online as @{me.username}")

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
