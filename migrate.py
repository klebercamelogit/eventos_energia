import sqlite3
import os

db_path = 'energisa.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verifica colunas existentes
    cursor.execute("PRAGMA table_info(events)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'location' not in columns:
        cursor.execute("ALTER TABLE events ADD COLUMN location VARCHAR(100)")
        print("➕ Coluna 'location' adicionada.")
    if 'country' not in columns:
        cursor.execute("ALTER TABLE events ADD COLUMN country VARCHAR(100)")
        print("➕ Coluna 'country' adicionada.")
    if 'source' not in columns:
        cursor.execute("ALTER TABLE events ADD COLUMN source VARCHAR(20) DEFAULT 'manual'")
        print("➕ Coluna 'source' adicionada.")
    if 'source_url' not in columns:
        cursor.execute("ALTER TABLE events ADD COLUMN source_url VARCHAR(500)")
        print("➕ Coluna 'source_url' adicionada.")
    if 'updated_at' not in columns:
        cursor.execute("ALTER TABLE events ADD COLUMN updated_at DATETIME")
        print("➕ Coluna 'updated_at' adicionada.")

    # Colunas de usuários (troca de senha obrigatória + perfil admin/usuário)
    cursor.execute("PRAGMA table_info(users)")
    user_columns = [col[1] for col in cursor.fetchall()]
    if 'must_change_password' not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN must_change_password BOOLEAN DEFAULT 0")
        print("➕ Coluna 'must_change_password' adicionada.")
    if 'role' not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'")
        print("➕ Coluna 'role' adicionada.")

    # Colunas de evidência em inscrições de palestra (só migra se a tabela já existir)
    cursor.execute("PRAGMA table_info(talk_registrations)")
    talk_reg_columns = [col[1] for col in cursor.fetchall()]
    if talk_reg_columns:
        if 'evidence_path' not in talk_reg_columns:
            cursor.execute("ALTER TABLE talk_registrations ADD COLUMN evidence_path VARCHAR(300)")
            print("➕ Coluna 'evidence_path' adicionada.")
        if 'evidence_uploaded_by' not in talk_reg_columns:
            cursor.execute("ALTER TABLE talk_registrations ADD COLUMN evidence_uploaded_by INTEGER")
            print("➕ Coluna 'evidence_uploaded_by' adicionada.")

    # Coluna de hotel em inscrições de evento
    cursor.execute("PRAGMA table_info(registrations)")
    reg_columns = [col[1] for col in cursor.fetchall()]
    if reg_columns and 'hotel_name' not in reg_columns:
        cursor.execute("ALTER TABLE registrations ADD COLUMN hotel_name VARCHAR(200)")
        print("➕ Coluna 'hotel_name' adicionada.")

    conn.commit()
    conn.close()
    print("✅ Migração concluída.")
    print("ℹ️ Lembrete: essa migração só serve pro SQLite local — o app_eventos.py já faz")
    print("   essas mesmas migrações sozinho ao iniciar, inclusive contra o Turso em produção.")
else:
    print("❌ Banco de dados não encontrado.")