import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import plotly.express as px

# ==================================================
# 1. KONFIGURASI HALAMAN
# ==================================================

st.set_page_config(
    page_title="Analisis Wisata Bandung",
    layout="wide"
)

# ==================================================
# 2. LOAD DATA
# ==================================================

df_awal = pd.read_csv("dataset/final dataset wisata bandung.csv")

jumlah_data_awal = len(df_awal)
missing_value_awal = int(df_awal.isnull().sum().sum())
duplikat_awal = int(df_awal.duplicated().sum())

# ==================================================
# 3. PILIH ATRIBUT
# ==================================================

atribut = [
    "Nama Tempat",
    "Kategori Tempat",
    "Rating Tempat",
    "Harga Masuk",
    "User Rating",
    "Wilayah"
]

df = df_awal[atribut].copy()

# ==================================================
# 4. PEMBERSIHAN FORMAT DATA
# ==================================================

df["Nama Tempat"] = df["Nama Tempat"].astype(str).str.strip()
df["Kategori Tempat"] = df["Kategori Tempat"].astype(str).str.strip().str.title()
df["Wilayah"] = df["Wilayah"].astype(str).str.strip()

kolom_numerik = ["Rating Tempat", "Harga Masuk", "User Rating"]

for kolom in kolom_numerik:
    df[kolom] = pd.to_numeric(df[kolom], errors="coerce")

# ==================================================
# 5. STANDARDISASI NAMA TEMPAT
# ==================================================

jumlah_sebelum_standar = len(df)
nama_sebelum = df["Nama Tempat"].copy()

df["Nama Tempat"] = df["Nama Tempat"].replace({
    "Museum Gedung Sate": "Gedung Sate",
    "Taman Hutan Raya Ir. H. Juanda": "Taman Hutan Raya Ir. H. Djuanda"
})

jumlah_nama_diubah = int((nama_sebelum != df["Nama Tempat"]).sum())

# ==================================================
# 6. HAPUS DUPLIKAT SETELAH STANDARDISASI
# ==================================================

duplikat_setelah_standar = df[df.duplicated(subset=["Nama Tempat"], keep=False)].copy()

df = (
    df.sort_values(
        by=["Nama Tempat", "User Rating", "Rating Tempat"],
        ascending=[True, False, False]
    )
    .drop_duplicates(subset=["Nama Tempat"], keep="first")
    .reset_index(drop=True)
)

jumlah_data_setelah_standar = len(df)
jumlah_data_dihapus = jumlah_sebelum_standar - jumlah_data_setelah_standar
persentase_data_dihapus = (jumlah_data_dihapus / jumlah_sebelum_standar) * 100

# ==================================================
# 7. PENANGANAN MISSING VALUE
# ==================================================

data_bermasalah = df[df[atribut].isnull().any(axis=1)]
jumlah_data_bermasalah = len(data_bermasalah)

df["Nama Tempat"] = df["Nama Tempat"].fillna("Tidak Diketahui")
df["Kategori Tempat"] = df["Kategori Tempat"].fillna("Tidak Diketahui")
df["Rating Tempat"] = df["Rating Tempat"].fillna(df["Rating Tempat"].mean())
df["Harga Masuk"] = df["Harga Masuk"].fillna(0)
df["User Rating"] = df["User Rating"].fillna(0)
df["Wilayah"] = df["Wilayah"].fillna("Tidak Diketahui")

jumlah_data_bersih = len(df)
missing_value_bersih = int(df.isnull().sum().sum())
duplikat_bersih = int(df.duplicated(subset=["Nama Tempat"]).sum())

df_sebelum_normalisasi = df[atribut].copy()

# ==================================================
# 8. NORMALISASI MIN-MAX
# ==================================================

scaler = MinMaxScaler()

df[["RatingNorm", "ReviewNorm", "TicketNorm"]] = scaler.fit_transform(
    df[["Rating Tempat", "User Rating", "Harga Masuk"]]
)

df["TicketScore"] = 1 - df["TicketNorm"]

# ==================================================
# 9. HITUNG SKOR POPULARITAS
# ==================================================

