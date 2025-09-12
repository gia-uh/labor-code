import os


config = {
    "OPENAI_BASE_URL": "http://10.6.125.217:8080/v1",
    "OPENAI_MODEL": "qwen/qwen3-14b",
    **os.environ,
}
