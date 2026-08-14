"""
Augeo Originality Check
------------------------
A lightweight safeguard against the generative layout engine producing
near-duplicate flyers — either repeating a customer's own past output,
or (much less likely, since the model never sees reference images)
converging on something structurally identical to another customer's.

This is NOT a copyright scanner against the wider internet — that's a
different, heavier problem. This catches OUR OWN system repeating
itself, and gives you an audit trail: if anyone ever questions whether
your output is original, you can show you're actively checking for it.

Uses perceptual hashing (imagehash) rather than exact byte comparison,
so it catches near-duplicates (same layout, different price/caption)
not just identical files.
"""

from typing import Optional, Tuple
import imagehash
from PIL import Image
import io

from database import get_recent_hashes, log_originality_flag

# Hamming distance threshold below which two flyers are flagged as
# suspiciously similar. 0 = identical. Perceptual hashes are 64-bit;
# a distance under ~8 generally means near-duplicate composition.
SIMILARITY_THRESHOLD = 8


def compute_hash(flyer_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(flyer_bytes))
    return str(imagehash.phash(img))


def check_originality(phone: str, flyer_bytes: bytes) -> Tuple[str, Optional[dict]]:
    """
    Returns (hash_str, flag_info). flag_info is None if the flyer looks
    original; otherwise a dict describing the closest match, and the
    match has already been logged to originality_flags for review.

    Never raises — a hashing failure just means no flag, not a crash.
    """
    try:
        new_hash = compute_hash(flyer_bytes)
    except Exception as e:
        print(f"[originality] could not hash flyer: {e}")
        return "", None

    try:
        new_hash_obj = imagehash.hex_to_hash(new_hash)
        closest_distance = None
        closest_match = None

        for other_phone, other_hash_str in get_recent_hashes():
            if not other_hash_str:
                continue
            try:
                other_hash_obj = imagehash.hex_to_hash(other_hash_str)
            except (TypeError, ValueError):
                continue
            distance = new_hash_obj - other_hash_obj
            if closest_distance is None or distance < closest_distance:
                closest_distance = distance
                closest_match = (other_phone, other_hash_str)

        if closest_distance is not None and closest_distance <= SIMILARITY_THRESHOLD:
            other_phone, other_hash_str = closest_match
            log_originality_flag(phone, new_hash, other_hash_str, other_phone, closest_distance)
            return new_hash, {
                'matched_customer': other_phone,
                'hamming_distance': closest_distance,
            }

        return new_hash, None
    except Exception as e:
        print(f"[originality] comparison failed: {e}")
        return new_hash, None
