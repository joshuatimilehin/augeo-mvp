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
"""


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with closing(get_connection()) as conn:
        conn.executescript(SCHEMA)
        conn.commit()


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
