import sqlite3
import json
from pathlib import Path
from contextlib import closing
from datetime import datetime, timezone
from config import DATABASE_PATH

DATABASE_PATH = Path(DATABASE_PATH)

SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT UNIQUE NOT NULL,
    name TEXT,
    business_name TEXT,
    language_preference TEXT DEFAULT 'english-market',
    credits_remaining INTEGER DEFAULT 0,
    total_flyers_generated INTEGER DEFAULT 0,
    total_purchases INTEGER DEFAULT 0,
    lifetime_value_ngn INTEGER DEFAULT 0,
    referral_code TEXT UNIQUE,
    referred_by TEXT,
    brand_memory_json TEXT,
    preferred_graphic_skill TEXT,
    preferred_prompt_skill TEXT,
    preferred_category_skill TEXT,
    preferred_tone TEXT,
    preferred_category_focus TEXT,
    last_flyer_at TEXT,
    last_engagement_at TEXT,
    reminder_opt_out BOOLEAN DEFAULT 0,
    conversation_state TEXT,
    conversation_data TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS flyers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_phone TEXT NOT NULL,
    product_photo_path TEXT,
    generated_flyer_path TEXT,
    preview_path TEXT,
    caption TEXT,
    price TEXT,
    sizes TEXT,
    delivery TEXT,
    graphic_skill TEXT,
    language_skill TEXT,
    category_skill TEXT,
    template_used TEXT,
    credits_used INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_phone) REFERENCES customers(phone)
);

CREATE TABLE IF NOT EXISTS skill_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_phone TEXT,
    graphic_skill TEXT,
    language_skill TEXT,
    category_skill TEXT,
    engagement_signal BOOLEAN,
    feedback TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS prompt_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id TEXT UNIQUE NOT NULL,
    times_used INTEGER DEFAULT 0,
    average_score REAL DEFAULT 0.0,
    best_score REAL DEFAULT 0.0,
    last_score REAL DEFAULT 0.0,
    last_used_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS creative_evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_phone TEXT,
    prompt_id TEXT NOT NULL,
    flyer_id INTEGER,
    visual_quality REAL,
    customer_approval REAL,
    relevance REAL,
    originality REAL,
    conversion_signal REAL,
    overall_score REAL,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_phone) REFERENCES customers(phone),
    FOREIGN KEY (flyer_id) REFERENCES flyers(id)
);

CREATE TABLE IF NOT EXISTS credit_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_phone TEXT,
    type TEXT,
    amount INTEGER,
    pack_name TEXT,
    paystack_reference TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_phone TEXT,
    direction TEXT,
    message_type TEXT,
    content TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS layout_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_phone TEXT NOT NULL,
    layout_json TEXT,
    image_hash TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS originality_flags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_phone TEXT,
    flyer_hash TEXT,
    matched_hash TEXT,
    matched_customer_phone TEXT,
    hamming_distance INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS brand_memory (
    customer_phone TEXT PRIMARY KEY,
    business_name TEXT,
    primary_color TEXT,
    secondary_color TEXT,
    logo_path TEXT,
    preferred_language TEXT,
    preferred_tone TEXT,
    common_phrases TEXT,
    avoid_words TEXT,
    category_focus TEXT,
    template_preference TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS usage_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_phone TEXT,
    session_id TEXT,
    job_id TEXT,
    provider TEXT,
    operation TEXT,
    units REAL,
    cost REAL,
    currency TEXT DEFAULT 'NGN',
    status TEXT DEFAULT 'pending',
    idempotency_key TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audio_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_phone TEXT,
    file_path TEXT,
    mime TEXT,
    size_bytes INTEGER,
    duration_seconds REAL,
    status TEXT DEFAULT 'received',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audio_transcripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audio_message_id INTEGER,
    provider TEXT,
    transcript TEXT,
    confidence REAL,
    metadata_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (audio_message_id) REFERENCES audio_messages(id)
);

