import responses

from src.llm import complete


@responses.activate
def test_complete_posts_openai_shape_and_returns_content():
    responses.post(
        "https://llm.example.com/v1/chat/completions",
        json={"choices": [{"message": {"content": "hello back"}}]},
        status=200,
    )

    out = complete(
        "you are terse",
        "say hi",
        model="test-model",
        base_url="https://llm.example.com/v1",
        api_key="secret",
    )

    assert out == "hello back"
    req = responses.calls[0].request
    assert req.headers["Authorization"] == "Bearer secret"
    import json

    body = json.loads(req.body)
    assert body["model"] == "test-model"
    assert body["messages"] == [
        {"role": "system", "content": "you are terse"},
        {"role": "user", "content": "say hi"},
    ]


@responses.activate
def test_complete_raises_on_non_200():
    responses.post(
        "https://llm.example.com/v1/chat/completions",
        json={"error": "nope"},
        status=500,
    )

    import pytest

    with pytest.raises(RuntimeError, match="500"):
        complete(
            "s",
            "u",
            model="m",
            base_url="https://llm.example.com/v1",
            api_key="k",
        )
