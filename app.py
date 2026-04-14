import streamlit as st
from services import csv_analysis
import pandas as pd
import uuid

# ---------------- CONFIG ---------------- #
st.set_page_config(page_title="Smart Analytics", layout="wide")
st.title("📊 Smart Analytics Platform")
st.markdown("Analyze SQL data or upload your own dataset")

mode = "Upload"

# ---------------- KPI DISPLAY ---------------- #
def display_kpis(kpis):
    cols = st.columns(len(kpis))
    for i, (key, value) in enumerate(kpis.items()):
        cols[i].metric(key, round(value, 2))

# =========================================================
# 🟢 DATABASE MODE
# =========================================================
# =========================================================
# 🟢 DATABASE MODE (FINAL)
# =========================================================
if mode == "Database":

    st.sidebar.header("📊 Analysis")

    option = st.sidebar.selectbox(
        "Select View",
        [
            "Overview",
            "Revenue",
            "Products",
            "Customers",
            "Category",
            "Profit"
        ]
    )

    # ---------------- OVERVIEW ---------------- #
    if option == "Overview":
        st.markdown("## 📌 Key Metrics")

        col1, col2 = st.columns(2)

        total = sql_analysis.total_revenue().iloc[0,0]
        avg = sql_analysis.avg_order_value().iloc[0,0]

        col1.metric("💰 Total Revenue", f"₹ {total}")
        col2.metric("🧾 Avg Order Value", f"₹ {avg}")

    # ---------------- REVENUE ---------------- #
    elif option == "Revenue":
        st.markdown("## 📈 Revenue Trends")

        col1, col2 = st.columns(2)

        df1 = sql_analysis.monthly_revenue()
        df2 = sql_analysis.daily_revenue()

        col1.line_chart(df1.set_index("Month"))
        col2.line_chart(df2.set_index("Date"))

        st.dataframe(df1)

    # ---------------- PRODUCTS ---------------- #
    elif option == "Products":
        st.markdown("## 🛍️ Product Insights")

        col1, col2 = st.columns(2)

        df1 = sql_analysis.top_products()
        df2 = sql_analysis.product_contribution()

        col1.bar_chart(df1.set_index("Product"))
        col2.bar_chart(df2.set_index("Product"))

        st.dataframe(df2)

    # ---------------- CUSTOMERS ---------------- #
    elif option == "Customers":
        st.markdown("## 👥 Customer Insights")

        df1 = sql_analysis.top_customers()
        df2 = sql_analysis.repeat_customers()

        st.bar_chart(df1.set_index("Customer"))

        st.write("### Repeat Customers")
        st.dataframe(df2)

    # ---------------- CATEGORY ---------------- #
    elif option == "Category":
        st.markdown("## 📦 Category Analysis")

        df = sql_analysis.category_sales()

        st.bar_chart(df.set_index("Category"))
        st.dataframe(df)

    # ---------------- PROFIT ---------------- #
    elif option == "Profit":
        st.markdown("## 💸 Profit Analysis")

        df = sql_analysis.profit_analysis()

        st.bar_chart(df.set_index("Product"))
        st.dataframe(df)


