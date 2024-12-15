import dspy
from gym_reader.api.cache_tools import cache
from gym_reader.logger import get_logger
from tenacity import retry, stop_after_attempt, wait_random_exponential
from instructor import Instructor
import json

log = get_logger(__name__)


def add_tokens_to_cache(request_id: str, prediction_tokens: int):
    token_till_now = cache.get(request_id)
    if token_till_now is None:
        log.debug(
            f"setting token_till_now: {prediction_tokens} for request_id: {request_id}"
        )
        cache.set(request_id, prediction_tokens)
    else:
        log.debug(
            f"updating token_till_now: {token_till_now} for request_id: {request_id}"
        )
        cache.set(request_id, token_till_now + prediction_tokens)


class TypedChainOfThoughtProgramme(dspy.Module):
    def __init__(self, signature):
        super().__init__()
        self.predictor = dspy.TypedChainOfThought(signature)

    def forward(self, model=None, request_id: str = None, **kwargs):
        if model:
            with dspy.context(lm=model):
                prediction = self.predictor(**kwargs)
                try:
                    prediction_tokens = model.history[-1]["response"]["usage"][
                        "total_tokens"
                    ]
                    log.debug(
                        f"prediction_tokens: {prediction_tokens} with request_id: {request_id}"
                    )
                    add_tokens_to_cache(request_id, prediction_tokens)
                except Exception as e:
                    log.error(f"Error adding tokens to cache: {e}", exc_info=True)
            return prediction
        else:
            prediction = self.predictor(**kwargs)
            model = dspy.settings.lm

            try:
                prediction_tokens = model.history[-1]["response"]["usage"][
                    "total_tokens"
                ]
                log.debug(
                    f"prediction_tokens: {prediction_tokens} with request_id: {request_id}"
                )
                add_tokens_to_cache(request_id, prediction_tokens)
            except Exception as e:
                log.error(f"Error adding tokens to cache: {e}", exc_info=True)
            return prediction


class TypedProgramme(dspy.Module):
    def __init__(self, signature):
        super().__init__()
        self.predictor = dspy.Predict(signature)

    def forward(self, model=None, request_id: str = None, **kwargs):
        if model:
            with dspy.context(lm=model):
                prediction = self.predictor(**kwargs)
                try:
                    prediction_tokens = model.history[-1]["response"]["usage"][
                        "total_tokens"
                    ]
                    log.debug(
                        f"prediction_tokens: {prediction_tokens} with request_id: {request_id}"
                    )
                    add_tokens_to_cache(request_id, prediction_tokens)
                except Exception as e:
                    log.error(f"Error adding tokens to cache: {e}", exc_info=True)
                return prediction
        else:
            prediction = self.predictor(**kwargs)
            model = dspy.settings.lm
            try:
                prediction_tokens = model.history[-1]["response"]["usage"][
                    "total_tokens"
                ]
                log.debug(f"prediction_tokens: {prediction_tokens}")
                add_tokens_to_cache(request_id, prediction_tokens)
            except Exception as e:
                log.error(f"Error adding tokens to cache: {e}", exc_info=True)
            return prediction


class InstructorProgramme:
    def __init__(self, client_instructor: Instructor):
        self.client_instructor = client_instructor

    @retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(5))
    def forward(self, model=None, request_id: str = None, **kwargs):
        if model is None:
            model = "gpt-4o"

        try:
            messages = kwargs.get("messages")
            temperature = kwargs.get("temperature", 0.2)
            seed = kwargs.get("seed", 123)
            top_p = kwargs.get("top_p", 1)
            max_tokens = kwargs.get("max_tokens", 4096)
            tools = kwargs.get("tools", None)
            function_call = kwargs.get("function_call", None)
            response_model = kwargs.get("response_model", None)
            user, completion = (
                self.client_instructor.chat.completions.create_with_completion(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    seed=seed,
                    top_p=top_p,
                    max_tokens=max_tokens,
                    tools=tools,
                    function_call=function_call,
                    response_model=response_model,
                )
            )

            log.debug(completion)
            try:
                prediction_tokens = completion.usage.total_tokens
                log.debug(
                    f"prediction_tokens: {prediction_tokens} with request_id: {request_id}"
                )
                add_tokens_to_cache(request_id, prediction_tokens)
            except Exception as e:
                log.error(f"Error adding tokens to cache: {e}", exc_info=True)
            # dump into pydantic model
            response = response_model(
                **json.loads(
                    completion.choices[0].message.tool_calls[0].function.arguments
                )
            )
            return response
        except Exception as e:
            log.exception("Unable to generate ChatCompletion response")
            log.error(f"Exception: {e}")
            return None
