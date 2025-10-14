import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from app.core.config import get_settings


settings = get_settings()


class ChatStorage:
    def __init__(self, storage_dir: Path | str | None = None):
        """Initialize the chat storage directory."""
        base_dir = Path(storage_dir or settings.chat_storage_dir)
        self.storage_dir = base_dir.resolve()
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        print(f"Chat storage directory initialized at: {self.storage_dir}")

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Persist a message for the specified session."""
        file_path = self.storage_dir / f"{session_id}.json"

        if file_path.exists():
            with file_path.open("r", encoding="utf-8") as file_obj:
                data = json.load(file_obj)
        else:
            data = {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "messages": [],
            }

        data["messages"].append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
            }
        )

        data["last_activity"] = datetime.now().isoformat()

        with file_path.open("w", encoding="utf-8") as file_obj:
            json.dump(data, file_obj, ensure_ascii=False, indent=2)

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Return the full session payload, if it exists."""
        file_path = self.storage_dir / f"{session_id}.json"

        if file_path.exists():
            with file_path.open("r", encoding="utf-8") as file_obj:
                return json.load(file_obj)
        return None

    def get_all_sessions(self) -> List[Dict]:
        """Return summaries of all stored sessions."""
        sessions: List[Dict] = []

        for file_path in self.storage_dir.glob("*.json"):
            try:
                with file_path.open("r", encoding="utf-8") as file_obj:
                    data = json.load(file_obj)
                    summary = {
                        "session_id": data.get("session_id"),
                        "created_at": data.get("created_at"),
                        "last_activity": data.get("last_activity"),
                        "message_count": len(data.get("messages", [])),
                        "first_message": (
                            data.get("messages", [{}])[0].get("content", "")[:100]
                            if data.get("messages")
                            else ""
                        ),
                    }
                    sessions.append(summary)
            except Exception as exc:
                print(f"Error reading {file_path}: {exc}")

        sessions.sort(key=lambda item: item.get("last_activity", ""), reverse=True)
        return sessions

    def delete_session(self, session_id: str) -> bool:
        """Delete the session file and return whether it existed."""
        file_path = self.storage_dir / f"{session_id}.json"

        if file_path.exists():
            file_path.unlink()
            return True
        return False


chat_storage = ChatStorage()
