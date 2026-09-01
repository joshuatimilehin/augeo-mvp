import hashlib
import hmac
import json
import os
import re
import requests
import threading
import time
import uuid
from pathlib import Path
from datetime import datetime

from flask import Flask, Response, request, jsonify, send_file
# Twilio removed: outgoing messages are logged or handled by external webhook
from PIL import Image, ImageDraw, ImageFont

from alerts import run_all_checks
from config import (
    BASE_URL,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_NUMBER,
    PAYSTACK_SECRET_KEY,
    CREDIT_PACKS,
    FLYER_CREDIT_COST,
    BRAND_MEMORY_THRESHOLD,
    FLASK_DEBUG,
    USE_GENERATIVE_LAYOUT,
    AUGEO_PERSONA,
    DISPLAY_PRICING_IN_CHAT,
)
from database import initialize_db, get_customer, get_or_create_customer, get_customer_by_phone, update_customer, add_credits, deduct_credit, get_credit_balance, add_flyer, log_conversation, get_flyer_count_for_customer, get_customers_for_retention, save_brand_memory, get_brand_memory, get_customer_by_referral_code, get_stats, get_connection, save_layout, get_recent_layouts
from skill_registry import SkillRegistry
from ai_service import generate_caption
from flyer_generator import FlyerGenerator
from layout_engine import generate_layout
from originality import check_originality
from safety import detect_distress, guardrail_response
from creative.context import CustomerContext
from creative.generation.orchestrator import CreativeOrchestrator
from creative.brand.manager import BrandManager
import database as database_module
from social_agent import CAPABILITIES, SocialAgent

app = Flask(__name__)
skill_registry = SkillRegistry()
social_agent = SocialAgent()
brand_manager = BrandManager(database_module)
initialize_db()

# ===================== UTILITIES =====================

def parse_incoming_message(body: str) -> dict:
    text = body.strip().lower()
    choice = 'message'
    if re.search(r'(^|\s)(order|flyer|design|package|buy|start)(\s|$)', text):
        choice = 'order'
    elif re.search(r'(^|\s)(help|info|pricing|how|price)(\s|$)', text):
        choice = 'help'
    elif re.search(r'(^|\s)(feedback|rate|review|grade|score)(\s|$)', text):
        choice = 'feedback'
    elif re.search(r'(^|\s)(paid|payment|done|completed|confirm)(\s|$)', text):
        choice = 'payment_confirm'
    elif re.search(r'(^|\s)(balance|credits|how many|left)(\s|$)', text):
        choice = 'balance'
    elif re.search(r'(^|\s)(refer|referral|invite|friend)(\s|$)', text):
        choice = 'referral'
    elif re.search(r'(^|\s)(stop|unsubscribe|pause)(\s|$)', text):
        choice = 'stop'
    elif re.search(r'(^|\s)(privacy|data)(\s|$)', text):
        choice = 'privacy'
    elif re.search(r'(^|\s)(terms|refund|policy)(\s|$)', text):
        choice = 'terms'
    elif re.search(r'(^|\s)(yes|yeah|sure|ok|okay)(\s|$)', text):
        choice = 'yes'
    elif re.search(r'(^|\s)(no|nope|nah)(\s|$)', text):
        choice = 'no'
    return {'intent': choice, 'text': body.strip()}


def save_flyer_bytes(flyer_bytes: bytes, prefix: str, suffix: str = '.jpg') -> str:
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    filename = f'{prefix}_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}{suffix}'
    path = output_dir / filename
    with open(path, 'wb') as fh:
        fh.write(flyer_bytes)
    return str(path)


def send_whatsapp_message(to_number: str, message: str, media_url: str | None = None) -> None:
    # Prefer Kaspo messaging if configured; otherwise log.
    try:
        from ai_clients.kaspo_client import send_message as kaspo_send_message
    except Exception:
        kaspo_send_message = None

    if kaspo_send_message:
        ok = kaspo_send_message(to_number, message, media_url=media_url)
        if ok:
            print(f"[kaspo] message sent to {to_number}")
            return

    # Fallback: log the outgoing message and media link
    try:
        print(f"[OUTGOING MESSAGE] to={to_number} msg={message} media={media_url}")
    except Exception as e:
        print(f"Message log error: {e}")


def extract_reference(text: str) -> str:
    match = re.search(r'\b([A-Za-z0-9]{8,24})\b', text)
    return match.group(1).strip() if match else ''


def safe_json_loads(data_str: str, default: dict = None) -> dict:
    if default is None:
        default = {}
    if not data_str:
        return default
    try:
        return json.loads(data_str)
    except Exception:
        return default

# ===================== CONVERSATION PERSONALITY =====================

def build_conversation_intro() -> str:
    return (
        "Hey — I’ve got this. We’ve reached the point where I can shape the idea into something that feels right for the audience.\n\n"
        "Send the product, reference, or concept and keep it simple: the goal, the audience, and any key notes you want me to lean into.\n\n"
        "Whether you’re a creator, freelancer, or running a business, I’ll give you the context and creative direction that fits."
    )


def build_order_prompt() -> str:
    return (
        "Perfect — we’ve reached the point where the creative can do the selling or the storytelling.\n\n"
        "Send the product, reference, or idea, and tell me the goal, the audience, and any notes you want highlighted.\n\n"
        "I’ll build it around the context you have now, and if you’re a business I’ll factor that in too."
    )


