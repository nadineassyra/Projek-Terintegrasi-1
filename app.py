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

df_awal = pd.read_csv(
    "dataset/final dataset wisata bandung.csv"
)


# ==================================================
# 3. CEK DATA AWAL
# ==================================================

jumlah_data_awal = len(df_awal)
missing_value_awal = int(df_awal.isnull().sum().sum())
duplikat_awal = int(df_awal.duplicated().sum())


# ==================================================
# 4. PILIH ATRIBUT
# ==================================================

df = df_awal[
    [
        "Nama Tempat",
        "Kategori Tempat",
        "Rating Tempat",
        "Harga Masuk",
        "User Rating"
    ]
].copy()


# ==================================================
# 5. KONVERSI DATA NUMERIK
# ==================================================

df["Rating Tempat"] = pd.to_numeric(df["Rating Tempat"], errors="coerce")
df["Harga Masuk"] = pd.to_numeric(df["Harga Masuk"], errors="coerce")
df["User Rating"] = pd.to_numeric(df["User Rating"], errors="coerce")


# ==================================================
# 6. DATA BERMASALAH
# ==================================================

data_bermasalah = df[
    df[
        [
            "Nama Tempat",
            "Kategori Tempat",
            "Rating Tempat",
            "Harga Masuk",
            "User Rating"
        ]
    ].isnull().any(axis=1)
]

jumlah_data_bermasalah = len(data_bermasalah)


# ==================================================
# 7. PENANGANAN DATA KOSONG
# ==================================================

df["Nama Tempat"] = df["Nama Tempat"].fillna("Tidak Diketahui")
df["Kategori Tempat"] = df["Kategori Tempat"].fillna("Tidak Diketahui")
df["Rating Tempat"] = df["Rating Tempat"].fillna(df["Rating Tempat"].mean())
df["Harga Masuk"] = df["Harga Masuk"].fillna(0)
df["User Rating"] = df["User Rating"].fillna(0)


jumlah_data_bersih = len(df)
missing_value_bersih = int(df.isnull().sum().sum())
duplikat_bersih = int(df.duplicated().sum())


# ==================================================
# 8. DATA SEBELUM NORMALISASI
# ==================================================

df_sebelum_normalisasi = df[
    [
        "Nama Tempat",
        "Kategori Tempat",
        "Rating Tempat",
        "Harga Masuk",
        "User Rating"
    ]
].copy()


# ==================================================
# 9. NORMALISASI MIN-MAX
# ==================================================

scaler = MinMaxScaler()

df[
    [
        "RatingNorm",
        "ReviewNorm",
        "TicketNorm"
    ]
] = scaler.fit_transform(
    df[
        [
            "Rating Tempat",
            "User Rating",
            "Harga Masuk"
        ]
    ]
)


# ==================================================
# 10. TICKET SCORE
# ==================================================

df["TicketScore"] = 1 - df["TicketNorm"]


# ==================================================
# 11. HITUNG SKOR POPULARITAS
# ==================================================

df["Skor Popularitas"] = (
    (0.5 * df["RatingNorm"])
    + (0.3 * df["ReviewNorm"])
    + (0.2 * df["TicketScore"])
)


# ==================================================
# 12. ABC ANALYSIS
# ==================================================

df = df.sort_values(
    by="Skor Popularitas",
    ascending=False
)

total_pop = df["Skor Popularitas"].sum()

df["Persentase Kontribusi (%)"] = (
    df["Skor Popularitas"] / total_pop
) * 100

df["Persentase Kumulatif (%)"] = (
    df["Persentase Kontribusi (%)"]
    .cumsum()
)


def klasifikasi_abc(nilai):
    if nilai <= 80:
        return "A"
    elif nilai <= 95:
        return "B"
    else:
        return "C"


df["Klasifikasi ABC"] = (
    df["Persentase Kumulatif (%)"]
    .apply(klasifikasi_abc)
)


# ==================================================
# 13. URUTAN POPULARITAS
# ==================================================

df = df.reset_index(drop=True)

df.insert(
    0,
    "Urutan Popularitas",
    range(1, len(df) + 1)
)


# ==================================================
# 14. HEADER
# ==================================================

st.title("📍 Analisis Tempat Wisata Bandung")

st.write(
    "ABC Analysis Berdasarkan Rating, Jumlah Ulasan, dan Budget Pengunjung"
)


# ==================================================
# 15. SIDEBAR
# ==================================================

