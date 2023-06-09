import json
import urllib

from flask import Flask, request, Response, stream_with_context, render_template
from flask_cors import CORS
import openai
import time

app = Flask(__name__)
CORS(app)
app.config["response_buffer_size"] = 100 * 1024 * 1024  # 增加缓冲区大小





@app.route("/")
def index():
    return render_template("index.html")


def generate_chat_response_stream(messages):

    messages = json.loads(messages)

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=messages,
        temperature=0,
        stream=True
    )

    for chunk in response:
        # print(chunk)
        # print("=======")
        choice = chunk['choices'][0]
        if "delta" in choice:
            delta = choice["delta"]
            created = chunk["created"]

            if choice["finish_reason"] == "stop":
                # 如果聊天结束了，直接退出
                return
            else:
                if "content" in delta:
                    content = delta["content"]
                    yield "data: {}\n\n".format(json.dumps({"text": content}))


@app.route("/chat_stream")
def chat_stream():
    message = request.args.get("message")
    api_key = request.args.get("api_key")

    api_key = api_key.replace("Bearer ", "")

    # 设置你的 OpenAI API 密钥
    openai.api_key = api_key
    print("key:"+api_key)

    response_stream = generate_chat_response_stream(message)
    return Response(stream_with_context(response_stream), content_type="text/event-stream")


if __name__ == "__main__":
    app.run(debug=False)
