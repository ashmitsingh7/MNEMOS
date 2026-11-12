"""SQLite persistence with atomic writes and a versioned, inspectable schema."""
import json
import sqlite3
from pathlib import Path

from .model import Episode


class EpisodeStore:
    def __init__(self, database: str | Path) -> None:
        self.database = str(Path(database).expanduser())
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute('''
                CREATE TABLE IF NOT EXISTS episodes (
                  identifier TEXT PRIMARY KEY, created_at REAL NOT NULL, kind TEXT NOT NULL,
                  pose_x REAL NOT NULL, pose_y REAL NOT NULL, pose_yaw REAL NOT NULL,
                  goal_x REAL, goal_y REAL, scan_signature TEXT NOT NULL,
                  semantic_tags TEXT NOT NULL, command_delta_linear REAL NOT NULL,
                  command_delta_angular REAL NOT NULL, confidence REAL NOT NULL,
                  evidence TEXT NOT NULL
                )''')
            connection.execute('CREATE INDEX IF NOT EXISTS idx_episode_time ON episodes(created_at DESC)')
            connection.execute('CREATE INDEX IF NOT EXISTS idx_episode_pose ON episodes(pose_x, pose_y)')

    def insert(self, episode: Episode) -> None:
        record = episode.to_record()
        for key in ('scan_signature', 'semantic_tags', 'evidence'):
            record[key] = json.dumps(record[key], separators=(',', ':'))
        with self._connect() as connection:
            connection.execute('''INSERT INTO episodes VALUES (
                :identifier,:created_at,:kind,:pose_x,:pose_y,:pose_yaw,:goal_x,:goal_y,
                :scan_signature,:semantic_tags,:command_delta_linear,:command_delta_angular,
                :confidence,:evidence)''', record)

    def recent(self, limit: int = 500) -> list[Episode]:
        with self._connect() as connection:
            rows = connection.execute('SELECT * FROM episodes ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
        episodes = []
        for row in rows:
            record = dict(row)
            for key in ('scan_signature', 'semantic_tags', 'evidence'):
                record[key] = json.loads(record[key])
            episodes.append(Episode.from_record(record))
        return episodes