df["Skor Popularitas"] = (
    0.5 * df["RatingNorm"] +
    0.3 * df["ReviewNorm"] +
    0.2 * df["TicketScore"]
)

# ==================================================
# 10. ABC ANALYSIS
# ==================================================

df = df.sort_values(by="Skor Popularitas", ascending=False).reset_index(drop=True)

total_pop = df["Skor Popularitas"].sum()

df["Persentase Kontribusi (%)"] = (df["Skor Popularitas"] / total_pop) * 100
df["Persentase Kumulatif (%)"] = df["Persentase Kontribusi (%)"].cumsum()

def klasifikasi_abc(nilai):
    if nilai <= 80:
        return "A"
    elif nilai <= 95:
        return "B"
    else:
        return "C"

df["Klasifikasi ABC"] = df["Persentase Kumulatif (%)"].apply(klasifikasi_abc)

df.insert(0, "Urutan Popularitas", range(1, len(df) + 1))

# ==================================================
# 11. HEADER
# ==================================================

st.title("📍 Analisis Tempat Wisata Bandung")
st.write("ABC Analysis Berdasarkan Rating, Jumlah Ulasan, dan Budget Pengunjung")

# ==================================================
# 12. SIDEBAR
# ==================================================

st.sidebar.title("Navigasi")

menu = st.sidebar.radio(
    "Pilih Halaman",
    ["Dashboard", "Preprocessing", "Hasil ABC Analysis"]
)

st.sidebar.markdown("---")
st.sidebar.header("Filter Rekomendasi Wisata")

budget = st.sidebar.slider(
    "Budget Maksimal",
    min_value=0,
    max_value=int(df["Harga Masuk"].max()),
    value=50000,
    step=5000
)

kategori = st.sidebar.selectbox(
    "Kategori Wisata",
    ["Semua"] + sorted(df["Kategori Tempat"].unique())
)

# ==================================================
# 13. FILTER REKOMENDASI
# ==================================================

rekomendasi = df[
    (df["Harga Masuk"] <= budget) &
    (df["Klasifikasi ABC"] == "A")
]

if kategori != "Semua":
    rekomendasi = rekomendasi[rekomendasi["Kategori Tempat"] == kategori]

# ==================================================
# 14. DASHBOARD
# ==================================================

