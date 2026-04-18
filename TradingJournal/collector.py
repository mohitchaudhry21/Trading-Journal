import MetaTrader5 as mt5
from datetime import datetime
import sqlite3
import time

conn = sqlite3.connect("journal.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS trades (
    ticket INTEGER PRIMARY KEY,
    symbol TEXT,
    type TEXT,
    volume REAL,
    profit REAL,
    time REAL
)
""")
conn.commit()

mt5.initialize()

last_time = 0

print("Collector running...")

while True:

    deals = mt5.history_deals_get(datetime.now().replace(hour=0, minute=0), datetime.now())

    if deals:
        for d in deals:

            if d.entry == 1 and d.time > last_time:

                cursor.execute("""
                INSERT OR IGNORE INTO trades VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    d.position_id,
                    d.symbol,
                    "BUY" if d.type == 1 else "SELL",
                    d.volume,
                    d.profit,
                    d.time
                ))

                conn.commit()

                last_time = d.time

                print("Saved trade:", d.symbol, d.profit)

    time.sleep(2)