import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Analisis Wisata Bandung",
    layout="wide"
)

# =========================
# LOAD DATA HASIL COLAB
# =========================

df = pd.read_csv("dataset/hasil_abc_wisata_bandung.csv")

df = df.rename(columns={
    "Popularitas": "Skor Popularitas",
    "Kategori ABC": "Klasifikasi ABC",
    "User Rating": "Jumlah Ulasan",
    "Harga Masuk": "Harga Tiket Masuk"
})

df = df.sort_values(by="Skor Popularitas", ascending=False).reset_index(drop=True)

if "Urutan Popularitas" not in df.columns:
    df.insert(0, "Urutan Popularitas", range(1, len(df) + 1))

# =========================
# HEADER
# =========================

st.title("📍 Analisis Tempat Wisata Bandung")
st.write("ABC Analysis Berdasarkan Rating, Jumlah Ulasan, dan Budget Pengunjung")

# =========================
# SIDEBAR
# =========================

st.sidebar.title("Navigasi")

menu = st.sidebar.radio(
    "Pilih Halaman",
    [
        "Dashboard",
        "Preprocessing",
        "Hasil ABC Analysis",
        "Validasi Referensi"
    ]
)

st.sidebar.markdown("---")
st.sidebar.header("Filter Data")

kategori_filter = st.sidebar.selectbox(
    "Kategori Wisata",
    ["Semua"] + sorted(df["Kategori Tempat"].unique())
)

abc_filter = st.sidebar.selectbox(
    "Klasifikasi ABC",
    ["Semua"] + sorted(df["Klasifikasi ABC"].unique())
)

budget = st.sidebar.slider(
    "💰 Budget Maksimal",
    min_value=0,
    max_value=int(df["Harga Tiket Masuk"].max()),
    value=50000,
    step=5000
)

df_filter = df.copy()

if kategori_filter != "Semua":
    df_filter = df_filter[df_filter["Kategori Tempat"] == kategori_filter]

if abc_filter != "Semua":
    df_filter = df_filter[df_filter["Klasifikasi ABC"] == abc_filter]

# =========================
# DASHBOARD
# =========================

