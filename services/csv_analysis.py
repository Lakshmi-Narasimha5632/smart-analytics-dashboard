import pandas as pd

# ---------------- LOAD DATA ---------------- #
def load_data(file):
    df = pd.read_csv(file)

    # normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # 🔥 remove 'index' column if exists
    df = df.loc[:, ~df.columns.str.contains("^index$")]

    # 🔥 remove duplicate columns
    df = df.loc[:, ~df.columns.duplicated(keep='first')]

    return df


# ---------------- BASIC INFO ---------------- #
def get_basic_info(df):
    return {
        "rows": df.shape[0],
        "cols": df.shape[1],
        "columns": df.columns.tolist()
    }


# ---------------- DETECT COLUMNS ---------------- #
def detect_columns(df):

    numeric = df.select_dtypes(include=["number"]).columns.tolist()
    categorical = df.select_dtypes(include=["object"]).columns.tolist()

    date_col = None

    for col in df.columns:
        try:
            parsed = pd.to_datetime(df[col], errors='coerce')

            if parsed.notna().sum() > len(df) * 0.3:
                date_col = col
                break
        except:
            continue

    return numeric, categorical, date_col


# ---------------- KPI ---------------- #
def get_kpis(df, numeric_cols):
    kpis = {}

    for col in numeric_cols[:3]:
        if pd.api.types.is_numeric_dtype(df[col]):
            kpis[col] = df[col].sum()

    return kpis


# ---------------- GROUP ---------------- #
def group_analysis(df, cat_col, num_col):
    if cat_col not in df.columns or num_col not in df.columns:
        return pd.Series()

    return df.groupby(cat_col)[num_col].sum().sort_values(ascending=False)


# ---------------- TIME SERIES ---------------- #
def time_series(df, date_col, num_col):

    if date_col not in df.columns or num_col not in df.columns:
        return pd.DataFrame()

    df = df.copy()

    # 🔥 remove duplicate columns again (safety)
    df = df.loc[:, ~df.columns.duplicated()]

    # remove index column if exists
    if "index" in df.columns:
        df = df.drop(columns=["index"])

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    df = df.dropna(subset=[date_col])

    if df.empty:
        return df

    df = df[[date_col, num_col]]

    df = df.loc[:, ~df.columns.duplicated()]

    df = df.sort_values(by=date_col)

    return df


# ---------------- FILTER ---------------- #
def filter_data(df, col, min_val, max_val):
    if col not in df.columns:
        return df

    return df[(df[col] >= min_val) & (df[col] <= max_val)]