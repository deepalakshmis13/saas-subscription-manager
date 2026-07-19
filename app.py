import streamlit as st
import sqlite3
import pandas as pd

# ---------- DB ----------
def get_connection():
    return sqlite3.connect("saas.db", check_same_thread=False)

conn = get_connection()
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price REAL,
    features TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    plan_id INTEGER,
    status TEXT
)""")

conn.commit()

# ---------- UI ----------
st.title("💳 SaaS Subscription Manager")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Plans", "Users", "Billing"])

# ---------- DASHBOARD ----------
if menu == "Dashboard":
    st.header("📊 Overview")
    users = pd.read_sql("SELECT * FROM users", conn)
    plans = pd.read_sql("SELECT * FROM plans", conn)

    st.metric("Total Users", len(users))
    st.metric("Total Plans", len(plans))

# ---------- PLANS ----------
elif menu == "Plans":
    st.header("📦 Plans")

    name = st.text_input("Plan Name")
    price = st.number_input("Price")
    features = st.text_area("Features")

    if st.button("Add Plan"):
        conn.execute("INSERT INTO plans (name, price, features) VALUES (?, ?, ?)",
                     (name, price, features))
        conn.commit()
        st.success("Plan Added!")

    df = pd.read_sql("SELECT * FROM plans", conn)
    st.dataframe(df)

# ---------- USERS ----------
elif menu == "Users":
    st.header("👤 Users")

    plans = pd.read_sql("SELECT * FROM plans", conn)

    name = st.text_input("Name")
    email = st.text_input("Email")

    if not plans.empty:
        plan_id = st.selectbox("Plan", plans["id"])
    else:
        st.warning("Create a plan first")
        plan_id = None

    if st.button("Add User") and plan_id:
        conn.execute(
            "INSERT INTO users (name, email, plan_id, status) VALUES (?, ?, ?, ?)",
            (name, email, plan_id, "Active")
        )
        conn.commit()
        st.success("User Added!")

    df = pd.read_sql("SELECT * FROM users", conn)
    st.dataframe(df)

# ---------- BILLING ----------
elif menu == "Billing":
    st.header("💰 Billing")

    df = pd.read_sql("""
        SELECT users.name, users.email, plans.price
        FROM users
        JOIN plans ON users.plan_id = plans.id
    """, conn)

    if not df.empty:
        df["invoice"] = df["price"]
        st.dataframe(df)
        st.metric("Total Revenue", f"₹{df['invoice'].sum()}")
