import os
import sys
from dataclasses import dataclass
import sqlite3 as sql

if sys.platform == "win32":
    data_folder = os.path.join(os.getenv('APPDATA'), "MCModSorter")
elif sys.platform == "darwin":
    data_folder = os.path.join(os.path.expanduser('~'), "Library", "Application Support", "MCModSorter")
else:
    data_folder = os.path.join(os.path.expanduser('~'), ".MCModSorter")

@dataclass
class ModData:
    mod_id: int
    file_id: int
    server: bool
    client: bool

class DataStorage:
    __instance : 'DataStorage | None' = None
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance._init()
        return cls.__instance
    
    def _init(self):
        os.makedirs(data_folder, exist_ok=True)
        self.db_path = os.path.join(data_folder, "data.db")
        self.conn = sql.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()
        
    def _create_tables(self):
        # primary key is a combination of mod_id and file_id
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS mods (
                mod_id INTEGER NOT NULL,
                file_id INTEGER NOT NULL,
                server BOOLEAN NOT NULL,
                client BOOLEAN NOT NULL,
                PRIMARY KEY (mod_id, file_id)
            )
        ''')
        
    def insert_mod(self, mod : ModData):
        self.cursor.execute('''
            INSERT OR REPLACE INTO mods (mod_id, file_id, server, client)
            VALUES (?, ?, ?, ?)
        ''', (mod.mod_id, mod.file_id, mod.server, mod.client))
        self.conn.commit()
        
    def get_mod(self, mod_id: int, file_id: int) -> ModData | None:
        self.cursor.execute('''
            SELECT * FROM mods WHERE mod_id = ? AND file_id = ?
        ''', (mod_id, file_id))
        row = self.cursor.fetchone()
        if row:
            return ModData(*row)
        
    def get_all_mods(self) -> list[ModData]:
        self.cursor.execute('SELECT * FROM mods')
        rows = self.cursor.fetchall()
        return [ModData(*row) for row in rows]

    def close(self):
        self.conn.close()
        
    def __del__(self):
        self.close()
    