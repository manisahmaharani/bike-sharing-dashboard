from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).parent

C_KERJA, C_LIBUR = "#1f4e79", "#e69f00"
C_CASUAL, C_REG = "#2a9d8f", "#6a4c93"
DAY_COLORS = {"Hari Kerja": C_KERJA, "Hari Libur / Akhir Pekan": C_LIBUR}
WEATHER_ORDER = ["Cerah", "Berkabut", "Hujan/Salju"]
SLOT_ORDER = ["Dini Hari (00-05)", "Pagi (06-09)", "Siang (10-15)",
              "Sore (16-19)", "Malam (20-23)"]

st.set_page_config(page_title="Dashboard Bike Sharing", page_icon="🚲", layout="wide")


@st.cache_data
def load_data():
    day = pd.read_csv(BASE_DIR / "main_data.csv", parse_dates=["dteday"])
    hour = pd.read_csv(BASE_DIR / "hour_data.csv", parse_dates=["dteday"])
    return day, hour


day_df, hour_df = load_data()

# ---------------- Sidebar ----------------
st.sidebar.title("🚲 Filter")
year_choice = st.sidebar.selectbox("Tahun (Pertanyaan 1)", ["2012", "2011", "2011-2012"])

min_date, max_date = day_df["dteday"].min().date(), day_df["dteday"].max().date()
date_range = st.sidebar.date_input("Rentang tanggal (Pertanyaan 2)",
                                   value=(min_date, max_date),
                                   min_value=min_date, max_value=max_date)
if len(date_range) != 2:
    st.info("Pilih tanggal akhir pada filter rentang tanggal.")
    st.stop()
start_date, end_date = date_range

st.sidebar.caption("Data: Capital Bikeshare, Washington D.C. (2011-2012)")

# ---------------- Data terfilter ----------------
hour_q1 = hour_df if year_choice == "2011-2012" else hour_df[hour_df["tahun"] == int(year_choice)]
day_q2 = day_df[(day_df["dteday"].dt.date >= start_date) & (day_df["dteday"].dt.date <= end_date)]

st.title("Dashboard Analisis Bike Sharing")
st.caption("Pertanyaan 1: jam sibuk hari kerja vs hari libur. Pertanyaan 2: proporsi pengguna casual vs registered menurut cuaca.")

# ---------------- KPI ----------------
total_rent = int(day_q2["cnt"].sum())
pct_casual = day_q2["casual"].sum() / total_rent * 100 if total_rent else 0
col1, col2, col3 = st.columns(3)
col1.metric("Total penyewaan (rentang terpilih)", f"{total_rent:,}")
col2.metric("Porsi pengguna casual", f"{pct_casual:.1f}%")
col3.metric("Jumlah hari (rentang terpilih)", f"{len(day_q2):,}")

tab1, tab2 = st.tabs(["Pertanyaan 1: Jam Sibuk", "Pertanyaan 2: Cuaca & Tipe Pengguna"])