# =========================================================
# 🔵 UPLOAD MODE (FINAL STABLE)
# =========================================================
# =========================================================
# 🔵 UPLOAD MODE (GLOBAL CHART CONTROL)
# =========================================================
else:

    import matplotlib.pyplot as plt

    file = st.file_uploader("Upload CSV", type=["csv"])

    if file:

        try:
            with st.spinner("Processing..."):
                df = csv_analysis.load_data(file)
        except:
            st.error("Invalid file")
            st.stop()

        # ---------------- GLOBAL CHART SELECTOR ---------------- #
        st.markdown("## 📊 Chart Settings")

        chart_type = st.selectbox(
            "Select Chart Type",
            ["Line", "Bar", "Pie", "Histogram", "Scatter"],
            key="global_chart"
        )

        # ---------------- CHART FUNCTION ---------------- #
        def plot_chart(df, x_col, y_col):

            fig, ax = plt.subplots()

            if chart_type == "Line":
                ax.plot(df[x_col], df[y_col])

            elif chart_type == "Bar":
                ax.bar(df[x_col], df[y_col])

            elif chart_type == "Pie":
                ax.pie(df[y_col], labels=df[x_col], autopct="%1.1f%%")

            elif chart_type == "Histogram":
                ax.hist(df[y_col])

            elif chart_type == "Scatter":
                ax.scatter(df[x_col], df[y_col])

            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)

            st.pyplot(fig)

        tab1, tab2 = st.tabs(["📊 Dashboard", "📄 Data"])

        # ---------------- DASHBOARD ---------------- #
        with tab1:

            st.dataframe(df.head())

            numeric_cols, cat_cols, date_col = csv_analysis.detect_columns(df)

            st.markdown("### 🧠 Detected Columns")
            st.write("Numeric:", numeric_cols)
            st.write("Categorical:", cat_cols)
            st.write("Date:", date_col)

            # ---------------- KPI ---------------- #
            st.markdown("## 📌 KPIs")

            kpis = csv_analysis.get_kpis(df, numeric_cols)

            if kpis:
                display_kpis(kpis)
            else:
                st.warning("No numeric data found")

            # ---------------- TIME TREND ---------------- #
            # ---------------- TIME TREND ---------------- #
            if date_col and numeric_cols:

                st.markdown("## 📅 Time Trend")

                num_col = numeric_cols[0]

                ts = csv_analysis.time_series(df, date_col, num_col)

                if not ts.empty and date_col in ts.columns:

                    temp = ts.reset_index()

                    # 🔥 SAFE: ensure column exists
                    if num_col in temp.columns:
                        plot_chart(temp, date_col, num_col)
                    else:
                        st.warning(f"{num_col} not found after processing")

                else:
                    st.warning("Invalid time series data")

            else:
                st.info("No valid date column found")

            # ---------------- CATEGORY ---------------- #
            if cat_cols and numeric_cols:

                st.markdown("## 📊 Category Analysis")

                grouped = csv_analysis.group_analysis(df, cat_cols[0], numeric_cols[0])

                grouped_df = grouped.reset_index()

                plot_chart(grouped_df, grouped_df.columns[0], grouped_df.columns[1])

            else:
                st.info("No category data available")

            # ---------------- COLUMN ANALYSIS ---------------- #
            st.markdown("## 🔍 Column Analysis")

            col = df.columns[0]

            if pd.api.types.is_numeric_dtype(df[col]):

                temp_df = df[[col]].copy()
                temp_df["index"] = range(len(temp_df))

                plot_chart(temp_df, "index", col)

            else:
                value_counts = df[col].value_counts().reset_index()
                value_counts.columns = ["category", "count"]

                plot_chart(value_counts, "category", "count")

            # ---------------- FILTER ---------------- #
            if numeric_cols:

                st.markdown("## 🎯 Filter")

                col = numeric_cols[0]

                min_val = float(df[col].min())
                max_val = float(df[col].max())

                selected = st.slider(
                    f"Range for {col}",
                    min_val,
                    max_val,
                    (min_val, max_val),
                    key=f"slider_{col}_{min_val}_{max_val}"
                )

                filtered = csv_analysis.filter_data(df, col, selected[0], selected[1])

                st.dataframe(filtered)

        # ---------------- RAW DATA ---------------- #
        with tab2:
            st.dataframe(df)

        
        # ---------------- DASHBOARD ---------------- #
        with tab1:

            st.dataframe(df.head())

            info = csv_analysis.get_basic_info(df)
            numeric_cols, cat_cols, date_col = csv_analysis.detect_columns(df)

            # ---------------- KPI ---------------- #
            st.markdown("## 📌 KPIs")
            kpis = csv_analysis.get_kpis(df, numeric_cols)

            if kpis:
                display_kpis(kpis)
            else:
                st.warning("No numeric columns found for KPI")

            # ---------------- TIME TREND ---------------- #
            # ---------------- TIME TREND ---------------- #
            if date_col and numeric_cols:

                st.markdown("## 📅 Time Trend")

                num_col = numeric_cols[0]

                ts = csv_analysis.time_series(df, date_col, num_col)

                if not ts.empty and date_col in ts.columns:

                    temp = ts.reset_index()

                    # 🔥 SAFE CHECK
                    if num_col in temp.columns:
                        plot_chart(temp, date_col, num_col)
                    else:
                        st.warning(f"{num_col} not found after processing")

                else:
                    st.warning("Invalid time series data")

            else:
                st.info("No valid date column found")

                    

            # ---------------- CATEGORY ---------------- #
            if cat_cols and numeric_cols:

                st.markdown("## 📊 Category Analysis")

                col1, col2 = st.columns(2)

                cat = col1.selectbox("Category", cat_cols)
                num = col2.selectbox("Value", numeric_cols)

                grouped = csv_analysis.group_analysis(df, cat, num)

                st.bar_chart(grouped)

            # ---------------- COLUMN ---------------- #
            st.markdown("## 🔍 Column Analysis")

            col = st.selectbox("Column", df.columns)

            if pd.api.types.is_numeric_dtype(df[col]):
                st.line_chart(df[col])
            else:
                st.bar_chart(df[col].value_counts())

            # ---------------- FILTER ---------------- #
            if col in numeric_cols:

                st.markdown("## 🎯 Filter")

                min_val = float(df[col].min())
                max_val = float(df[col].max())

                selected = st.slider(
    f"Range for {col}",
    min_val,
    max_val,
    (min_val, max_val),
    key=f"slider_{col}_{uuid.uuid4()}"
)

                filtered = csv_analysis.filter_data(df, col, selected[0], selected[1])

                st.dataframe(filtered)

        # ---------------- RAW DATA ---------------- #
        with tab2:
            st.dataframe(df)

st.markdown("---")
st.markdown("🚀 Built with Python, SQL, Pandas & Streamlit")