if menu == "Dashboard":

    st.header("📊 Dashboard Analisis Wisata")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Wisata", len(df_filter))
    col2.metric("Kategori A", len(df_filter[df_filter["Klasifikasi ABC"] == "A"]))
    col3.metric("Kategori B", len(df_filter[df_filter["Klasifikasi ABC"] == "B"]))
    col4.metric("Kategori C", len(df_filter[df_filter["Klasifikasi ABC"] == "C"]))

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Proporsi Klasifikasi ABC")

        abc_count = (
            df_filter.groupby("Klasifikasi ABC")
            .size()
            .reset_index(name="Jumlah")
        )

        fig_pie_abc = px.pie(
            abc_count,
            names="Klasifikasi ABC",
            values="Jumlah",
            hole=0.35,
            color="Klasifikasi ABC",
            color_discrete_map={
                "A": "#2056a7",
                "B": "#70ab0b",
                "C": "#bc4a19"
            }
        )

        fig_pie_abc.update_traces(textinfo="label+percent+value")
        st.plotly_chart(fig_pie_abc, use_container_width=True)
        
        
        st.subheader("Distribusi Kategori Wisata per Kategori ABC")

        distribusi_kategori = (
            df_filter.groupby(["Kategori Tempat", "Klasifikasi ABC"])
            .size()
            .reset_index(name="Jumlah")
)

    fig = px.bar(
        distribusi_kategori,
        x="Kategori Tempat",
        y="Jumlah",
        color="Klasifikasi ABC",
        barmode="group",
        text="Jumlah",
        color_discrete_map={
        "A":"#2056a7",
        "B":"#70ab0b",
        "C":"#bc4a19"
    }
)

    fig.update_traces(textposition="outside")

    st.plotly_chart(fig,use_container_width=True)


    st.subheader("Distribusi Wisata Kategori A Berdasarkan Jenis Wisata")

    kategori_a = (
        df_filter[df_filter["Klasifikasi ABC"]=="A"]
)

    kategori_a_count = (
        kategori_a.groupby("Kategori Tempat")
        .size()
        .reset_index(name="Jumlah")
        .sort_values(by="Jumlah",ascending=False)
)

    fig = px.bar(
        kategori_a_count,
        x="Kategori Tempat",
        y="Jumlah",
        color="Kategori Tempat",
        text="Jumlah"
)

    fig.update_traces(textposition="outside")

    st.plotly_chart(fig,use_container_width=True)


    st.subheader("Distribusi Wisata Kategori A Berdasarkan Wilayah")

    wilayah_a = (
        df_filter[df_filter["Klasifikasi ABC"]=="A"]
)

    wilayah_count = (
        wilayah_a.groupby("Wilayah")
        .size()
        .reset_index(name="Jumlah")
        .sort_values(by="Jumlah",ascending=False)
)

    fig = px.bar(
        wilayah_count,
        x="Wilayah",
        y="Jumlah",
        color="Wilayah",
        text="Jumlah"
)

    fig.update_traces(textposition="outside")

    st.plotly_chart(fig,use_container_width=True)

    with col_right:
        st.subheader("Top 10 Tempat Wisata Berdasarkan Skor Popularitas")

        top10 = (
            df_filter.sort_values(by="Skor Popularitas", ascending=False)
            .head(10)
            .sort_values(by="Skor Popularitas", ascending=True)
        )

        fig_top10 = px.bar(
            top10,
            x="Skor Popularitas",
            y="Nama Tempat",
            orientation="h",
            text="Skor Popularitas",
            color="Klasifikasi ABC",
            color_discrete_map={
                "A": "#2056a7",
                "B": "#70ab0b",
                "C": "#bc4a19"
            }
        )

        fig_top10.update_traces(texttemplate="%{text:.3f}", textposition="outside")
        fig_top10.update_layout(
            xaxis_title="Skor Popularitas",
            yaxis_title="Nama Tempat Wisata"
        )

        st.plotly_chart(fig_top10, use_container_width=True)

        st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Hubungan Rating Tempat dengan Jumlah Ulasan")

        fig_scatter = px.scatter(
            df_filter,
            x="Rating Tempat",
            y="Jumlah Ulasan",
            color="Klasifikasi ABC",
            size="Skor Popularitas",
            hover_name="Nama Tempat",
            hover_data={
                "Kategori Tempat": True,
                "Harga Tiket Masuk": True,
                "Skor Popularitas": ":.3f"
            },
            color_discrete_map={
                "A": "#2056a7",
                "B": "#70ab0b",
                "C": "#bc4a19"
            }
        )

        fig_scatter.update_layout(
            xaxis_title="Rating Tempat",
            yaxis_title="Jumlah Ulasan"
        )

        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_right:
        st.subheader("Histogram Harga Tiket Masuk")

        fig_hist_harga = px.histogram(
            df_filter,
            x="Harga Tiket Masuk",
            nbins=20,
            color="Klasifikasi ABC",
            color_discrete_map={
                "A": "#2056a7",
                "B": "#70ab0b",
                "C": "#bc4a19"
            }
        )

        fig_hist_harga.update_layout(
            xaxis_title="Harga Tiket Masuk",
            yaxis_title="Jumlah Tempat Wisata"
        )

        st.plotly_chart(fig_hist_harga, use_container_width=True)

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Boxplot Skor Popularitas")

        fig_box_pop = px.box(
            df_filter,
            x="Klasifikasi ABC",
            y="Skor Popularitas",
            color="Klasifikasi ABC",
            points="all",
            hover_name="Nama Tempat",
            color_discrete_map={
                "A": "#2056a7",
                "B": "#70ab0b",
                "C": "#bc4a19"
            }
        )

        fig_box_pop.update_layout(
            xaxis_title="Klasifikasi ABC",
            yaxis_title="Skor Popularitas"
        )

        st.plotly_chart(fig_box_pop, use_container_width=True)

    with col_right:
        st.subheader("Distribusi Tempat Wisata Berdasarkan Kategori")

        kategori_count = (
            df_filter.groupby("Kategori Tempat")
            .size()
            .reset_index(name="Jumlah")
            .sort_values(by="Jumlah", ascending=True)
        )

        fig_kategori = px.bar(
            kategori_count,
            x="Jumlah",
            y="Kategori Tempat",
            orientation="h",
            text="Jumlah",
            color="Kategori Tempat"
        )

        fig_kategori.update_traces(textposition="outside")
        fig_kategori.update_layout(
            xaxis_title="Jumlah Tempat Wisata",
            yaxis_title="Kategori Wisata",
            showlegend=False
        )

        st.plotly_chart(fig_kategori, use_container_width=True)

        st.markdown("---")

    with col_left:
        st.subheader("Distribusi Klasifikasi ABC Berdasarkan Wilayah")

    wilayah_abc = (
        df_filter.groupby(["Wilayah", "Klasifikasi ABC"])
        .size()
        .reset_index(name="Jumlah")
    )

    fig_wilayah = px.bar(
        wilayah_abc,
        x="Wilayah",
        y="Jumlah",
        color="Klasifikasi ABC",
        text="Jumlah",
        barmode="group",
        color_discrete_map={
            "A": "#2056a7",
            "B": "#70ab0b",
            "C": "#bc4a19"
        }
    )

    fig_wilayah.update_traces(textposition="outside")
    fig_wilayah.update_layout(
        xaxis_title="Wilayah",
        yaxis_title="Jumlah Tempat Wisata"
    )

    st.plotly_chart(fig_wilayah, use_container_width=True)


