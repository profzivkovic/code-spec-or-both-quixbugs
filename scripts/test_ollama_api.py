from ollama import chat
from pydantic import BaseModel


MODEL = "qwen2.5-coder:7b"


class TestGeneration(BaseModel):
    code: str


SYSTEM_PROMPT = """
You generate pytest tests.

Return test code only through the requested structured output.

Do not:
- explain the answer;
- use Markdown code fences;
- redefine or reimplement the function under test;
- include the implementation of the function under test.

The function under test will already exist in the evaluation environment.
"""


USER_PROMPT = """
Generate pytest tests for this function:

def add(a, b):
    return a + b

Test normal, negative, and zero values.
Do not redefine add().
"""


response = chat(
    model=MODEL,
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": USER_PROMPT,
        },
    ],
    format=TestGeneration.model_json_schema(),
    options={
        "temperature": 0.7,
        "seed": 101,
        "num_ctx": 8192,
        "num_predict": 2048,
    },
)


result = TestGeneration.model_validate_json(
    response.message.content
)

print("=" * 70)
print("GENERATED CODE")
print("=" * 70)
print(result.code)

print()
print("=" * 70)
print("METRICS")
print("=" * 70)

print(
    "Prompt tokens:",
    response.prompt_eval_count,
)

print(
    "Output tokens:",
    response.eval_count,
)

print(
    "Total duration:",
    response.total_duration,
)