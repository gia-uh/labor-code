from typing import List, Self, Tuple
from pydantic import BaseModel


class Message(BaseModel):
    role: str
    content: str


class TalkHistory(BaseModel):
    msg_history: List[Message] = []

    @staticmethod
    def empty():
        return TalkHistory(msg_history=[])

    def word_count(self) -> int:
        return sum(
            (1 for message in self.msg_history for word in message.content.split(" "))
        )

    def with_system_prompt(self, prompt: str) -> Self:
        return TalkHistory(
            msg_history=[Message(role="system", content=prompt)] + self.msg_history
        )

    def with_shot(self, prompt: str, answer: str) -> Self:
        return TalkHistory(
            msg_history=self.msg_history
            + [
                Message(role="user", content=prompt),
                Message(role="assistant", content=answer),
            ]
        )

    def detached_message(self) -> Tuple[Self, Message]:
        return TalkHistory(msg_history=self.msg_history[:-1]), self.msg_history[-1]