CREATE TABLE IF NOT EXISTS creative_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_phone TEXT,
    type TEXT,
    brief TEXT,
    context_json TEXT,
    direction TEXT,
    production_plan_json TEXT,
    assets_json TEXT,
    constraints_json TEXT,
    provider TEXT,
    status TEXT DEFAULT 'pending',
    outputs_json TEXT,
    intent TEXT,
    subject TEXT,
    audience TEXT,
    desired_effect TEXT,
    medium TEXT,
    format TEXT,
    references_json TEXT,
    approval_state TEXT DEFAULT 'pending',
    notes_json TEXT,
    memory_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_creative_job_columns():
    with closing(get_connection()) as conn:
        existing = conn.execute("PRAGMA table_info(creative_jobs)").fetchall()
        existing_names = {row[1] for row in existing}
        for column_sql in [
            "ALTER TABLE creative_jobs ADD COLUMN production_plan_json TEXT",
            "ALTER TABLE creative_jobs ADD COLUMN intent TEXT",
            "ALTER TABLE creative_jobs ADD COLUMN subject TEXT",
            "ALTER TABLE creative_jobs ADD COLUMN audience TEXT",
            "ALTER TABLE creative_jobs ADD COLUMN desired_effect TEXT",
            "ALTER TABLE creative_jobs ADD COLUMN medium TEXT",
            "ALTER TABLE creative_jobs ADD COLUMN format TEXT",
            "ALTER TABLE creative_jobs ADD COLUMN references_json TEXT",
            "ALTER TABLE creative_jobs ADD COLUMN approval_state TEXT DEFAULT 'pending'",
            "ALTER TABLE creative_jobs ADD COLUMN notes_json TEXT",
            "ALTER TABLE creative_jobs ADD COLUMN memory_json TEXT",
        ]:
            column_name = column_sql.split("ADD COLUMN ", 1)[1].split(" ", 1)[0]
            if column_name in existing_names:
                continue
            try:
                conn.execute(column_sql)
            except sqlite3.OperationalError:
                pass
        conn.commit()


def initialize_db():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with closing(get_connection()) as conn:
        conn.executescript(SCHEMA)
        for column_sql in [
            "ALTER TABLE customers ADD COLUMN preferred_tone TEXT",
            "ALTER TABLE customers ADD COLUMN preferred_category_focus TEXT",
        ]:
            try:
                conn.execute(column_sql)
            except sqlite3.OperationalError:
                pass
        conn.commit()
    ensure_creative_job_columns()


def remember_customer_preferences(phone, *, tone=None, category_focus=None, business_name=None, graphic_skill=None, prompt_skill=None, category_skill=None):
    payload = {}
    if tone is not None:
        payload['preferred_tone'] = tone
    if category_focus is not None:
        payload['preferred_category_focus'] = category_focus
    if business_name is not None:
        payload['business_name'] = business_name
    if graphic_skill is not None:
        payload['preferred_graphic_skill'] = graphic_skill
    if prompt_skill is not None:
        payload['preferred_prompt_skill'] = prompt_skill
    if category_skill is not None:
        payload['preferred_category_skill'] = category_skill
    if not payload:
        return None
    get_or_create_customer(phone)
    update_customer(phone, **payload)
    return get_customer_by_phone(phone)


def get_or_create_customer(phone, name=None):
    with closing(get_connection()) as conn:
        cur = conn.execute('SELECT * FROM customers WHERE phone = ?', (phone,))
        row = cur.fetchone()
        if row:
            return dict(row)
        import uuid
        referral_code = uuid.uuid4().hex[:8].upper()
        cur = conn.execute(
            'INSERT INTO customers (phone, name, referral_code) VALUES (?, ?, ?)',
            (phone, name, referral_code),
        )
        conn.commit()
        cur = conn.execute('SELECT * FROM customers WHERE id = ?', (cur.lastrowid,))
        return dict(cur.fetchone())


