import requests
import os

HUGGINGFACE_TOKEN = os.getenv("HF_TOKEN")

def fix_grammar(text, lang):
    if lang == 'en':
        model_url = "https://api-inference.huggingface.co/models/pszemraj/flan-t5-base-grammar-synthesis"
    elif lang == 'bn':
        return text  # Bangla grammar fix currently unsupported
    else:
        return text

    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_TOKEN}"
    }

    payload = {"inputs": text}

    try:
        response = requests.post(model_url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result[0]['generated_text'] if result else text
    except Exception as e:
        print("Grammar fix error:", e)
        return text
