
---

# 🚀 Lightweight In-Memory DB (Python)

### *Version 1.1 - Optimized for Google Colab*

`LightweightDB` is a high-performance, in-memory relational database simulation designed for educational purposes and lightweight data tasks in Google Colab. It bridges the gap between simple Python dictionaries and heavy SQL engines like SQLite.

## ✨ Key Features

* **Hash-Map Indexing:** Optimized lookups from  to  for indexed columns.
* **System Tables:** Metadata management via internal `_system_tables` and `_system_indexes`.
* **Primary Key Support:** Instant uniqueness validation using internal PK mapping.
* **JSON Persistence:** Easy export/import to save your session data.
* **SQL-ish Querying:** Basic string-based query support for a familiar feel.

---

## 🛠️ Quick Start

### 1. Initialize and Create Tables

```python
db = LightweightDB(name="ColabStore")

# Create a table with a Primary Key
db.create_table('users', ['id', 'name', 'email', 'city'], primary_key='id')

# Create an index for high-speed 'city' lookups
db.create_index('users', 'city')

```

### 2. CRUD Operations

```python
# Create
db.insert('users', {'id': 1, 'name': 'Alice', 'city': 'Kyoto'})

# Read (uses the City index automatically)
results = db.select('users', where={'city': 'Kyoto'})

# Update
db.update('users', {'name': 'Alice Smith'}, where={'id': 1})

# Delete
db.delete('users', where={'id': 1})

```

---

## 📈 Performance: Why This Version?

In standard Python lists, finding a specific record requires checking every single item (a "Full Table Scan"). In this optimized version, we use **Hash Maps** (Python Dictionaries) to point directly to the data location.

| Feature | Original Implementation | Optimized Implementation | Impact |
| --- | --- | --- | --- |
| **Row Storage** | List `[]` | Dictionary `{row_id: row}` | Faster deletions/updates. |
| **Search** |  (Linear) |  (Constant) | Instant lookups on indexed cols. |
| **PK Validation** | Loop through all rows | Direct Map lookup | Prevent duplicates instantly. |
| **Deletions** | Requires full re-index | Targeted index removal | High-speed data cleanup. |

---

## 🔍 API Reference

| Method | Description |
| --- | --- |
| `create_table(name, cols, pk)` | Initializes a new table schema and adds it to system metadata. |
| `insert(table, data)` | Adds a row. Validates PK and updates all relevant indexes. |
| `select(table, cols, where, limit)` | Retrieves data. Automatically selects the best index to use. |
| `create_index(table, col)` | Builds a hash-map for a specific column to speed up queries. |
| `get_stats()` | Returns database health, memory usage, and operation counts. |
| `export_to_json(file)` | Serializes user tables to a local JSON file. |

---