def get_customer_by_phone(phone):
    with closing(get_connection()) as conn:
        cur = conn.execute('SELECT * FROM customers WHERE phone = ?', (phone,))
        row = cur.fetchone()
        return dict(row) if row else None


def get_customer(customer_id):
    with closing(get_connection()) as conn:
        cur = conn.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def update_customer(phone, **fields):
    if not fields:
        return
    columns = ', '.join("%s = ?" % k for k in fields)
    values = list(fields.values()) + [phone]
    with closing(get_connection()) as conn:
        conn.execute('UPDATE customers SET ' + columns + ' WHERE phone = ?', values)
        conn.commit()


def add_credits(phone, amount, pack_name=None, paystack_reference=None, txn_type='purchase'):
    with closing(get_connection()) as conn:
        conn.execute(
            'INSERT INTO credit_transactions (customer_phone, type, amount, pack_name, paystack_reference) VALUES (?, ?, ?, ?, ?)',
            (phone, txn_type, amount, pack_name, paystack_reference)
        )
        conn.execute(
            'UPDATE customers SET credits_remaining = credits_remaining + ?, total_purchases = total_purchases + 1 WHERE phone = ?',
            (amount, phone)
        )
        conn.commit()


def deduct_credit(phone):
    with closing(get_connection()) as conn:
        cur = conn.execute('SELECT credits_remaining FROM customers WHERE phone = ?', (phone,))
        row = cur.fetchone()
        if not row or row['credits_remaining'] < 1:
            return False
        conn.execute(
            'UPDATE customers SET credits_remaining = credits_remaining - 1, total_flyers_generated = total_flyers_generated + 1, last_flyer_at = ? WHERE phone = ?',
            (datetime.utcnow().isoformat(), phone)
        )
        conn.commit()
        return True


def get_credit_balance(phone):
    with closing(get_connection()) as conn:
        cur = conn.execute('SELECT credits_remaining FROM customers WHERE phone = ?', (phone,))
        row = cur.fetchone()
        return row['credits_remaining'] if row else 0


def add_flyer(customer_phone, **fields):
    with closing(get_connection()) as conn:
        columns = ', '.join(fields.keys())
        placeholders = ', '.join('?' for _ in fields)
        cur = conn.execute(
            'INSERT INTO flyers (customer_phone, ' + columns + ') VALUES (?, ' + placeholders + ')',
            (customer_phone, *fields.values())
        )
        conn.commit()
        return cur.lastrowid


def log_conversation(phone, direction, message_type, content):
    with closing(get_connection()) as conn:
        conn.execute(
            'INSERT INTO conversations (customer_phone, direction, message_type, content) VALUES (?, ?, ?, ?)',
            (phone, direction, message_type, content)
        )
        conn.commit()


def get_flyer_count_for_customer(phone):
    with closing(get_connection()) as conn:
        cur = conn.execute('SELECT COUNT(*) as count FROM flyers WHERE customer_phone = ?', (phone,))
        return cur.fetchone()['count']


def get_customers_for_retention(days=7):
    with closing(get_connection()) as conn:
        cur = conn.execute(
            "SELECT phone, credits_remaining, preferred_graphic_skill, preferred_prompt_skill "
            "FROM customers "
            "WHERE (last_flyer_at < datetime('now', '-" + str(days) + " days') OR last_flyer_at IS NULL) "
            "AND credits_remaining > 0 "
            "AND reminder_opt_out = 0 "
            "AND created_at < datetime('now', '-1 days')"
        )
        return [dict(row) for row in cur.fetchall()]


def save_brand_memory(phone, **fields):
    with closing(get_connection()) as conn:
        columns = ', '.join(fields.keys())
        placeholders = ', '.join('?' for _ in fields)
        updates = ', '.join("%s=excluded.%s" % (k, k) for k in fields)
        conn.execute(
            'INSERT INTO brand_memory (customer_phone, ' + columns + ', updated_at) '
            'VALUES (?, ' + placeholders + ', ?) '
            'ON CONFLICT(customer_phone) DO UPDATE SET '
            + updates + ', updated_at=excluded.updated_at',
            (phone, *fields.values(), datetime.utcnow().isoformat())
        )
        conn.commit()


