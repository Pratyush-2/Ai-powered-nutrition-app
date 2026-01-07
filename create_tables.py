from app.database import engine, Base
from app import models

print('Creating all tables...')
Base.metadata.create_all(bind=engine)
print('✅ Tables created!')

import sqlite3
conn = sqlite3.connect('nutrition.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(foods)')
cols = cursor.fetchall()
print('\nColumns in foods table:')
for col in cols:
    print(f'  - {col[1]} ({col[2]})')
conn.close()
