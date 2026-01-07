import sqlite3

# Connect to the REAL database
conn = sqlite3.connect('data/app.db')
cursor = conn.cursor()

# Check current columns
cursor.execute('PRAGMA table_info(foods)')
columns = cursor.fetchall()
print('Current columns in foods table:')
for col in columns:
    print(f'  - {col[1]} ({col[2]})')

# Check if ingredients_text exists
has_ingredients = any(col[1] == 'ingredients_text' for col in columns)

if not has_ingredients:
    print('\n❌ ingredients_text column missing!')
    print('Adding column...')
    cursor.execute('ALTER TABLE foods ADD COLUMN ingredients_text TEXT')
    conn.commit()
    print('✅ Column added!')
else:
    print('\n✅ ingredients_text column already exists!')

# Check if allergens_tags exists
has_tags = any(col[1] == 'allergens_tags' for col in columns)

if not has_tags:
    print('\n❌ allergens_tags column missing!')
    print('Adding column...')
    cursor.execute('ALTER TABLE foods ADD COLUMN allergens_tags TEXT')
    conn.commit()
    print('✅ allergens_tags column added!')
else:
    print('\n✅ allergens_tags column already exists!')

conn.close()
print('\n🎉 Database migration complete!')