# =========================
# REKOMENDASI WISATA
# =========================

    st.markdown("---")
    st.header("🎯 Rekomendasi Tempat Wisata Berdasarkan Budget")
    st.write("Rekomendasi Tempat Wisata Berdasarkan Kategori A")
    rekomendasi = df.copy()

    rekomendasi = rekomendasi[
        (rekomendasi["Harga Tiket Masuk"] <= budget) &
        (rekomendasi["Klasifikasi ABC"] == "A")
]

    if kategori_filter != "Semua":
        rekomendasi = rekomendasi[
            rekomendasi["Kategori Tempat"] == kategori_filter
    ]
    
        col1, col2, col3 = st.columns(3)
    
        col1.metric("Jumlah Rekomendasi", len(rekomendasi))

    if len(rekomendasi) > 0:
        col2.metric("Rating Tertinggi", f"{rekomendasi['Rating Tempat'].max():.1f}")
        col3.metric("Harga Termurah", f"Rp {rekomendasi['Harga Tiket Masuk'].min():,.0f}")

        st.success(f"Ditemukan {len(rekomendasi)} tempat wisata sesuai budget dan kategori.")

        st.dataframe(
            rekomendasi[
            [
                "Urutan Popularitas",
                "Nama Tempat",
                "Kategori Tempat",
                "Wilayah",
                "Rating Tempat",
                "Jumlah Ulasan",
                "Harga Tiket Masuk",
                "Skor Popularitas",
                "Klasifikasi ABC"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    
    else:
        col2.metric("Rating Tertinggi", "-")
        col3.metric("Harga Termurah", "-")
    
    st.warning(
    "Tidak ditemukan rekomendasi yang sesuai. Coba naikkan budget atau pilih kategori lain."
)
    
if menu == "Preprocessing":
    st.header("⚙️ Ringkasan Preprocessing Data")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Data Awal", 126)
    col2.metric("Data Setelah Preprocessing", len(df))
    col3.metric("Data Digabung/Dihapus", 2)
    col4.metric("Missing Value", 0)

    st.markdown("---")

    st.subheader("Tahapan Preprocessing")

    st.markdown("""
    Dataset yang digunakan pada dashboard ini merupakan dataset akhir hasil preprocessing dari Google Colab.
    
    Tahapan preprocessing yang telah dilakukan meliputi:
    
    1. Pemeriksaan struktur dataset.
    2. Pemeriksaan missing value.
    3. Standardisasi nama destinasi wisata.
    4. Penghapusan data ganda setelah standardisasi.
    5. Pemilihan atribut yang relevan.
    6. Transformasi tipe data numerik.
    7. Normalisasi data menggunakan Min-Max Normalization.
    8. Perhitungan Ticket Score.
    9. Perhitungan skor popularitas.
    10. Klasifikasi ABC berdasarkan persentase kumulatif.
    """)

    st.subheader("Data Hasil Preprocessing dan ABC Analysis")

    st.dataframe(
        df.head(15),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Boxplot Harga Tiket Masuk")

    fig_box_harga = px.box(
        df,
        x="Klasifikasi ABC",
        y="Harga Tiket Masuk",
        color="Klasifikasi ABC",
        points="all",
        hover_name="Nama Tempat",
        color_discrete_map={
            "A": "#2056a7",
            "B": "#70ab0b",
            "C": "#bc4a19"
        }
    )

    st.plotly_chart(fig_box_harga, use_container_width=True)

# =========================
# HASIL ABC ANALYSIS
# =========================

elif menu == "Hasil ABC Analysis":

    st.header("📌 Hasil ABC Analysis")

    st.subheader("Ringkasan Klasifikasi ABC")

    abc_summary = (
        df.groupby("Klasifikasi ABC")
        .agg(
            Jumlah_Tempat=("Nama Tempat", "count"),
            Rata_Rata_Popularitas=("Skor Popularitas", "mean"),
            Min_Kumulatif=("Persentase Kumulatif", "min"),
            Max_Kumulatif=("Persentase Kumulatif", "max")
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

    fig_abc = px.pie(
        abc_count,
        names="Klasifikasi ABC",
        values="Jumlah",
        hole=0.35,
        color="Klasifikasi ABC",
        color_discrete_map={
            "A": "#2056a7",
            "B": "#70ab0b",
            "C": "#bc4a19"
        }
    )

    fig_abc.update_traces(textinfo="label+percent+value")
    st.plotly_chart(fig_abc, use_container_width=True)

    st.markdown("---")

    st.subheader("Top 20 Wisata Kategori A")

    st.dataframe(
        df[df["Klasifikasi ABC"] == "A"].head(20),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Top 20 Wisata Kategori B")

    st.dataframe(
        df[df["Klasifikasi ABC"] == "B"].head(20),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Top 20 Wisata Kategori C")

    st.dataframe(
        df[df["Klasifikasi ABC"] == "C"].head(20),
        use_container_width=True,
        hide_index=True
    )

# =========================
# VALIDASI REFERENSI
# =========================

elif menu == "Validasi Referensi":

    st.header("✅ Validasi Hasil Rekomendasi dengan Platform Referensi")

    st.write(
        "Validasi dilakukan dengan membandingkan wisata kategori A terhadap platform referensi seperti Tripadvisor, Traveloka, Trip.com, dan Agoda."
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Kategori A", 90)
    col2.metric("Ditemukan", 72)
    col3.metric("Tidak Ditemukan", 18)
    col4.metric("Masuk Top 50", 41)

    st.markdown("---")

    validasi_df = pd.DataFrame({
        "Status Validasi": ["Ditemukan", "Tidak Ditemukan"],
        "Jumlah": [72, 18]
    })

    st.subheader("Proporsi Hasil Validasi Platform Referensi")

    fig_validasi = px.pie(
        validasi_df,
        names="Status Validasi",
        values="Jumlah",
        hole=0.35,
        color="Status Validasi",
        color_discrete_map={
            "Ditemukan": "#2056a7",
            "Tidak Ditemukan": "#bc4a19"
        }
    )

    fig_validasi.update_traces(textinfo="label+percent+value")
    st.plotly_chart(fig_validasi, use_container_width=True)

    st.subheader("Ringkasan Validasi")

    ringkasan_validasi = pd.DataFrame({
        "Keterangan": [
            "Total wisata kategori A",
            "Ditemukan pada platform referensi",
            "Tidak ditemukan pada platform referensi",
            "Masuk Top 50 platform referensi"
        ],
        "Jumlah": [90, 72, 18, 41],
        "Persentase": [
            "100,00%",
            "80,00%",
            "20,00%",
            "45,56% dari kategori A"
        ]
    })

    st.dataframe(
        ringkasan_validasi,
        use_container_width=True,
        hide_index=True
    )

    st.info(
        "Hasil validasi menunjukkan bahwa sebagian besar wisata kategori A ditemukan pada platform referensi. "
        "Hal ini menunjukkan bahwa hasil klasifikasi ABC memiliki kesesuaian dengan rekomendasi wisata populer pada platform digital."
    )

# =========================
# FOOTER
# =========================

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