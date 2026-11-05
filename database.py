"""SQLite transactions that also release Windows file handles on scope exit."""
import sqlite3


class Connection(sqlite3.Connection):
    def __exit__(self,*error):
        try:
            return super().__exit__(*error)
        finally:
            self.close()


def connect(*args,**kwargs):
    return sqlite3.connect(*args,factory=Connection,**kwargs)