def get_brand_memory(phone):
    with closing(get_connection()) as conn:
        cur = conn.execute('SELECT * FROM brand_memory WHERE customer_phone = ?', (phone,))
        row = cur.fetchone()
        return dict(row) if row else None


def get_customer_by_referral_code(code):
    with closing(get_connection()) as conn:
        cur = conn.execute('SELECT * FROM customers WHERE referral_code = ?', (code,))
        row = cur.fetchone()
        return dict(row) if row else None


def save_layout(phone, layout: dict, image_hash: str = None):
    with closing(get_connection()) as conn:
        conn.execute(
            'INSERT INTO layout_history (customer_phone, layout_json, image_hash) VALUES (?, ?, ?)',
            (phone, json.dumps(layout), image_hash)
        )
        # Keep only the last 5 per customer so this table doesn't grow unbounded
        conn.execute(
            'DELETE FROM layout_history WHERE customer_phone = ? AND id NOT IN '
            '(SELECT id FROM layout_history WHERE customer_phone = ? ORDER BY id DESC LIMIT 5)',
            (phone, phone)
        )
        conn.commit()


def get_recent_hashes(limit=200):
    """Recent (phone, hash) pairs across ALL customers, for originality checks."""
    with closing(get_connection()) as conn:
        cur = conn.execute(
            'SELECT customer_phone, image_hash FROM layout_history '
            'WHERE image_hash IS NOT NULL ORDER BY id DESC LIMIT ?',
            (limit,)
        )
        return [(row['customer_phone'], row['image_hash']) for row in cur.fetchall()]


def log_originality_flag(phone, flyer_hash, matched_hash, matched_phone, distance):
    with closing(get_connection()) as conn:
        conn.execute(
            'INSERT INTO originality_flags (customer_phone, flyer_hash, matched_hash, '
            'matched_customer_phone, hamming_distance) VALUES (?, ?, ?, ?, ?)',
            (phone, flyer_hash, matched_hash, matched_phone, distance)
        )
        conn.commit()


def get_recent_layouts(phone, limit=3):
    with closing(get_connection()) as conn:
        cur = conn.execute(
            'SELECT layout_json FROM layout_history WHERE customer_phone = ? ORDER BY id DESC LIMIT ?',
            (phone, limit)
        )
        rows = cur.fetchall()
    layouts = []
    for row in rows:
        try:
            layouts.append(json.loads(row['layout_json']))
        except (TypeError, json.JSONDecodeError):
            continue
    return list(reversed(layouts))


def get_stats():
    with closing(get_connection()) as conn:
        stats = {}
        cur = conn.execute('SELECT COUNT(*) as count FROM customers')
        stats['total_customers'] = cur.fetchone()['count']
        cur = conn.execute('SELECT COUNT(*) as count FROM flyers')
        stats['total_flyers'] = cur.fetchone()['count']
        cur = conn.execute('SELECT SUM(lifetime_value_ngn) as total FROM customers')
        stats['total_revenue'] = cur.fetchone()['total'] or 0
        cur = conn.execute('SELECT COUNT(*) as count FROM customers WHERE credits_remaining > 0')
        stats['customers_with_credits'] = cur.fetchone()['count']
        return stats


def create_usage_transaction(customer_phone: str, session_id: str = None, job_id: str = None,
                             provider: str = None, operation: str = None, units: float = 0.0,
                             cost: float = None, currency: str = 'NGN', status: str = 'pending',
                             idempotency_key: str = None) -> int:
    """Insert a usage ledger entry and return its row id."""
    with closing(get_connection()) as conn:
        cur = conn.execute(
            'INSERT INTO usage_transactions (customer_phone, session_id, job_id, provider, operation, units, cost, currency, status, idempotency_key) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (customer_phone, session_id, job_id, provider, operation, units, cost, currency, status, idempotency_key)
        )
        conn.commit()
        return cur.lastrowid


