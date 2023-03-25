import sqlite3


def init_db() -> sqlite3.Connection:
    db = sqlite3.connect("hn-bot.db")
    with db:
        db.execute(
            """CREATE TABLE IF NOT EXISTS hn_posts(
                id PRIMARY_KEY,
                stored_at INT NOT NULL,
                created_at INT NOT NULL,
                updated_at INT NOT NULL,
                toot_id INT,
                tooted_at INT
            )"""
        )
    return db
