import logging
import os

from flask import Flask, request, jsonify
from transformers import AutoModel, AutoTokenizer
import torch

app = Flask(__name__)

MODEL_PATH = os.environ.get('GLM4_MODEL_PATH', os.path.join(os.path.dirname(__file__), 'glm-4-9b-chat'))
MAX_NEW_TOKENS = int(os.environ.get('GLM4_MAX_NEW_TOKENS', 512))

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
dtype = torch.float16 if device.type == 'cuda' else torch.float32

tokenizer = None
model = None
model_load_error = None


def load_model():
    global tokenizer, model, model_load_error
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
        model = AutoModel.from_pretrained(MODEL_PATH, trust_remote_code=True)
        if device.type == 'cuda':
            model = model.half()
        else:
            model = model.to(dtype=dtype)
        model = model.to(device)
        model = model.eval()
        logging.info("GLM4 模型加载完成，设备：%s", device)
        model_load_error = None
    except Exception as exc:  # pylint: disable=broad-except
        tokenizer = None
        model = None
        model_load_error = str(exc)
        logging.error("加载 GLM4 模型失败：%s", exc)


load_model()


@app.route('/chat/completions', methods=['POST'])
def chat_completions():
    if model is None or tokenizer is None:
        return jsonify({
            "error": "GLM4 模型尚未准备好，请先下载/解压模型到 llm_models/glm-4-9b-chat 或设置 GLM4_MODEL_PATH 环境变量。",
            "details": model_load_error
        }), 503

    data = request.json or {}
    messages = data.get('messages', [])

    user_input = next((msg['content'] for msg in messages if msg.get('role') == 'user'), None)
    if not user_input:
        return jsonify({"error": "No user message provided"}), 400

    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_tensors="pt",
        return_dict=True
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=True,
            top_p=0.8,
            temperature=0.8,
            repetition_penalty=1.2,
            eos_token_id=model.config.eos_token_id,
        )

    response = tokenizer.decode(
        outputs[0][len(inputs['input_ids'][0]):],
        skip_special_tokens=True
    ).strip()

    return jsonify({
        "choices": [{
            "message": {"role": "assistant", "content": response or "（空响应）"}
        }]
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