def get_pack_selection_message() -> str:
    pack_lines = [
        f"1. {CREDIT_PACKS['starter']['label']}",
        f"2. {CREDIT_PACKS['growth']['label']}",
        f"3. {CREDIT_PACKS['pro']['label']}",
    ]

    if DISPLAY_PRICING_IN_CHAT:
        pack_lines = [
            f"1. {CREDIT_PACKS['starter']['label']} — ₦{CREDIT_PACKS['starter']['price_ngn']:,}",
            f"2. {CREDIT_PACKS['growth']['label']} — ₦{CREDIT_PACKS['growth']['price_ngn']:,}",
            f"3. {CREDIT_PACKS['pro']['label']} — ₦{CREDIT_PACKS['pro']['price_ngn']:,}",
        ]

    return (
        "If you want to take it final, choose a pack when you’re ready:\n"
        + "\n".join(pack_lines)
        + "\n\nReply 1, 2, or 3 to continue."
    )


# ===================== LOCAL PAYMENT TEST =====================

@app.route('/test/payment-success', methods=['POST'])
def test_payment_success():
    """
    Development-only payment simulator.

    This bypasses Paystack verification but uses the same
    credit-accounting path as a real successful payment.

    NEVER enable this endpoint in production.
    """

    if os.getenv("AUGEO_ENABLE_TEST_PAYMENTS", "").lower() != "true":
        return jsonify({
            "status": "error",
            "message": "Test payment endpoint disabled."
        }), 403

    phone = request.form.get("phone")
    pack_name = request.form.get("pack", "starter")

    if not phone:
        return jsonify({
            "status": "error",
            "message": "phone is required"
        }), 400

    pack = CREDIT_PACKS.get(pack_name)

    if not pack:
        return jsonify({
            "status": "error",
            "message": f"Unknown pack: {pack_name}"
        }), 400

    reference = f"TEST-{uuid.uuid4().hex[:12].upper()}"

    add_credits(
        phone,
        pack["credits"],
        pack_name=pack_name,
        paystack_reference=reference,
        txn_type="purchase",
    )

    update_customer(
        phone,
        lifetime_value_ngn=pack["price_ngn"],
    )

    return jsonify({
        "status": "ok",
        "test_payment": True,
        "phone": phone,
        "pack": pack_name,
        "credits_added": pack["credits"],
        "amount_ngn": pack["price_ngn"],
        "reference": reference,
    }), 200

# ===================== PAYMENT =====================

