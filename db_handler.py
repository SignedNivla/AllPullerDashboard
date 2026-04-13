from sqlalchemy import create_engine, text
import pandas as pd

def get_engine(db_type, db_user, db_pass, db_host, db_port, db_name):
    """Membuat koneksi database menggunakan SQLAlchemy"""
    protocol = "postgresql" if db_type == "PostgreSQL" else "mysql+pymysql"
    conn_str = f"{protocol}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(conn_str)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return engine

def push_to_sql(df, engine, table_name):
    """Mengirim data ke tabel yang dipilih"""
    df.to_sql(table_name, con=engine, if_exists='append', index=False)