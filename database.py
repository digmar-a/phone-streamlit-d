import psycopg2
import pandas as pd
import streamlit as st
from datetime import datetime


# ============================
# DB CONNECTION
# ============================
def get_conn():
    return psycopg2.connect(st.secrets["DATABASE_URL"])


# ============================
# INITIALIZE DATABASE
# ============================
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS extracted_contacts (
            id SERIAL PRIMARY KEY,
            keyword TEXT,
            phone TEXT,
            source TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(keyword, phone)
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


# ============================
# INSERT NEW CONTACT
# ============================
def insert_contact(keyword, phone, source):
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO extracted_contacts (keyword, phone, source, created_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (keyword, phone) DO NOTHING
        """, (keyword, phone, source, datetime.now()))

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        # Optional: uncomment for debugging
        # print(e)
        pass


# ============================
# SEARCH CONTACTS
# ============================
def search_contacts(keyword="", phone="", source="", date_from=None, date_to=None):

    conn = get_conn()

    query = "SELECT * FROM extracted_contacts WHERE 1=1"
    params = []

    if keyword:
        query += " AND keyword ILIKE %s"
        params.append(f"%{keyword}%")

    if phone:
        query += " AND phone ILIKE %s"
        params.append(f"%{phone}%")

    if source:
        query += " AND source ILIKE %s"
        params.append(f"%{source}%")

    if date_from:
        query += " AND created_at::date >= %s"
        params.append(date_from)

    if date_to:
        query += " AND created_at::date <= %s"
        params.append(date_to)

    query += " ORDER BY created_at DESC"

    df = pd.read_sql(query, conn, params=params)

    conn.close()

    return df