def update_usage_transaction_status(txn_id: int, status: str, cost: float = None) -> None:
    """Update status (and optionally cost) for a usage transaction."""
    with closing(get_connection()) as conn:
        if cost is not None:
            conn.execute('UPDATE usage_transactions SET status = ?, cost = ? WHERE id = ?', (status, cost, txn_id))
        else:
            conn.execute('UPDATE usage_transactions SET status = ? WHERE id = ?', (status, txn_id))
        conn.commit()


def get_usage_transactions_for_customer(phone: str, limit: int = 100) -> list:
    with closing(get_connection()) as conn:
        cur = conn.execute('SELECT * FROM usage_transactions WHERE customer_phone = ? ORDER BY id DESC LIMIT ?', (phone, limit))
        return [dict(row) for row in cur.fetchall()]


def get_usage_transaction_by_job_id(job_id: str):
    with closing(get_connection()) as conn:
        cur = conn.execute('SELECT * FROM usage_transactions WHERE job_id = ?', (job_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def get_usage_transaction_by_idempotency_key(idempotency_key: str):
    with closing(get_connection()) as conn:
        cur = conn.execute('SELECT * FROM usage_transactions WHERE idempotency_key = ? LIMIT 1', (idempotency_key,))
        row = cur.fetchone()
        return dict(row) if row else None


def create_audio_message(customer_phone: str, file_path: str, mime: str, size_bytes: int, duration_seconds: float = None, status: str = 'received') -> int:
    with closing(get_connection()) as conn:
        cur = conn.execute(
            'INSERT INTO audio_messages (customer_phone, file_path, mime, size_bytes, duration_seconds, status) VALUES (?, ?, ?, ?, ?, ?)',
            (customer_phone, file_path, mime, size_bytes, duration_seconds, status)
        )
        conn.commit()
        return cur.lastrowid


def update_audio_message_status(audio_id: int, status: str) -> None:
    with closing(get_connection()) as conn:
        conn.execute('UPDATE audio_messages SET status = ? WHERE id = ?', (status, audio_id))
        conn.commit()


def add_audio_transcript(audio_message_id: int, provider: str, transcript: str, confidence: float = None, metadata_json: str = None) -> int:
    with closing(get_connection()) as conn:
        cur = conn.execute(
            'INSERT INTO audio_transcripts (audio_message_id, provider, transcript, confidence, metadata_json) VALUES (?, ?, ?, ?, ?)',
            (audio_message_id, provider, transcript, confidence, metadata_json)
        )
        conn.commit()
        return cur.lastrowid


def get_audio_messages_for_customer(phone: str, limit: int = 50) -> list:
    with closing(get_connection()) as conn:
        cur = conn.execute('SELECT * FROM audio_messages WHERE customer_phone = ? ORDER BY id DESC LIMIT ?', (phone, limit))
        return [dict(row) for row in cur.fetchall()]
def get_latest_transcript_for_audio(audio_message_id: int):
    with closing(get_connection()) as conn:
        cur = conn.execute(
            'SELECT * FROM audio_transcripts WHERE audio_message_id = ? ORDER BY id DESC LIMIT 1',
            (audio_message_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None


def create_creative_job(customer_phone: str, job_type: str, brief: str, context_json: str = None,
                        direction: str = None, production_plan_json: str = None, assets_json: str = None, constraints_json: str = None,
                        provider: str = None, status: str = 'pending',
                        intent: str = None, subject: str = None, audience: str = None,
                        desired_effect: str = None, medium: str = None, format: str = None,
                        references_json: str = None, approval_state: str = 'pending',
                        notes_json: str = None, memory_json: str = None) -> int:
    ensure_creative_job_columns()
    with closing(get_connection()) as conn:
        cur = conn.execute(
            '''
            INSERT INTO creative_jobs (
                customer_phone, type, brief, context_json, direction, production_plan_json,
                assets_json, constraints_json, provider, status, intent, subject, audience,
                desired_effect, medium, format, references_json, approval_state, notes_json,
                memory_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                customer_phone, job_type, brief, context_json, direction, production_plan_json,
                assets_json, constraints_json, provider, status, intent, subject, audience,
                desired_effect, medium, format, references_json, approval_state, notes_json,
                memory_json,
            )
        )
        conn.commit()
        return cur.lastrowid


def get_creative_job(job_id: int):
    with closing(get_connection()) as conn:
        cur = conn.execute('SELECT * FROM creative_jobs WHERE id = ?', (job_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def list_creative_jobs_for_customer(phone: str, limit: int = 50) -> list:
    with closing(get_connection()) as conn:
        cur = conn.execute('SELECT * FROM creative_jobs WHERE customer_phone = ? ORDER BY id DESC LIMIT ?', (phone, limit))
        return [dict(row) for row in cur.fetchall()]

def record_prompt_evaluation(
    prompt_id,
    score,
    customer_phone=None,
    flyer_id=None,
    visual_quality=None,
    customer_approval=None,
    relevance=None,
    originality=None,
    conversion_signal=None,
    notes=None,
):
    """
    Persist a creative evaluation and update the prompt's
    historical performance.

    The prompt itself remains in the prompt library.
    This table stores its observed performance.
    """

    with closing(get_connection()) as conn:

        conn.execute(
            """
            INSERT INTO creative_evaluations (
                customer_phone,
                prompt_id,
                flyer_id,
                visual_quality,
                customer_approval,
                relevance,
                originality,
                conversion_signal,
                overall_score,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                customer_phone,
                prompt_id,
                flyer_id,
                visual_quality,
                customer_approval,
                relevance,
                originality,
                conversion_signal,
                score,
                notes,
            ),
        )

        existing = conn.execute(
            """
            SELECT
                times_used,
                average_score,
                best_score
            FROM prompt_performance
            WHERE prompt_id = ?
            """,
            (prompt_id,),
        ).fetchone()

        now = datetime.now(timezone.utc).isoformat()
        if existing:

            old_count = existing["times_used"]
            old_average = existing["average_score"]

            new_count = old_count + 1

            new_average = (
                (
                    old_average * old_count
                )
                + score
            ) / new_count

            new_best = max(
                existing["best_score"],
                score,
            )

            conn.execute(
                """
                UPDATE prompt_performance
                SET
                    times_used = ?,
                    average_score = ?,
                    best_score = ?,
                    last_score = ?,
                    last_used_at = ?,
                    updated_at = ?
                WHERE prompt_id = ?
                """,
                (
                    new_count,
                    new_average,
                    new_best,
                    score,
                    now,
                    now,
                    prompt_id,
                ),
            )

        else:

            conn.execute(
                """
                INSERT INTO prompt_performance (
                    prompt_id,
                    times_used,
                    average_score,
                    best_score,
                    last_score,
                    last_used_at,
                    updated_at
                )
                VALUES (?, 1, ?, ?, ?, ?, ?)
                """,
                (
                    prompt_id,
                    score,
                    score,
                    score,
                    now,
                    now,
                ),
            )

        conn.commit()


def get_prompt_performance(prompt_id):
    """
    Return historical performance for one prompt.
    """

    with closing(get_connection()) as conn:

        cur = conn.execute(
            """
            SELECT *
            FROM prompt_performance
            WHERE prompt_id = ?
            """,
            (prompt_id,),
        )

        row = cur.fetchone()

        return dict(row) if row else None


def get_all_prompt_performance():
    """
    Return historical performance for all prompts.
    """

    with closing(get_connection()) as conn:

        cur = conn.execute(
            """
            SELECT *
            FROM prompt_performance
            ORDER BY average_score DESC
            """
        )

        return [
            dict(row)
            for row in cur.fetchall()
        ]