if menu == "Dashboard":

    st.header("📊 Dashboard Analisis Wisata")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Data", len(df))
    col2.metric("Kategori A", len(df[df["Klasifikasi ABC"] == "A"]))
    col3.metric("Kategori B", len(df[df["Klasifikasi ABC"] == "B"]))
    col4.metric("Kategori C", len(df[df["Klasifikasi ABC"] == "C"]))

    st.markdown("---")

    st.subheader("Distribusi Klasifikasi ABC")

    label_map = {
        "A": "A (Paling Populer)",
        "B": "B (Cukup Populer)",
        "C": "C (Kurang Populer)"
    }

    abc_count = (
        df.groupby("Klasifikasi ABC")
        .size()
        .reset_index(name="Jumlah")
    )

    abc_count["Klasifikasi ABC Label"] = abc_count["Klasifikasi ABC"].map(label_map)

    fig1 = px.bar(
        abc_count,
        x="Klasifikasi ABC Label",
        y="Jumlah",
        color="Klasifikasi ABC Label",
        text="Jumlah",
        color_discrete_map={
            "A (Paling Populer)": "#2056a7",
            "B (Cukup Populer)": "#70ab0b",
            "C (Kurang Populer)": "#bc4a19"
        }
    )

    fig1.update_traces(textposition="outside")
    fig1.update_layout(xaxis_title="Klasifikasi ABC", yaxis_title="Jumlah")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Distribusi Kategori Wisata")

    kategori_count = (
        df.groupby("Kategori Tempat")
        .size()
        .reset_index(name="Jumlah")
        .sort_values(by="Jumlah", ascending=False)
    )

    fig_kategori = px.bar(
        kategori_count,
        x="Kategori Tempat",
        y="Jumlah",
        text="Jumlah",
        color="Kategori Tempat"
    )

    fig_kategori.update_traces(textposition="outside")
    fig_kategori.update_layout(
        xaxis_title="Kategori Wisata",
        yaxis_title="Jumlah Tempat Wisata"
    )

    st.plotly_chart(fig_kategori, use_container_width=True)

    st.subheader("Distribusi Klasifikasi ABC Berdasarkan Wilayah")

    wilayah_abc = (
        df.groupby(["Wilayah", "Klasifikasi ABC"])
        .size()
        .reset_index(name="Jumlah")
    )

    fig_wilayah_abc = px.bar(
        wilayah_abc,
        x="Wilayah",
        y="Jumlah",
        color="Klasifikasi ABC",
        text="Jumlah",
        barmode="group"
    )

    fig_wilayah_abc.update_traces(textposition="outside")
    fig_wilayah_abc.update_layout(
        xaxis_title="Wilayah",
        yaxis_title="Jumlah Tempat Wisata"
    )

    st.plotly_chart(fig_wilayah_abc, use_container_width=True)

    st.subheader("Distribusi Wisata Kategori A Berdasarkan Wilayah")

    wilayah_a = (
        df[df["Klasifikasi ABC"] == "A"]
        .groupby("Wilayah")
        .size()
        .reset_index(name="Jumlah")
        .sort_values(by="Jumlah", ascending=False)
    )

    fig_wilayah_a = px.bar(
        wilayah_a,
        x="Wilayah",
        y="Jumlah",
        text="Jumlah",
        color="Wilayah"
    )

    fig_wilayah_a.update_traces(textposition="outside")
    fig_wilayah_a.update_layout(
        xaxis_title="Wilayah",
        yaxis_title="Jumlah Wisata Kategori A",
        showlegend=False
    )

    st.plotly_chart(fig_wilayah_a, use_container_width=True)

    st.subheader("Distribusi Wisata Kategori A Berdasarkan Jenis Wisata")

    kategori_a = df[df["Klasifikasi ABC"] == "A"]

    kategori_a_count = (
        kategori_a.groupby("Kategori Tempat")
        .size()
        .reset_index(name="Jumlah")
        .sort_values(by="Jumlah", ascending=False)
    )

    fig_kategori_a = px.bar(
        kategori_a_count,
        x="Kategori Tempat",
        y="Jumlah",
        text="Jumlah",
        color="Kategori Tempat"
    )

    fig_kategori_a.update_traces(textposition="outside")
    fig_kategori_a.update_layout(
        xaxis_title="Kategori Wisata",
        yaxis_title="Jumlah Wisata Kategori A"
    )

    st.plotly_chart(fig_kategori_a, use_container_width=True)

    st.subheader("Top 10 Tempat Wisata Berdasarkan Skor Popularitas")

    top10 = df.head(10)

    fig2 = px.bar(
        top10,
        x="Nama Tempat",
        y="Skor Popularitas",
        text="Skor Popularitas"
    )

    fig2.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig2.update_layout(
        xaxis_title="Nama Tempat Wisata",
        yaxis_title="Skor Popularitas"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Rekomendasi Wisata Berdasarkan Budget dan Kategori")

    st.write(f"Budget maksimal yang dipilih: **Rp{budget:,.0f}**")

    st.dataframe(
        rekomendasi[
            [
                "Urutan Popularitas",
                "Nama Tempat",
                "Kategori Tempat",
                "Rating Tempat",
                "Harga Masuk",
                "Klasifikasi ABC"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

# ==================================================
# 15. PREPROCESSING
# ==================================================

elif menu == "Preprocessing":

    st.header("⚙️ Preprocessing Data")

    col1, col2, col3 = st.columns(3)

    col1.metric("Data Awal", jumlah_data_awal)
    col2.metric("Missing Value Awal", missing_value_awal)
    col3.metric("Duplikat Awal", duplikat_awal)

    col4, col5, col6 = st.columns(3)

    col4.metric("Data Setelah Preprocessing", jumlah_data_bersih)
    col5.metric("Missing Value Setelah", missing_value_bersih)
    col6.metric("Duplikat Setelah", duplikat_bersih)

    col7, col8, col9 = st.columns(3)

    col7.metric("Nama Distandardisasi", jumlah_nama_diubah)
    col8.metric("Data Digabung/Dihapus", jumlah_data_dihapus)
    col9.metric("Persentase Data Digabung", f"{persentase_data_dihapus:.2f}%")

    st.markdown("---")

    st.subheader("Tahapan Preprocessing")

    st.markdown("""
    1. Memilih atribut yang digunakan, yaitu **Nama Tempat**, **Kategori Tempat**, **Rating Tempat**, **Harga Masuk**, **User Rating**, dan **Wilayah**.
    2. Mengecek missing value dan data duplikat.
    3. Mengubah atribut numerik menjadi tipe data yang sesuai.
    4. Melakukan standardisasi nama destinasi wisata.
    5. Menghapus data ganda setelah standardisasi.
    6. Menangani data kosong jika ditemukan.
    7. Melakukan normalisasi menggunakan metode **Min-Max Normalization**.
    8. Menghitung **Ticket Score**.
    9. Menghitung **Skor Popularitas** sebagai dasar ABC Analysis.
    """)

    st.subheader("Data yang Terindikasi Ganda Setelah Standardisasi")

    if len(duplikat_setelah_standar) > 0:
        st.dataframe(
            duplikat_setelah_standar,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Tidak ditemukan data ganda setelah standardisasi.")

    st.subheader("Data Sebelum Normalisasi")

    st.dataframe(
        df_sebelum_normalisasi.head(15),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Data Setelah Normalisasi")

    st.dataframe(
        df[
            [
                "Urutan Popularitas",
                "Nama Tempat",
                "RatingNorm",
                "ReviewNorm",
                "TicketNorm",
                "TicketScore",
                "Skor Popularitas"
            ]
        ].head(15),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Rumus yang Digunakan")

    st.latex(r"X_{norm} = \frac{X - X_{min}}{X_{max} - X_{min}}")
    st.latex(r"TicketScore = 1 - TicketNorm")
    st.latex(
        r"Skor\ Popularitas = (0.5 \times RatingNorm) + (0.3 \times ReviewNorm) + (0.2 \times TicketScore)"
    )

# ==================================================
# 16. HASIL ABC ANALYSIS
# ==================================================

elif menu == "Hasil ABC Analysis":

    st.header("📌 Hasil ABC Analysis")

    st.subheader("Tabel Hasil Analisis Berdasarkan Urutan Popularitas")

    st.dataframe(
        df[
            [
                "Urutan Popularitas",
                "Nama Tempat",
                "Kategori Tempat",
                "Rating Tempat",
                "User Rating",
                "Harga Masuk",
                "Skor Popularitas",
                "Persentase Kontribusi (%)",
                "Persentase Kumulatif (%)",
                "Klasifikasi ABC"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.subheader("Ringkasan Klasifikasi ABC")

    abc_summary = (
        df.groupby("Klasifikasi ABC")
        .agg(
            Jumlah_Tempat=("Nama Tempat", "count"),
            Rata_Rata_Popularitas=("Skor Popularitas", "mean"),
            Min_Kumulatif=("Persentase Kumulatif (%)", "min"),
            Max_Kumulatif=("Persentase Kumulatif (%)", "max")
        )
        .reset_index()
    )

    abc_summary["Persentase Data (%)"] = (
        abc_summary["Jumlah_Tempat"] / len(df) * 100
    )

    st.dataframe(
        abc_summary.round(2),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Proporsi Klasifikasi ABC")

    abc_count = (
        df.groupby("Klasifikasi ABC")
        .size()
        .reset_index(name="Jumlah")
    )

    fig3 = px.pie(
        abc_count,
        names="Klasifikasi ABC",
        values="Jumlah"
    )

    st.plotly_chart(fig3, use_container_width=True)

# ==================================================
# 17. FOOTER
# ==================================================

st.markdown("---")

st.markdown(
    """
    <div style='text-align:center'>
        © 2026 Nadine Assyra & Thia Nadela | Projek Terintegrasi 1<br>
        Program Studi S1 Sains Data ULBI
    </div>
    """,
    unsafe_allow_html=True
)


