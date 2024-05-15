# use sqlite for simplicity and because it's lightweight
# in our experiment we use postgresql which is more scalable and easily prevents write skew
import sqlite3

# use Lock to enforce mutual exclusion
from threading import Lock

class KeyValueStore:
    def __init__(self, path=":memory:"):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.lock = Lock()
        # create a table to store key-value pairs. 
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS store 
                               (key TEXT PRIMARY KEY, value TEXT)''')
        self.conn.commit()

    def put(self, key, value):
        # prevent other threads from accessing the database
        with self.lock:
            self.cursor.execute("REPLACE INTO store (key, value) VALUES (?, ?)", (key, value))
            self.conn.commit()

    def get(self, key):
        # prevent other threads from accessing the database
        with self.lock:
            self.cursor.execute("SELECT value FROM store WHERE key=?", (key,))
            item = self.cursor.fetchone()
            return item[0] if item else None

    def delete(self, key):
        # prevent other threads from accessing the database
        with self.lock:
            self.cursor.execute("DELETE FROM store WHERE key=?", (key,))
            self.conn.commit()

    # close the connection to the database
    def close(self):
        self.conn.close()
