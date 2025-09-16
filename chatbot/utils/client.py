import os
from typing import Any, Callable, Iterator, List, Optional, Type
import openai
from openai.types.chat.chat_completion import ChatCompletion
from pydantic import BaseModel

from utils.history import TalkHistory
from utils.models.intents import IntentOutput
from utils.prompting import BASE_PROMPT, build_intent_classifier_prompt
from config import config


class RequestLog(BaseModel):
    message: Optional[str]
    context: TalkHistory
    failed: bool = False
    response: Optional[object] = None


class WrappedClient(openai.OpenAI):
    # Complete prompt or user message | Context | Did it failed for some reason(validation, etc.)
    requests_history: List[RequestLog] = []

    def __init__(self):
        super().__init__(base_url=config["OPENAI_BASE_URL"], api_key=config["OPENAI_KEY"])

    def __talk_model(
        self,
        messages: TalkHistory,
        prompt: Optional[str] = None,
        *,
        _from_response: Callable[[ChatCompletion], Any] = lambda x: x,
        **_extra_args,
    ) -> Any:
        self.requests_history.append(
            RequestLog(message=prompt, context=messages.model_copy())
        )

        response = self.chat.completions.create(
            model=config["OPENAI_MODEL"],
            messages=messages.msg_history
            + (
                [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ]
                if prompt
                else []
            ),
            temperature=_extra_args.get("temperature", 0.5),
            **{k: v for k, v in _extra_args.items() if k != "temperature"},
        )

        self.requests_history[-1].response = response

        return _from_response(response)

    def __talk_model_formatted(
        self,
        messages: TalkHistory,
        model: Type[BaseModel],
        prompt: Optional[str] = None,
        **kwargs,
    ) -> BaseModel:
        while True:
            self.requests_history.append(
                RequestLog(message=prompt, context=messages.model_copy())
            )

            classification = self.beta.chat.completions.parse(
                messages=messages.msg_history
                + (
                    [
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ]
                    if prompt
                    else []
                ),
                model=config["OPENAI_MODEL"],
                response_format=model,
            )

            self.requests_history[-1].response = classification

            classification = classification.choices[0].message

            if result := classification.parsed:
                return result

            self.requests_history[-1].failed = True

    def query_simple(
        self, messages: TalkHistory, prompt: str, stream: bool = True, **extra_args
    ) -> str | Iterator[str]:
        return self.__talk_model(
            messages.with_system_prompt(BASE_PROMPT),
            prompt,
            _from_response=lambda x: x.choices[0].message.content if not stream else x,
            stream=stream,
            **extra_args,
        )

    def query_classify_intent(self, shots: TalkHistory, prompt: str) -> IntentOutput:
        return self.__talk_model_formatted(
            shots.with_system_prompt(build_intent_classifier_prompt(prompt)),
            IntentOutput,
        )


def load_client():
    client = WrappedClient()

    return client