st.sidebar.title("Navigasi")

menu = st.sidebar.radio(
    "Pilih Halaman",
    [
        "Dashboard",
        "Preprocessing",
        "Hasil ABC Analysis"
    ]
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
# 16. FILTER REKOMENDASI
# ==================================================

rekomendasi = df[
    (df["Harga Masuk"] <= budget)
    &
    (df["Klasifikasi ABC"] == "A")
]

if kategori != "Semua":
    rekomendasi = rekomendasi[
        rekomendasi["Kategori Tempat"] == kategori
    ]


# ==================================================
# 17. HALAMAN DASHBOARD
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

    abc_count = (
        df.groupby("Klasifikasi ABC")
        .size()
        .reset_index(name="Jumlah")
    )

    fig1 = px.bar(
    abc_count,
    x="Klasifikasi ABC",
    y="Jumlah",
    color="Klasifikasi ABC",
    text="Jumlah",
    title="Distribusi Klasifikasi ABC",
    color_discrete_map={
        "A": "#28a745",
        "B": "#ffc107",
        "C": "#dc3545"
    }
)

    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Top 10 Tempat Wisata Berdasarkan Skor Popularitas")

    top10 = df.head(10)

    fig2 = px.bar(
    top10,
    x="Nama Tempat",
    y="Skor Popularitas",
    text="Skor Popularitas",
    title="Top 10 Tempat Wisata Berdasarkan Skor Popularitas"
)
    fig2.update_traces(
    texttemplate="%{text:.3f}",
    textposition="outside"
)
    fig2.update_layout(
    xaxis_title="Nama Tempat Wisata",
    yaxis_title="Skor Popularitas"
)

    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Rekomendasi Wisata Berdasarkan Budget dan Kategori")

    st.write(
        f"Budget maksimal yang dipilih: **Rp{budget:,.0f}**"
    )

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
# 18. HALAMAN PREPROCESSING
# ==================================================

elif menu == "Preprocessing":

    st.header("⚙️ Preprocessing Data")

    st.subheader("Ringkasan Data")

    col1, col2, col3 = st.columns(3)

    col1.metric("Data Awal", jumlah_data_awal)
    col2.metric("Missing Value Awal", missing_value_awal)
    col3.metric("Duplikat Awal", duplikat_awal)

    col4, col5, col6 = st.columns(3)

    col4.metric("Data Setelah Preprocessing", jumlah_data_bersih)
    col5.metric("Missing Value Setelah Preprocessing", missing_value_bersih)
    col6.metric("Duplikat Setelah Preprocessing", duplikat_bersih)

    st.markdown("---")

    st.subheader("Tahapan Preprocessing")

    st.markdown("""
    1. Memilih atribut yang digunakan, yaitu **Nama Tempat**, **Kategori Tempat**, 
       **Rating Tempat**, **Harga Masuk**, dan **User Rating**.

    2. Mengecek missing value dan data duplikat.

    3. Mengubah atribut **Rating Tempat**, **Harga Masuk**, dan **User Rating** 
       menjadi tipe data numerik.

    4. Menangani data kosong jika ditemukan.

    5. Melakukan normalisasi menggunakan metode **Min-Max Normalization**.

    6. Menghitung **Ticket Score** dengan membalik nilai normalisasi harga tiket.

    7. Menghitung **Skor Popularitas** sebagai dasar analisis ABC.
    """)

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

    st.markdown("---")

    st.subheader("Rumus yang Digunakan")

    st.latex(
        r"X_{norm} = \frac{X - X_{min}}{X_{max} - X_{min}}"
    )

    st.latex(
        r"TicketScore = 1 - TicketNorm"
    )

    st.latex(
        r"Skor\ Popularitas = (0.5 \times RatingNorm) + (0.3 \times ReviewNorm) + (0.2 \times TicketScore)"
    )


# ==================================================
# 19. HALAMAN HASIL ABC ANALYSIS
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

    st.subheader("Proporsi Klasifikasi ABC")

    abc_count = (
        df.groupby("Klasifikasi ABC")
        .size()
        .reset_index(name="Jumlah")
    )

    fig3 = px.pie(
        abc_count,
        names="Klasifikasi ABC",
        values="Jumlah",
        title="Proporsi Klasifikasi ABC"
    )

    st.plotly_chart(fig3, use_container_width=True)


# ==================================================
# 20. FOOTER
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