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

    _COLUMNS = (
        ('identifier', 'TEXT PRIMARY KEY'),
        ('created_at', 'REAL NOT NULL'),
        ('kind', 'TEXT NOT NULL'),
        ('pose_x', 'REAL NOT NULL'),
        ('pose_y', 'REAL NOT NULL'),
        ('pose_yaw', 'REAL NOT NULL'),
        ('goal_x', 'REAL'),
        ('goal_y', 'REAL'),
        ('map_session_id', 'TEXT'),
        ('autonomous_command_linear', 'REAL NOT NULL DEFAULT 0.0'),
        ('autonomous_command_angular', 'REAL NOT NULL DEFAULT 0.0'),
        ('human_command_linear', 'REAL NOT NULL DEFAULT 0.0'),
        ('human_command_angular', 'REAL NOT NULL DEFAULT 0.0'),
        ('scan_signature', 'TEXT NOT NULL'),
        ('semantic_tags', 'TEXT NOT NULL'),
        ('command_delta_linear', 'REAL NOT NULL'),
        ('command_delta_angular', 'REAL NOT NULL'),
        ('confidence', 'REAL NOT NULL'),
        ('evidence', 'TEXT NOT NULL'),
        ('intervention_started_at', 'REAL'),
        ('intervention_ended_at', 'REAL'),
        ('outcome', 'TEXT'),
        ('bag_reference', 'TEXT'),
    )

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute('CREATE TABLE IF NOT EXISTS episodes (' +
                               ', '.join(f'{name} {definition}' for name, definition in self._COLUMNS) + ')')
            # Migrate older databases by adding any missing columns.
            existing = {row[1] for row in connection.execute('PRAGMA table_info(episodes)').fetchall()}
            numeric_defaults = {'autonomous_command_linear', 'autonomous_command_angular',
                                'human_command_linear', 'human_command_angular'}
            for name, definition in self._COLUMNS:
                if name not in existing:
                    column_type = definition.split()[0]
                    default = ' DEFAULT 0.0' if name in numeric_defaults else ''
                    connection.execute(f'ALTER TABLE episodes ADD COLUMN {name} {column_type}{default}')
            connection.execute('CREATE INDEX IF NOT EXISTS idx_episode_time ON episodes(created_at DESC)')
            connection.execute('CREATE INDEX IF NOT EXISTS idx_episode_pose ON episodes(pose_x, pose_y)')

    def insert(self, episode: Episode) -> None:
        record = episode.to_record()
        for key in ('scan_signature', 'semantic_tags', 'evidence'):
            record[key] = json.dumps(record[key], separators=(',', ':'))
        columns = [name for name, _ in self._COLUMNS]
        placeholders = ', '.join(':' + name for name in columns)
        column_list = ', '.join(columns)
        with self._connect() as connection:
            connection.execute(f'INSERT INTO episodes ({column_list}) VALUES ({placeholders})', record)

    def count(self) -> int:
        with self._connect() as connection:
            return int(connection.execute('SELECT COUNT(*) FROM episodes').fetchone()[0])

    def recent(self, limit: int = 500) -> list[Episode]:
        if limit is not None and limit <= 0:
            return []
        with self._connect() as connection:
            if limit is None:
                rows = connection.execute('SELECT * FROM episodes ORDER BY created_at DESC').fetchall()
            else:
                rows = connection.execute('SELECT * FROM episodes ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
        episodes = []
        for row in rows:
            record = dict(row)
            for key in ('scan_signature', 'semantic_tags', 'evidence'):
                record[key] = json.loads(record[key])
            episodes.append(Episode.from_record(record))
        return episodes
