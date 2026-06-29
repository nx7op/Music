from AXL.config import Config


class QueueManager:
    def __init__(self):
        self.queues = {}
        self.current_playing = {}
        self.loop_mode = {}
        self.is_paused = {}

    def add_to_queue(self, chat_id: int, song: dict) -> int:
        if chat_id not in self.queues:
            self.queues[chat_id] = []

        if len(self.queues[chat_id]) >= Config.MAX_QUEUE_SIZE:
            raise OverflowError("Queue is full")

        self.queues[chat_id].append(song)
        return len(self.queues[chat_id])

    def get_queue(self, chat_id: int) -> list:
        return self.queues.get(chat_id, [])

    def pop_next(self, chat_id: int):
        queue = self.queues.get(chat_id, [])
        if not queue:
            return None
        return queue.pop(0)

    def peek_next(self, chat_id: int):
        queue = self.queues.get(chat_id, [])
        if not queue:
            return None
        return queue[0]

    def clear_queue(self, chat_id: int):
        self.queues[chat_id] = []

    def remove_at_index(self, chat_id: int, index: int) -> bool:
        queue = self.queues.get(chat_id, [])
        if 0 < index <= len(queue):
            queue.pop(index - 1)
            return True
        return False

    def set_current(self, chat_id: int, song: dict):
        self.current_playing[chat_id] = song

    def get_current(self, chat_id: int):
        return self.current_playing.get(chat_id)

    def clear_current(self, chat_id: int):
        self.current_playing.pop(chat_id, None)

    def set_loop(self, chat_id: int, value: bool):
        self.loop_mode[chat_id] = value

    def is_looping(self, chat_id: int) -> bool:
        return self.loop_mode.get(chat_id, False)

    def set_paused(self, chat_id: int, value: bool):
        self.is_paused[chat_id] = value

    def get_paused(self, chat_id: int) -> bool:
        return self.is_paused.get(chat_id, False)

    def shuffle_queue(self, chat_id: int):
        import random
        queue = self.queues.get(chat_id, [])
        random.shuffle(queue)

    def queue_length(self, chat_id: int) -> int:
        return len(self.queues.get(chat_id, []))

    def cleanup_chat(self, chat_id: int):
        self.queues.pop(chat_id, None)
        self.current_playing.pop(chat_id, None)
        self.loop_mode.pop(chat_id, None)
        self.is_paused.pop(chat_id, None)


queue_manager = QueueManager()
