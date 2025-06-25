import requests
import os

HUGGINGFACE_TOKEN = os.getenv("HF_TOKEN")

def fix_grammar(text, lang):
    if lang == 'bn':
        model_url = "https://api-inference.huggingface.co/models/csebuetnlp/banglat5"
    elif lang == 'en':
        model_url = "https://api-inference.huggingface.co/models/vennify/t5-base-grammar-correction"
    else:
        return text  # unsupported language

    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_TOKEN}"
    }
    payload = {"inputs": text}

    try:
        response = requests.post(model_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()[0]['generated_text']
    except Exception as e:
        print("Grammar fix error:", e)
        return text
