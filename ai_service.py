import os
from typing import Dict, Any

from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_caption(prompt_skill: Dict[str, Any], product_description: str, price: str, language: str = 'en') -> str:
    config = prompt_skill.get('config', {})
    system_prompt = config.get('system_prompt', (
        'You are a marketing copywriter for Nigerian small businesses. '
        'Write a short promotional caption with price, benefits, and a clear CTA.'
    ))
    system_prompt += (
        '\n\nNever use a real, existing brand name, trademark, or slogan '
        'that is not the seller\'s own. Write original copy — do not '
        'reproduce or closely paraphrase any specific ad or campaign line '
        'you may recall.'
    )

    vocab = prompt_skill.get('vocabulary', {})
    constraints = prompt_skill.get('constraints', {})
    examples = prompt_skill.get('examples', [])

    # Build few-shot examples block
    examples_block = ""
    if examples:
        examples_block = "\n## Examples\n"
        for ex in examples[:5]:
            examples_block += f"Input: {ex.get('input', '')}\nOutput: {ex.get('output', '')}\n\n"

    vocab_block = ""
    if vocab:
        vocab_block = "\n## Vocabulary\n"
        for category, words in vocab.items():
            vocab_block += f"{category}: {', '.join(words)}\n"

    constraints_block = ""
    if constraints:
        forbidden = constraints.get('forbidden', [])
        if forbidden:
            constraints_block = "\n## Forbidden\n" + "\n".join(f"- {f}" for f in forbidden)
        rules = constraints.get('rules', [])
        if rules:
            constraints_block += "\n## Rules\n" + "\n".join(f"- {r}" for r in rules)

    messages = [
        {'role': 'system', 'content': system_prompt + examples_block + vocab_block + constraints_block},
        {
            'role': 'user',
            'content': (
                f'Generate a flyer caption for this product:\n'
                f'Product description: {product_description}\n'
                f'Price: {price}\n'
                f'Language: {language}\n'
                'Output should be 1-3 short sentences suitable for a WhatsApp product flyer. Do not use quotation marks around the output.'
            ),
        },
    ]

    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            max_tokens=120,
            temperature=0.85,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        # Fallback caption if OpenAI fails
        return f"{product_description}. Price: {price}. DM to order now!"
