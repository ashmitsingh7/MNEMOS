"""A minimal immutable trial ledger; raw ROS bags remain the primary evidence."""
from dataclasses import asdict, dataclass, field
import sqlite3
from pathlib import Path
from time import time
from uuid import uuid4


@dataclass(frozen=True)
class TrialRecord:
    configuration: str
    scenario: str
    success: bool
    duration_seconds: float
    path_length_meters: float
    interventions: int
    collision_events: int
    notes: str = ''
    created_at: float = field(default_factory=time)
    identifier: str = field(default_factory=lambda: str(uuid4()))


class TrialLedger:
    """Stores individual trials; aggregation never silently drops failed runs."""
    def __init__(self, database: str | Path) -> None:
        self.database = str(Path(database).expanduser())
        with self._connect() as connection:
            connection.execute('''CREATE TABLE IF NOT EXISTS trials (
                identifier TEXT PRIMARY KEY, created_at REAL NOT NULL,
                configuration TEXT NOT NULL, scenario TEXT NOT NULL, success INTEGER NOT NULL,
                duration_seconds REAL NOT NULL, path_length_meters REAL NOT NULL,
                interventions INTEGER NOT NULL, collision_events INTEGER NOT NULL, notes TEXT NOT NULL)''')

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        return connection

    def append(self, trial: TrialRecord) -> None:
        with self._connect() as connection:
            connection.execute('''INSERT INTO trials VALUES (
                :identifier,:created_at,:configuration,:scenario,:success,:duration_seconds,
                :path_length_meters,:interventions,:collision_events,:notes)''',
                               {**asdict(trial), 'success': int(trial.success)})

    def count(self, configuration: str | None = None, scenario: str | None = None) -> int:
        query = 'SELECT COUNT(*) FROM trials'
        parameters: list = []
        conditions = []
        if configuration is not None:
            conditions.append('configuration=?')
            parameters.append(configuration)
        if scenario is not None:
            conditions.append('scenario=?')
            parameters.append(scenario)
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        with self._connect() as connection:
            return int(connection.execute(query, parameters).fetchone()[0])

    def summary(self, configuration: str, scenario: str) -> dict[str, float | int]:
        with self._connect() as connection:
            row = connection.execute('''SELECT COUNT(*) AS trials, AVG(success) AS success_rate,
                AVG(duration_seconds) AS mean_duration_seconds,
                AVG(path_length_meters) AS mean_path_length_meters,
                AVG(interventions) AS mean_interventions,
                SUM(collision_events) AS total_collision_events
                FROM trials WHERE configuration=? AND scenario=?''', (configuration, scenario)).fetchone()
        return {key: (0 if row[key] is None else row[key]) for key in row.keys()}