def create_paystack_payment_link(reference: str, email: str, amount_kobo: int, metadata: dict = None) -> str:
    if not PAYSTACK_SECRET_KEY:
        return f"https://paystack.com/pay/demo-{reference}"
    url = 'https://api.paystack.co/transaction/initialize'
    headers = {
        'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        'email': email,
        'amount': amount_kobo,
        'reference': reference,
        'currency': 'NGN',
        'callback_url': f'{BASE_URL}/payment/callback',
        'metadata': metadata or {'order_reference': reference, 'service': 'Augeo Flyer'},
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['data']['authorization_url']
    except Exception as e:
        print(f"Paystack error: {e}")
        return f"https://paystack.com/pay/demo-{reference}"


def verify_paystack_transaction(reference: str) -> bool:
    if not PAYSTACK_SECRET_KEY or not reference:
        return False
    url = f'https://api.paystack.co/transaction/verify/{reference}'
    headers = {'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('status') and data.get('data', {}).get('status') == 'success'
    except Exception:
        return False


def verify_paystack_signature(payload: bytes, signature: str) -> bool:
    if not signature or not PAYSTACK_SECRET_KEY:
        return False
    computed = hmac.new(PAYSTACK_SECRET_KEY.encode('utf-8'), payload, hashlib.sha512).hexdigest()
    return hmac.compare_digest(computed, signature)


# ===================== FLYER BUILDING =====================
def build_flyer_for_order(
    details: dict,
    graphic_skill_name: str,
    prompt_skill_name: str,
    category_skill_name: str,
    watermark: bool = False,
    customer_phone: str = None,
) -> tuple[bytes, str]:

    product_description = ' '.join(filter(None, [
        details.get('brand_name'),
        details.get('description'),
        details.get('niche'),
    ]))

    price_text = details.get('price', '₦0')

    # -------------------------------------------------
    # CUSTOMER CONTEXT
    # -------------------------------------------------

    customer_context = CustomerContext.from_order(
        details=details,
        graphic_skill_name=graphic_skill_name,
        prompt_skill_name=prompt_skill_name,
        category_skill_name=category_skill_name,
        product_description=product_description,
        price_text=price_text,
    )

    print("[creative] CustomerContext:")
    print(customer_context)

    # -------------------------------------------------
    # CREATIVE INTELLIGENCE
    # -------------------------------------------------

    creative_orchestrator = CreativeOrchestrator()

    creative_result = creative_orchestrator.generate(
        customer_context
    )

    print("[creative] Prompt Intelligence:")
    print(f"Prompt ID: {creative_result['prompt_id']}")
    print(f"Prompt name: {creative_result['prompt_name']}")
    print(f"Prompt score: {creative_result['prompt_score']}")
    print(f"Final prompt:\n{creative_result['final_prompt']}")

    # -------------------------------------------------
    # SKILLS
    # -------------------------------------------------

    graphic_skill = (
        skill_registry.get_graphic_skill(graphic_skill_name)
        or skill_registry.get_graphic_skill('skill-luxury')
    )

    prompt_skill = (
        skill_registry.get_prompt_skill(prompt_skill_name)
        or skill_registry.get_prompt_skill('skill-english-market')
    )

    # -------------------------------------------------
    # USE CREATIVE INTELLIGENCE IMAGE
    # -------------------------------------------------

    image = creative_result.get("image")

    if image is None:
        image = Image.new(
            'RGB',
            (1080, 1080),
            '#FFFFFF',
        )

    # -------------------------------------------------
    # OPTIONAL REFERENCE IMAGE
    # -------------------------------------------------

    image_url = details.get('reference_image')

    if image_url:
        try:
            response = requests.get(
                image_url,
                stream=True,
                timeout=10,
            )
            response.raise_for_status()

            reference_image = Image.open(
                response.raw
            ).convert('RGB')

            image = reference_image

        except Exception as e:
            print(
                f"[creative] Could not load reference image: {e}"
            )

    # -------------------------------------------------
    # CAPTION
    # -------------------------------------------------

    # If the order includes a user-provided caption (e.g., quote or custom text), prefer it.
    custom_caption = details.get('caption') or details.get('custom_caption') or None

    caption = generate_caption(
        prompt_skill,
        product_description,
        price_text,
        voice_instructions=customer_context.brand_voice,
        locale=customer_context.location or customer_context.locale,
        channel=customer_context.language or customer_context.visual_style,
        custom_caption=custom_caption,
    )

    # -------------------------------------------------
    # FLYER GENERATION
    # -------------------------------------------------

    flyer = FlyerGenerator(graphic_skill)

    if USE_GENERATIVE_LAYOUT and graphic_skill:

        brand_memory = (
            get_brand_memory(customer_phone)
            if customer_phone
            else None
        )

        previous_layouts = (
            get_recent_layouts(customer_phone)
            if customer_phone
            else None
        )

        layout = generate_layout(
            product_description=(
                product_description
                or 'Product for sale'
            ),
            price=price_text,
            graphic_skill=graphic_skill,
            brand_memory=brand_memory,
            previous_layouts=previous_layouts,
        )

        flyer_bytes = flyer.create_flyer_from_layout(
            image,
            caption,
            price_text,
            layout,
            watermark=watermark,
        )

    else:

        layout = None

        flyer_bytes = flyer.create_flyer(
            image,
            caption,
            price_text,
            watermark=watermark,
        )

    # -------------------------------------------------
    # ORIGINALITY + LAYOUT LEARNING
    # -------------------------------------------------

    if customer_phone:
        try:
            flyer_hash, flag = check_originality(
                customer_phone,
                flyer_bytes,
            )

            if flag:
                print(
                    f"[originality] Flyer for {customer_phone} "
                    f"is similar to a flyer from "
                    f"{flag['matched_customer']} "
                    f"(distance={flag['hamming_distance']}). "
                    f"Logged for review."
                )

            save_layout(
                customer_phone,
                layout or {},
                image_hash=flyer_hash,
            )

        except Exception as e:
            print(
                "Could not run originality check / "
                f"save layout history: {e}"
            )

    return flyer_bytes, caption
# ===================== RETENTION MESSAGES =====================

def get_low_credits_message(balance: int, graphic_skill: str = None, prompt_skill: str = None) -> str:
    style_text = ""
    if graphic_skill:
        style_map = {
            'skill-luxury': '✨ Luxury',
            'skill-bold': '🔥 Bold',
            'skill-urgency': '⚡ Urgency',
            'skill-festive': '🎉 Festive',
            'skill-minimal': '📋 Minimal',
        }
        style_text = f" Your saved style is {style_map.get(graphic_skill, graphic_skill)}."

    if balance == 2:
        return (
            f"\n\n⚠️ You have {balance} flyers left.{style_text} "
            f"Want me to make your next one? Just send a photo."
        )
    elif balance == 1:
        return (
            f"\n\n🔴 You have {balance} flyer left!{style_text} "
            f"Don't let it waste — send a photo now."
        )
    return ""


def get_brand_memory_message(phone: str, flyer_count: int) -> str:
    if flyer_count == BRAND_MEMORY_THRESHOLD:
        bm = get_brand_memory(phone)
        if not bm:
            return (
                "\n\n🧠 I notice you have been creating flyers with me. "
                "Should I save your preferred style for next time? Reply YES to save your brand look."
            )
    return ""


def get_referral_message(customer: dict) -> str:
    code = customer.get('referral_code', '')
    return (
        f"\n\n💰 Love Augeo? Share my number with a seller friend. "
        f"When they buy their first pack, you both get 2 free flyers! "
        f"Your referral code: {code}"
    )


# ===================== WEBHOOKS =====================

@app.route('/payment/callback', methods=['POST'])
def paystack_webhook():
    signature = request.headers.get('X-Paystack-Signature', '')
    payload = request.data
    if not verify_paystack_signature(payload, signature):
        return jsonify({'status': 'error', 'message': 'invalid signature'}), 403

    event = request.get_json(silent=True) or {}
    if event.get('event') != 'charge.success':
        return jsonify({'status': 'ignored'}), 200

    data = event.get('data', {})
    reference = data.get('reference')
    metadata = data.get('metadata', {})

    # Check if this is a credit pack purchase
    pack_name = metadata.get('pack_name')
    customer_phone = metadata.get('customer_phone')

    if pack_name and customer_phone:
        pack = CREDIT_PACKS.get(pack_name)
        if pack:
            add_credits(customer_phone, pack['credits'], pack_name=pack_name, 
                       paystack_reference=reference, txn_type='purchase')
            update_customer(customer_phone, lifetime_value_ngn=pack['price_ngn'])
            send_whatsapp_message(
                customer_phone,
                f"Payment confirmed! 🎉 You now have {pack['credits']} flyer credits. "
                f"Send a product photo to create your first flyer."
            )
            return jsonify({'status': 'ok'}), 200

    # Unrecognized payment reference — nothing to reconcile against
    print(f"Paystack webhook: unmatched reference {reference}, metadata={metadata}")
    return jsonify({'status': 'ok'}), 200


@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    from_number = request.form.get('From')
    body = request.form.get('Body', '')
    num_media = int(request.form.get('NumMedia', '0'))
    media_url = request.form.get('MediaUrl0', '') if num_media > 0 else ''

    customer = get_or_create_customer(from_number)
    log_conversation(from_number, 'incoming', 'image' if num_media > 0 else 'text', body or media_url)

    if detect_distress(body):
        response_text = guardrail_response()
        log_conversation(from_number, 'outgoing', 'distress_guardrail', response_text)
        return response_text, 200, {'Content-Type': 'text/plain'}

    parsed = parse_incoming_message(body)
    response_text = handle_message(from_number, body, parsed, customer, media_url, num_media)

    log_conversation(from_number, 'outgoing', 'text', response_text)

    # Return plain text response. Configure your messaging gateway to
    # use this body or replace with a provider-specific reply format.
    return response_text, 200, {'Content-Type': 'text/plain'}


@app.route('/agent/capabilities', methods=['GET'])
def agent_capabilities():
    """Discovery for WhatsApp, web, or future comment/tag adapters."""
    return jsonify({
        'name': 'Augeo Social Agent',
        'capabilities': list(CAPABILITIES),
        'usage': 'Tag Augeo for a design, UGC script, launch-video brief, caption, or content plan.',
    })


@app.route('/agent/execute', methods=['POST'])
def agent_execute():
    """Platform-neutral entry point for a social mention or direct message."""
    payload = request.get_json(silent=True) or {}
    instruction = str(payload.get('instruction', '')).strip()
    if not instruction:
        return jsonify({'error': 'instruction is required'}), 400
    parsed = social_agent.classify(instruction)
    if not parsed:
        return jsonify({'error': 'Ask for a design, UGC script, launch video, caption, or content plan.'}), 400
    context = dict(payload.get('context') or {})
    customer_phone = context.pop('customer_phone', None)
    if customer_phone and 'brand' not in context:
        context['brand'] = brand_manager.build_creative_context(str(customer_phone))
    result = social_agent.execute(parsed, context)
    if customer_phone and result.get('status') == 'submitted':
        video_id = result.get('video', {}).get('video_id')
        if video_id:
            start_video_progress_tracking(str(customer_phone), video_id)
    return jsonify(result)


@app.route('/agent/video/<video_id>', methods=['GET'])
def video_status(video_id: str):
    try:
        return jsonify(social_agent.video_service.status(video_id))
    except Exception as exc:
        return jsonify({'error': str(exc)}), 502


@app.route('/agent/video/<video_id>/content', methods=['GET'])
def video_content(video_id: str):
    try:
        provider_response = social_agent.video_service.download(video_id)
        return Response(
            provider_response.iter_content(chunk_size=64 * 1024),
            content_type=provider_response.headers.get('Content-Type', 'video/mp4'),
            headers={'Content-Disposition': f'inline; filename="{video_id}.mp4"'},
        )
    except Exception as exc:
        return jsonify({'error': str(exc)}), 502


def start_video_progress_tracking(customer_phone: str, video_id: str) -> None:
    """Keep the existing WhatsApp customer informed while an async render runs."""
    def watch() -> None:
        last_progress = -1
        for _ in range(90):  # 30 minutes at a 20-second cadence
            try:
                job = social_agent.video_service.status(video_id)
            except Exception:
                return
            status = str(job.get('status', '')).upper()
            progress = int(job.get('progress') or 0)
            if progress >= last_progress + 25:
                send_whatsapp_message(customer_phone, f"Your video is rendering — {progress}% complete.")
                last_progress = progress
            if status in {'COMPLETED', 'SUCCEEDED'}:
                send_whatsapp_message(
                    customer_phone,
                    "Your product video is ready.",
                    media_url=f"{BASE_URL}/agent/video/{video_id}/content",
                )
                return
            if status in {'FAILED', 'CANCELLED'}:
                send_whatsapp_message(customer_phone, "Your video could not be rendered. Reply with a new product photo and I’ll try again.")
                return
            time.sleep(20)

    worker = threading.Thread(target=watch, daemon=True, name=f"video-{video_id[:12]}")
    worker.start()


def handle_message(from_number: str, body: str, parsed: dict, customer: dict, media_url: str, num_media: int) -> str:
    intent = parsed['intent']
    text = parsed['text']
    state = customer.get('conversation_state') or 'idle'
    data = safe_json_loads(customer.get('conversation_data'))

    # Let a tagged, natural-language request skip the legacy questionnaire.
    # Visual work still uses the proven asset-and-details flyer flow.
    social_request = social_agent.classify(text)
    if social_request and state == 'idle':
        result = social_agent.execute(
            social_request,
            {'channel': 'whatsapp', 'brand': brand_manager.build_creative_context(from_number)},
        )
        if result['status'] == 'ready':
            return result['content']
        if result['status'] == 'submitted':
            video_id = result.get('video', {}).get('video_id')
            if video_id:
                start_video_progress_tracking(from_number, video_id)
            return result['message']
        if num_media > 0:
            update_customer(from_number, conversation_state='collect_details',
                            conversation_data=json.dumps({'reference_image': media_url}))
            return (
                "Nice — this is the part where the product starts to feel sellable. 📸\n\n"
                "Send the offer, who it’s for, and any delivery or sizing notes you want in the flyer."
            )
        return result['message']

    # Global commands
    if intent == 'help':
        return (
            "Hi — I’m Augeo, your brand media partner. I build the creative that sells the product: product visuals, reels, launch films, and campaign-ready content for businesses.\n\n"
            "How it works:\n"
            "1. Send the product or reference asset\n"
            "2. Share the offer, target buyer, and any key notes\n"
            "3. Choose the visual or video direction\n"
            "4. I shape the final output to the brief, not just a template\n\n"
            "Reply 'order' to start, or 'balance' to check credits.\n\n"
            "Reply 'privacy' or 'terms' for full details on data and refunds."
        )

    if intent == 'balance':
        balance = get_credit_balance(from_number)
        return f"You have {balance} flyer credits remaining."

    if intent == 'referral':
        code = customer.get('referral_code', '')
        return (
            f"Your referral code: {code}\n\n"
            f"Share Augéo with a seller friend. When they buy their first pack, "
            f"you both get 2 free flyers!"
        )

    if intent == 'stop':
        update_customer(from_number, reminder_opt_out=1)
        return "Got it. I will pause reminder messages. Reply 'start' anytime to resume."

    if intent in ('privacy', 'terms'):
        if intent == 'privacy':
            return (
                "Your privacy matters to us. We only use your details to make your flyers "
                "and remember your brand style — we never sell your data.\n\n"
                f"Full notice: {BASE_URL}/privacy"
            )
        return (
            "Quick summary: unused credits are refundable within 7 days, used credits aren't "
            "(but we'll fix our own mistakes free). Full details:\n"
            f"{BASE_URL}/terms"
        )

    if intent == 'feedback':
        return handle_feedback(from_number, text, customer)

    # State machine
    if intent == 'order' or state == 'idle':
        if state == 'idle' and intent != 'order':
            # User sent a photo out of the blue
            if num_media > 0:
                update_customer(from_number, conversation_state='collect_details', 
                               conversation_data=json.dumps({'reference_image': media_url}))
                return (
                    "Nice — this is the part where the product starts to feel sellable. 📸\n\n"
                    "Send the offer, who it’s for, and any delivery or sizing notes you want in the flyer."
                )
            return build_conversation_intro()

        update_customer(from_number, conversation_state='collect_details', conversation_data='{}')
        return build_order_prompt()

    if state == 'collect_details':
        # Parse price, sizes, delivery from text
        data['details_text'] = text
        data['price'] = extract_price(text) or '₦0'
        data['sizes'] = extract_sizes(text) or ''
        data['delivery'] = extract_delivery(text) or ''
                # Use remaining text as description
        desc = text
        for pattern in [r'[₦N#]\s*[\d,]+', r'\b[SMXL]+\b', r'same day', r'next day', r'nationwide', r'lagos', r'abuja', r'pickup', r'waybill', r'delivery']:
            desc = re.sub(pattern, '', desc, flags=re.I)
        data['description'] = desc.strip(' ,') or text
        if media_url:
            data['reference_image'] = media_url

        update_customer(from_number, conversation_state='pick_style', conversation_data=json.dumps(data))
        return (
            "Great — which design vibe fits this product?\n\n"
            "1. 🔥 Bold & Energetic — punchy, street-focused\n"
            "2. ✨ Luxury & Elegant — premium, refined\n"
            "3. ⚡ Urgency & Sale — fast-moving, conversion-led\n"
            "4. 🎉 Festive — celebratory, colorful\n"
            "5. 📋 Minimal — clean, professional\n\n"
            "Reply 1–5."
        )

    if state == 'pick_style':
        style_map = {
            '1': 'skill-bold', 'bold': 'skill-bold', 'fire': 'skill-bold',
            '2': 'skill-luxury', 'luxury': 'skill-luxury', 'elegant': 'skill-luxury',
            '3': 'skill-urgency', 'urgency': 'skill-urgency', 'sale': 'skill-urgency', 'flash': 'skill-urgency',
            '4': 'skill-festive', 'festive': 'skill-festive', 'holiday': 'skill-festive',
            '5': 'skill-minimal', 'minimal': 'skill-minimal', 'corporate': 'skill-minimal', 'church': 'skill-minimal',
        }
        chosen = style_map.get(text.lower().strip(), 'skill-luxury')
        data['graphic_skill'] = chosen
        update_customer(from_number, conversation_state='pick_language', conversation_data=json.dumps(data))
        return (
            "Nice choice! Now pick the language for your caption:\n\n"
            "1. 🇬🇧 English (direct & clear)\n\n"
            "Reply 1."
        )

    if state == 'pick_language':
        lang_map = {
            '1': 'skill-english-market', 'english': 'skill-english-market', 'eng': 'skill-english-market',
        }
        chosen = lang_map.get(text.lower().strip(), 'skill-english-market')
        data['prompt_skill'] = chosen

        # Check if user has credits
        balance = get_credit_balance(from_number)
        if balance >= FLYER_CREDIT_COST:
            # Generate preview with watermark
            return generate_and_send_preview(from_number, customer, data)
        else:
            # No credits — show preview but require payment
            update_customer(from_number, conversation_state='preview_ready_no_credits', conversation_data=json.dumps(data))
            return generate_preview_and_payment_prompt(from_number, data)

    if state == 'preview_ready_no_credits':
        if intent == 'yes' or text.lower() in ['1', 'starter', '2', 'growth', '3', 'pro']:
            return handle_pack_purchase(from_number, text, data)
        return (
            "Your preview is ready above ☝️\n\n"
            + get_pack_selection_message()
        )

    if state == 'awaiting_pack_payment':
        pack_name = data.get('pending_pack')
        if pack_name and intent == 'payment_confirm':
            ref = extract_reference(text)
            if ref and verify_paystack_transaction(ref):
                pack = CREDIT_PACKS.get(pack_name)
                if pack:
                    add_credits(from_number, pack['credits'], pack_name=pack_name, paystack_reference=ref)
                    update_customer(from_number, lifetime_value_ngn=pack['price_ngn'])
                    # Now generate the flyer they wanted
                    return generate_and_send_flyer(from_number, customer, data)
            return "Payment verification in progress. Please wait a moment and reply 'paid' again."
        return handle_pack_purchase(from_number, text, data)

    if state == 'collect_feedback':
        return handle_feedback_state(from_number, text, data)

    if state == 'ask_brand_memory':
        if intent == 'yes':
            bm_data = {
                'business_name': data.get('brand_name', ''),
                'template_preference': data.get('graphic_skill', ''),
                'preferred_language': data.get('prompt_skill', ''),
                'category_focus': data.get('niche', ''),
            }
            save_brand_memory(from_number, **bm_data)
            update_customer(from_number, 
                           preferred_graphic_skill=data.get('graphic_skill'),
                           preferred_prompt_skill=data.get('prompt_skill'),
                           preferred_category_skill=data.get('category_skill', 'skill-retail'),
                           conversation_state='idle', conversation_data='{}')
            return (
                "Saved! 🧠 I'll remember your style for next time.\n\n"
                "Just send a photo and I'll use your brand look automatically."
            )
        else:
            update_customer(from_number, conversation_state='idle', conversation_data='{}')
            return "No problem! Send a photo anytime for a new flyer."

    # Default: if they send a photo while idle, restart flow
    if num_media > 0 and state == 'idle':
        update_customer(from_number, conversation_state='collect_details', 
                       conversation_data=json.dumps({'reference_image': media_url}))
        return (
            "New product? Good. We’ve reached the point where the offer can do the selling. 📸\n\n"
            "Send the offer, who it’s for, and any delivery or sizing notes you want me to lean into."
        )

    return (
        "I’m still with you — let’s keep this simple.\n\n"
        "Reply 'order' to create a flyer, 'balance' to check credits, or 'help' for info."
    )


# ===================== HELPERS =====================

def extract_price(text: str) -> str:
    match = re.search(r'[₦N#]\s*([\d,]+)', text)
    if match:
        return f"₦{match.group(1)}"
    match = re.search(r'([\d,]+)\s*naira', text, re.I)
    if match:
        return f"₦{match.group(1)}"
    match = re.search(r'([\d,]+)\s*k', text, re.I)
    if match:
        return f"₦{match.group(1)},000"
    return ''


def extract_sizes(text: str) -> str:
    sizes = re.findall(r'\b([SMLX]+|\d+\s*(cm|inch|in)?)\b', text, re.I)
    return ', '.join([s[0] for s in sizes]) if sizes else ''


def extract_delivery(text: str) -> str:
    keywords = ['same day', 'next day', 'nationwide', 'lagos', 'abuja', 'ph', 'pickup', 'waybill', 'tomorrow']
    for kw in keywords:
        if kw in text.lower():
            idx = text.lower().find(kw)
            start = max(0, idx - 10)
            end = min(len(text), idx + 30)
            return text[start:end].strip()
    return ''


def generate_and_send_preview(from_number: str, customer: dict, data: dict) -> str:
    """Generate watermarked preview, deduct credit, and send."""
    try:
        flyer_bytes, caption = build_flyer_for_order(
            data, data.get('graphic_skill', 'skill-luxury'),
            data.get('prompt_skill', 'skill-english-market'),
            data.get('category_skill', 'skill-retail'),
            watermark=True,
            customer_phone=from_number,
        )

        preview_path = save_flyer_bytes(flyer_bytes, f"preview_{from_number.replace('+', '')}")

        # Deduct credit
        if not deduct_credit(from_number):
            return generate_preview_and_payment_prompt(from_number, data)

        # Save flyer record
        add_flyer(
            from_number,
            preview_path=preview_path,
            caption=caption,
            price=data.get('price'),
            sizes=data.get('sizes'),
            delivery=data.get('delivery'),
            graphic_skill=data.get('graphic_skill'),
            language_skill=data.get('prompt_skill'),
            category_skill=data.get('category_skill'),
        )

        # Build response with retention hooks
        balance = get_credit_balance(from_number)
        response = (
            f"Your flyer is ready! ✨\n\n"
            f"Caption: '{caption}'\n\n"
            f"Save this image and share to your WhatsApp Status."
        )

        response += get_low_credits_message(balance, data.get('graphic_skill'), data.get('prompt_skill'))

        flyer_count = get_flyer_count_for_customer(from_number)
        response += get_brand_memory_message(from_number, flyer_count)

        if flyer_count >= 1:
            response += get_referral_message(customer)

        # Check if we asked brand memory
        if flyer_count == BRAND_MEMORY_THRESHOLD:
            update_customer(from_number, conversation_state='ask_brand_memory', conversation_data=json.dumps(data))
        else:
            update_customer(from_number, conversation_state='idle', conversation_data='{}')

        # Log media link and return the response with a view URL. Integrate
        # a messaging provider here if you want automatic media delivery.
        media_url = f"{BASE_URL}/output/{Path(preview_path).name}"
        print(f"[MEDIA READY] {media_url}")

        return response + f"\n\nView: {media_url}"

    except Exception as e:
        import traceback

        print("=" * 70)
        print("FLYER GENERATION ERROR")
        print("=" * 70)
        print(f"Error: {e}")
        traceback.print_exc()
        print("=" * 70)

        return "Oops, network wahala. Try again in 1 minute. 🙏"


def generate_preview_and_payment_prompt(from_number: str, data: dict) -> str:
    """Generate preview but require payment."""
    try:
        flyer_bytes, caption = build_flyer_for_order(
            data, data.get('graphic_skill', 'skill-luxury'),
            data.get('prompt_skill', 'skill-english-market'),
            data.get('category_skill', 'skill-retail'),
            watermark=True,
            customer_phone=from_number,
        )

        preview_path = save_flyer_bytes(flyer_bytes, f"preview_{from_number.replace('+', '')}")
        data['preview_path'] = preview_path
        data['caption'] = caption
        update_customer(from_number, conversation_state='preview_ready_no_credits', conversation_data=json.dumps(data))

        return (
            f"Here’s your preview ☝️\n\n"
            f"Caption: '{caption}'\n\n"
            + get_pack_selection_message()
        )
    except Exception as e:
        print(f"Preview error: {e}")
        return "Oops, something went wrong. Please try again."


def generate_and_send_flyer(from_number: str, customer: dict, data: dict) -> str:
    """Generate final flyer after credit purchase."""
    return generate_and_send_preview(from_number, customer, data)


def handle_pack_purchase(from_number: str, text: str, data: dict) -> str:
    pack_map = {
        '1': 'starter', 'starter': 'starter', '10': 'starter',
        '2': 'growth', 'growth': 'growth', '25': 'growth',
        '3': 'pro', 'pro': 'pro', '60': 'pro',
    }
    pack_name = pack_map.get(text.lower().strip(), 'starter')
    pack = CREDIT_PACKS.get(pack_name)
    if not pack:
        return "Invalid pack. Reply 1, 2, or 3."

    reference = uuid.uuid4().hex[:12]
    payment_url = create_paystack_payment_link(
        reference, 
        f'{from_number}@augeo.app', 
        pack['price_ngn'] * 100,
        metadata={'pack_name': pack_name, 'customer_phone': from_number, 'order_reference': reference}
    )

    data['pending_pack'] = pack_name
    data['pending_reference'] = reference
    update_customer(from_number, conversation_state='awaiting_pack_payment', conversation_data=json.dumps(data))

    return (
        f"Great choice! {pack['label']}\n\n"
        f"Tap to pay: {payment_url}\n\n"
        f"After payment, reply with 'paid {reference}'."
    )


def handle_feedback(from_number: str, text: str, customer: dict) -> str:
    # Find latest completed flyer
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT * FROM flyers WHERE customer_phone = ? ORDER BY created_at DESC LIMIT 1",
            (from_number,)
        )
        latest = cur.fetchone()

    if not latest:
        return "You don't have any flyers to rate yet. Send a photo to create one!"

    update_customer(from_number, conversation_state='collect_feedback', 
                   conversation_data=json.dumps({'flyer_id': latest['id']}))
    return "Please reply with a number from 1 to 5 to rate your flyer. ⭐"


def handle_feedback_state(from_number: str, text: str, data: dict) -> str:
    try:
        rating = int(text.strip())
        if 1 <= rating <= 5:
            flyer_id = data.get('flyer_id')
            if flyer_id:
                with get_connection() as conn:
                    conn.execute("UPDATE flyers SET feedback = ? WHERE id = ?", (rating, flyer_id))
                    conn.commit()
            update_customer(from_number, conversation_state='idle', conversation_data='{}')
            return f"Thanks for your {rating}-star rating! ⭐ We appreciate it."
    except ValueError:
        pass
    return "Please send a number from 1 to 5."


# Need get_connection for handle_feedback
from database import get_connection


# ===================== RETENTION CRON =====================

def retention_check():
    """Check for re-engagement opportunities every hour."""
    try:
        dormant = get_customers_for_retention(days=7)
        for customer in dormant:
            phone = customer['phone']
            balance = customer['credits_remaining']
            style = customer.get('preferred_graphic_skill', '')
            lang = customer.get('preferred_prompt_skill', '')

            style_map = {
                'skill-luxury': '✨ Luxury',
                'skill-bold': '🔥 Bold',
                'skill-urgency': '⚡ Urgency',
                'skill-festive': '🎉 Festive',
                'skill-minimal': '📋 Minimal',
            }
            style_text = f" I'll use your saved {style_map.get(style, style)} style." if style else ""

            send_whatsapp_message(
                phone,
                f"Hope sales are going well! 🙏\n\n"
                f"You have {balance} flyers left in your pack.{style_text} "
                f"New arrivals this week? Send a photo and I'll create one now.\n\n"
                f"Reply STOP to pause reminders."
            )

        # Low credit nudges (customers with 1-2 credits who haven't been nudged)
        with get_connection() as conn:
            cur = conn.execute(
                "SELECT phone, credits_remaining, preferred_graphic_skill FROM customers "
                "WHERE credits_remaining IN (1, 2) "
                "AND (last_flyer_at > datetime('now', '-3 days') OR last_engagement_at > datetime('now', '-3 days'))"
            )
            low_credit = [dict(row) for row in cur.fetchall()]

        for customer in low_credit:
            phone = customer['phone']
            balance = customer['credits_remaining']
            msg = get_low_credits_message(balance, customer.get('preferred_graphic_skill'))
            if msg:
                send_whatsapp_message(phone, msg.strip())

    except Exception as e:
        print(f"Retention check error: {e}")

    # Schedule next check
    t = threading.Timer(3600, retention_check)
    t.daemon = True
    t.start()


# Start retention loop
_retention_timer = threading.Timer(60, retention_check)
_retention_timer.daemon = True
_retention_timer.start()


def alarm_check_loop():
    try:
        run_all_checks()
    except Exception as e:
        print(f"Alarm check error: {e}")
    t = threading.Timer(1800, alarm_check_loop)  # every 30 minutes
    t.daemon = True
    t.start()


_alarm_timer = threading.Timer(30, alarm_check_loop)
_alarm_timer.daemon = True
_alarm_timer.start()


# ===================== ADMIN & TEST =====================

@app.route('/privacy', methods=['GET'])
def privacy_notice():
    path = Path(__file__).resolve().parent / 'docs' / 'PRIVACY_NOTICE.md'
    if not path.exists():
        return "Privacy notice not found.", 404
    return path.read_text(encoding='utf-8'), 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route('/terms', methods=['GET'])
def terms_and_refunds():
    path = Path(__file__).resolve().parent / 'docs' / 'TERMS_AND_REFUNDS.md'
    if not path.exists():
        return "Terms not found.", 404
    return path.read_text(encoding='utf-8'), 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route('/test', methods=['GET'])
def test_flyer():
    skill_name = request.args.get('skill', 'skill-luxury')
    graphic_skill = skill_registry.get_graphic_skill(skill_name) or skill_registry.get_graphic_skill('skill-luxury')
    caption = (
        "Stella's cosmetics and skincare delivered worldwide. "
        "Luxury beauty essentials for every skin type. "
        "Order now and enjoy fast delivery across the globe."
    )
    price_text = '₦50,000–₦100,000'

    image = Image.new('RGB', (1080, 1080), '#F9F5FF')
    draw = ImageDraw.Draw(image)
    draw.rectangle([120, 120, 960, 960], fill='#6B3F95')
    draw.ellipse([280, 220, 800, 740], fill='#F8C7EA')

    flyer = FlyerGenerator(graphic_skill)

    if USE_GENERATIVE_LAYOUT:
        layout = generate_layout(
            product_description="Stella's cosmetics and skincare line",
            price=price_text,
            graphic_skill=graphic_skill,
        )
        flyer_bytes = flyer.create_flyer_from_layout(image, caption, price_text, layout)
    else:
        flyer_bytes = flyer.create_flyer(image, caption, price_text)

    path = save_flyer_bytes(flyer_bytes, 'stella_test')

    return jsonify({
        'status': 'ok',
        'message': 'Stella flyer generated locally.',
        'skill': skill_name,
        'generative_layout': USE_GENERATIVE_LAYOUT,
        'url': f'{BASE_URL}/output/{Path(path).name}',
    })


@app.route('/output/<path:filename>', methods=['GET'])
def serve_output(filename):
    output_dir = Path('output')
    file_path = output_dir / filename
    if not file_path.exists():
        return jsonify({'error': 'File not found'}), 404
    return send_file(file_path, mimetype='image/jpeg')


@app.route('/stats', methods=['GET'])
def admin_stats():
    return jsonify(get_stats())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=FLASK_DEBUG)