# ---------------- Tab 1 ----------------
with tab1:
    st.subheader(f"Rata-rata penyewaan per jam ({year_choice})")
    hourly = hour_q1.groupby(["day_type", "hr"])["cnt"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(10, 4.5))
    for tipe, color in DAY_COLORS.items():
        grp = hourly[hourly["day_type"] == tipe]
        if grp.empty:
            continue
        ax.plot(grp["hr"], grp["cnt"], marker="o", linewidth=2.2, color=color, label=tipe)
        top = grp.loc[grp["cnt"].idxmax()]
        ax.annotate(f"{int(top['hr']):02d}:00 ({top['cnt']:.0f})",
                    xy=(top["hr"], top["cnt"]), xytext=(0, 10),
                    textcoords="offset points", ha="center",
                    color=color, fontweight="bold")
    ax.set_xticks(range(24))
    ax.set_ylim(0, hourly["cnt"].max() * 1.2)
    ax.set_xlabel("Jam (0-23)")
    ax.set_ylabel("Rata-rata penyewaan per jam")
    ax.legend(title="Tipe hari")
    st.pyplot(fig)

    peak = hourly.sort_values("cnt", ascending=False).groupby("day_type").head(3)
    cols = st.columns(2)
    for col, tipe in zip(cols, DAY_COLORS):
        rows = peak[peak["day_type"] == tipe].sort_values("cnt", ascending=False)
        jam = ", ".join(f"{int(h):02d}:00" for h in rows["hr"])
        col.markdown(f"**{tipe}** - 3 jam tersibuk: {jam}")

    st.subheader("Persentase penyewaan per segmen waktu")
    slot_total = hour_q1.groupby(["day_type", "time_slot"])["cnt"].sum().unstack()
    slot_share = slot_total.div(slot_total.sum(axis=1), axis=0).mul(100)
    slot_share = slot_share.reindex(columns=SLOT_ORDER).reindex(list(DAY_COLORS)).dropna(how="all")

    fig, ax = plt.subplots(figsize=(10, 4))
    pos = np.arange(len(SLOT_ORDER))
    width = 0.38
    for k, tipe in enumerate(slot_share.index):
        bars = ax.bar(pos + (k - 0.5) * width, slot_share.loc[tipe], width,
                      color=DAY_COLORS[tipe], label=tipe)
        ax.bar_label(bars, fmt="%.1f%%", padding=3)
    ax.set_xticks(pos)
    ax.set_xticklabels([s.replace(" (", "\n(") for s in SLOT_ORDER])
    ax.set_ylim(0, slot_share.values.max() * 1.15)
    ax.set_ylabel("Persentase penyewaan (%)")
    ax.legend(title="Tipe hari")
    st.pyplot(fig)

# ---------------- Tab 2 ----------------
with tab2:
    st.subheader(f"Pengguna casual vs registered menurut cuaca ({start_date} s.d. {end_date})")
    if day_q2.empty:
        st.warning("Tidak ada data pada rentang tanggal tersebut.")
    else:
        summary = day_q2.groupby("weather_label").agg(
            jumlah_hari=("cnt", "size"),
            total_casual=("casual", "sum"),
            total_registered=("registered", "sum"),
            rata2_casual=("casual", "mean"),
            rata2_registered=("registered", "mean"),
        ).reindex(WEATHER_ORDER).dropna(subset=["jumlah_hari"])
        summary["persen_casual"] = summary["total_casual"] / (summary["total_casual"] + summary["total_registered"]) * 100
        summary["persen_registered"] = 100 - summary["persen_casual"]

        ytick = [f"{w}\n({int(n)} hari)" for w, n in zip(summary.index, summary["jumlah_hari"])]
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.8))

        ax1.barh(ytick, summary["persen_casual"], color=C_CASUAL, label="Casual")
        ax1.barh(ytick, summary["persen_registered"], left=summary["persen_casual"],
                 color=C_REG, label="Registered")
        for i, (pc, pr) in enumerate(zip(summary["persen_casual"], summary["persen_registered"])):
            ax1.text(pc / 2, i, f"{pc:.1f}%", ha="center", va="center", color="white", fontweight="bold")
            ax1.text(pc + pr / 2, i, f"{pr:.1f}%", ha="center", va="center", color="white", fontweight="bold")
        ax1.set_xlim(0, 100)
        ax1.invert_yaxis()
        ax1.set_xlabel("Persentase dari total penyewaan (%)")
        ax1.set_title("Proporsi pengguna")
        ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2)

        pos = np.arange(len(summary))
        width = 0.38
        b1 = ax2.bar(pos - width / 2, summary["rata2_casual"], width, color=C_CASUAL, label="Casual")
        b2 = ax2.bar(pos + width / 2, summary["rata2_registered"], width, color=C_REG, label="Registered")
        ax2.bar_label(b1, fmt="%.0f", padding=3)
        ax2.bar_label(b2, fmt="%.0f", padding=3)
        ax2.set_xticks(pos)
        ax2.set_xticklabels(summary.index)
        ax2.set_ylim(0, summary["rata2_registered"].max() * 1.15)
        ax2.set_ylabel("Rata-rata penyewaan per hari")
        ax2.set_title("Rata-rata penyewaan harian")
        ax2.legend(title="Jenis pengguna")
        plt.tight_layout()
        st.pyplot(fig)

        if (summary["jumlah_hari"] < 30).any():
            st.caption("Catatan: ada kategori cuaca dengan kurang dari 30 hari pada rentang ini, jadi angkanya kurang stabil.")
        st.dataframe(summary.round(1))
