from typing import Optional


class MemoryStore:
    def __init__(self, keep_last_n_items: int):
        self._store: dict = {}
        self._keep_last_n_items = keep_last_n_items

    async def load(self, session_id: str) -> Optional[list]:
        return self._store.get(session_id)

    async def reset(self, session_id: str) -> None:
        if session_id in self._store:
            del self._store[session_id]

    async def save(
        self, session_id: str, user_msg: Optional[str], assistant_msg: str
    ) -> None:
        msgs = self._store.get(session_id, [])
        if user_msg is not None:
            msgs.append({"role": "user", "content": user_msg})
        msgs.append({"role": "assistant", "content": assistant_msg})

        # cap the history to the last n
        msgs = msgs[-self._keep_last_n_items :]

        self._store[session_id] = msgs


store = MemoryStore(keep_last_n_items=20)
