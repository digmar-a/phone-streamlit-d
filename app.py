import streamlit as st
import pandas as pd
import io
from datetime import date

from database import init_db, insert_contact, search_contacts
from scraper import search_and_extract

# ============================
# INITIALIZE DATABASE
# ============================
init_db()

st.set_page_config(
    page_title="Phone & WhatsApp Extractor — ANVIA",
    layout="wide"
)

# ============================
# SIDEBAR NAVIGATION
# ============================
st.sidebar.title("📂 Navigation")
page = st.sidebar.radio(
    "Select Option",
    ["🔍 Extract Numbers", "🗄 View Database"]
)

# ============================
# 🔍 EXTRACT NUMBERS PAGE
# ============================
if page == "🔍 Extract Numbers":

    st.title("📞 Phone & WhatsApp Extractor — ANVIA")

    uploaded = st.file_uploader(
        "📂 Upload Excel (.xlsx) with **keyword** column",
        type=["xlsx"]
    )

    if uploaded is not None:
        df = pd.read_excel(uploaded)

        if "keyword" not in df.columns:
            st.error("❌ Excel must contain a column named **keyword**")
        else:
            st.success("✔ File loaded successfully")

            if st.button("🚀 Start Extraction"):
                progress = st.progress(0)
                all_results = []

                keywords = df["keyword"].dropna().tolist()
                total = len(keywords)

                for i, keyword in enumerate(keywords):
                    st.write(f"🔍 Searching: **{keyword}**")

                    extracted = search_and_extract(keyword)

                    if not extracted:
                        st.info("No valid numbers found for this keyword")

                    for phone, source in extracted:
                        insert_contact(keyword, phone, source)

                        all_results.append({
                            "keyword": keyword,
                            "phone": phone,
                            "source": source
                        })

                    progress.progress((i + 1) / total)

                if all_results:
                    out_df = pd.DataFrame(all_results)
                    st.subheader("✅ Extracted Results")
                    st.dataframe(out_df, use_container_width=True)

                    buffer = io.BytesIO()
                    out_df.to_excel(buffer, index=False)
                    buffer.seek(0)

                    st.download_button(
                        label="📥 Download Extracted Data (Excel)",
                        data=buffer,
                        file_name="extracted_numbers.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.warning("❌ No phone or WhatsApp numbers found")

# ============================
# 🗄 VIEW DATABASE PAGE
# ============================
if page == "🗄 View Database":

    st.title("🗄 Search Stored Database")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        keyword = st.text_input("🔎 Search by Keyword")

    with col2:
        date_from = st.date_input("📅 From Date", value=date.today())

    with col3:
        date_to = st.date_input("📅 To Date", value=date.today())

    with col4:
        source = st.text_input("🔎 Search by Source")

    if st.button("🔍 Search Database"):
        df = search_contacts(
            keyword=keyword,
            source=source,
            date_from=str(date_from),
            date_to=str(date_to)
        )

        if df.empty:
            st.warning("❌ No data found")
        else:
            st.success(f"✔ Found {len(df)} records")

            df_display = df[["id", "keyword", "phone", "source", "created_at"]]
            st.dataframe(df_display, use_container_width=True)

            buffer = io.BytesIO()
            df_display.to_excel(buffer, index=False)
            buffer.seek(0)

            st.download_button(
                label="📥 Download Filtered Data (Excel)",
                data=buffer,
                file_name="filtered_database.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
