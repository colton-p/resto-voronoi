import logging
import sqlite3

class Persist:
    def __init__(self, tag, dbfile) -> None:
        self.tag = tag
        self.con = sqlite3.connect(dbfile)
        pass

    def _get_known(self):
        res = self.cur.execute("SELECT tag, store_id from locations where tag = ?", (self.tag,))

        return set(res.fetchall())

    def __enter__(self):
        self.cur = self.con.cursor()
        self.known = self._get_known()
        logging.info('%d known locations', len(self.known))
        return self
    
    def __exit__(self, type, value, traceback):
        self.con.close()
    
    def save_record(self, records):
        rows = [
            (self.tag, id, name, city, state, country, lat, lon) for
            (id, name, city, state, country, (lat, lon)) in records
            if (self.tag, str(id)) not in self.known
        ]
        self.known |= {(tag, str(id)) for (tag, id, *_) in rows}
        if rows:
            logging.info('saved %d locations', len(rows))
            self.cur.executemany("INSERT INTO locations VALUES(null, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
            self.con.commit()
