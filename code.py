import json
import time
from datetime import datetime
from collections import defaultdict
from typing import Any, Dict, List, Optional

class LightweightDB:
    def __init__(self, name: str = "colab_db"):
        self.name = name
        self.tables = {}
        self.indexes = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        self._pk_maps = defaultdict(dict)
        self.stats = {'queries': 0, 'inserts': 0, 'updates': 0, 'deletes': 0, 'start_time': time.time()}
        self._setup_system_tables()

    def _setup_system_tables(self):
        self.create_table('_system_tables', ['name', 'columns', 'row_count', 'created_at'])
        self.create_table('_system_indexes', ['table_name', 'column_name', 'index_type'])

    def create_table(self, table_name: str, columns: List[str], primary_key: str = None):
        if table_name in self.tables: raise ValueError(f"Table exists")
        self.tables[table_name] = {
            'columns': columns, 'rows': {}, 'next_id': 0, 'primary_key': primary_key,
            'column_index': {col: i for i, col in enumerate(columns)}
        }
        if not table_name.startswith('_'):
            self.insert('_system_tables', {'name': table_name, 'columns': json.dumps(columns), 'row_count': 0})
        return True

    def insert(self, table_name: str, data: Dict[str, Any]) -> int:
        table = self.tables[table_name]
        row_id = table['next_id']
        pk = table['primary_key']
        if pk:
            val = data[pk]
            if val in self._pk_maps[table_name]: raise ValueError("Duplicate PK")
            self._pk_maps[table_name][val] = row_id
        row = [data.get(col) for col in table['columns']]
        table['rows'][row_id] = row
        table['next_id'] += 1
        self._update_indexes(table_name, row, row_id)
        self.stats['inserts'] += 1
        self._update_table_stats(table_name)
        return row_id

    def select(self, table_name, columns=None, where=None, limit=None):
        table = self.tables[table_name]
        self.stats['queries'] += 1
        ids = table['rows'].keys()
        if where:
            indexed = set(where.keys()) & set(self.indexes[table_name].keys())
            if indexed:
                col = list(indexed)[0]
                ids = self.indexes[table_name][col].get(where[col], [])
        
        results = []
        for r_id in ids:
            row = table['rows'][r_id]
            if self._row_matches_where(row, table, where):
                res_cols = columns if columns else table['columns']
                results.append({col: row[table['column_index'][col]] for col in res_cols})
                if limit and len(results) >= limit: break
        return results

    def update(self, table_name, data, where=None):
        table = self.tables[table_name]
        targets = [r_id for r_id, row in table['rows'].items() if self._row_matches_where(row, table, where)]
        for r_id in targets:
            row = table['rows'][r_id]
            self._remove_from_indexes(table_name, row, r_id)
            for col, val in data.items():
                if col in table['column_index']:
                    if col == table['primary_key']:
                        del self._pk_maps[table_name][row[table['column_index'][col]]]
                        self._pk_maps[table_name][val] = r_id
                    row[table['column_index'][col]] = val
            self._update_indexes(table_name, row, r_id)
        self.stats['updates'] += 1
        return len(targets)

    def delete(self, table_name, where=None):
        table = self.tables[table_name]
        targets = [r_id for r_id, row in table['rows'].items() if self._row_matches_where(row, table, where)]
        for r_id in targets:
            row = table['rows'][r_id]
            if table['primary_key']: del self._pk_maps[table_name][row[table['column_index'][table['primary_key']]]]
            self._remove_from_indexes(table_name, row, r_id)
            del table['rows'][r_id]
        self.stats['deletes'] += len(targets)
        self._update_table_stats(table_name)
        return len(targets)

    def create_index(self, table_name, column_name):
        table = self.tables[table_name]
        col_idx = table['column_index'][column_name]
        for r_id, row in table['rows'].items():
            if row[col_idx] is not None: self.indexes[table_name][column_name][row[col_idx]].append(r_id)
        return True

    def _row_matches_where(self, row, table, where):
        if not where: return True
        return all(row[table['column_index'][k]] == v for k, v in where.items())

    def _update_indexes(self, table_name, row, row_id):
        for col, val_map in self.indexes[table_name].items():
            val = row[self.tables[table_name]['column_index'][col]]
            if val is not None: val_map[val].append(row_id)

    def _remove_from_indexes(self, table_name, row, row_id):
        for col, val_map in self.indexes[table_name].items():
            val = row[self.tables[table_name]['column_index'][col]]
            if val in val_map and row_id in val_map[val]: val_map[val].remove(row_id)

    def _update_table_stats(self, table_name):
        if table_name.startswith('_'): return
        row_count = len(self.tables[table_name]['rows'])
        for row in self.tables['_system_tables']['rows'].values():
            if row[0] == table_name: row[2] = row_count; break

    def get_stats(self):
        return {**self.stats, 'uptime': f"{time.time()-self.stats['start_time']:.2f}s"}
