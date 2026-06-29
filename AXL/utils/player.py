from pytgcalls.types import MediaStream
from pytgcalls.exceptions import NoActiveGroupCall

from AXL import calls, LOGGER
from AXL.utils.queue_manager import queue_manager
from AXL.database import increment_play_count


async def play_song(chat_id: int, song: dict, is_first: bool = True):
    stream = MediaStream(
        song["file_path"],
        audio_parameters_quality="studio",
    )

    if is_first:
        await calls.play(chat_id, stream)
    else:
        await calls.play(chat_id, stream)

    queue_manager.set_current(chat_id, song)
    queue_manager.set_paused(chat_id, False)
    await increment_play_count(chat_id)
    LOGGER.info(f"Now playing '{song['title']}' in chat {chat_id}")


async def play_next(chat_id: int):
    if queue_manager.is_looping(chat_id):
        current = queue_manager.get_current(chat_id)
        if current:
            await play_song(chat_id, current, is_first=False)
            return

    next_song = queue_manager.pop_next(chat_id)
    if next_song is None:
        queue_manager.clear_current(chat_id)
        try:
            await calls.leave_call(chat_id)
        except Exception:
            pass
        return

    await play_song(chat_id, next_song, is_first=False)


async def stop_playback(chat_id: int):
    queue_manager.cleanup_chat(chat_id)
    try:
        await calls.leave_call(chat_id)
    except NoActiveGroupCall:
        pass
    except Exception as e:
        LOGGER.warning(f"Error leaving call in {chat_id}: {e}")


async def skip_current(chat_id: int):
    await play_next(chat_id)


async def pause_playback(chat_id: int) -> bool:
    try:
        await calls.pause(chat_id)
        queue_manager.set_paused(chat_id, True)
        return True
    except Exception as e:
        LOGGER.warning(f"Error pausing in {chat_id}: {e}")
        return False


async def resume_playback(chat_id: int) -> bool:
    try:
        await calls.resume(chat_id)
        queue_manager.set_paused(chat_id, False)
        return True
    except Exception as e:
        LOGGER.warning(f"Error resuming in {chat_id}: {e}")
        return False
