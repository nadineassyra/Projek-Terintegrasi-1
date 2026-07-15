import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# KONFIGURASI HALAMAN
# =========================

st.set_page_config(
    page_title="Analisis Wisata Bandung",
    layout="wide"
)

# =========================
# WARNA 
# =========================

COLOR_ABC = {
    "A": "#2056a7",
    "B": "#70ab0b",
    "C": "#bc4a19"
}

COLOR_KATEGORI = {
    "Cagar Alam": "#2E8B57",
    "Taman Hiburan": "#F38E12",
    "Budaya": "#8E44AD",
    "Tempat Ibadah": "#1F77B4"
}

# =========================
# FUNGSI BANTUAN
# =========================

def format_rupiah(nilai):
    if pd.isna(nilai):
        return "-"
    return f"Rp {nilai:,.0f}".replace(",", ".")


def ambil_kolom_tersedia(dataframe, daftar_kolom):
    return [kolom for kolom in daftar_kolom if kolom in dataframe.columns]


# =========================
# LOAD DATA
# =========================

@st.cache_data
def load_data():
    df = pd.read_csv("dataset/hasil_abc_wisata_bandung.csv")

    # Menyamakan nama kolom
    df = df.rename(columns={
        "Popularitas": "Skor Popularitas",
        "Kategori ABC": "Klasifikasi ABC",
        "User Rating": "Jumlah Ulasan",
        "Harga Masuk": "Harga Masuk"
    })

    # Membersihkan nama tempat
    df["Nama Tempat"] = df["Nama Tempat"].astype(str).str.strip()

    # Mengubah kolom numerik
    kolom_numerik = [
        "Rating Tempat",
        "Jumlah Ulasan",
        "Harga Masuk",
        "Skor Popularitas",
        "Persentase Kontribusi",
        "Persentase Kumulatif"
    ]

    for kolom in kolom_numerik:
        if kolom in df.columns:
            df[kolom] = pd.to_numeric(df[kolom], errors="coerce")

    # =========================
    # LOAD DATA ALAMAT & GOOGLE MAPS
    # =========================

    try:
        df_maps = pd.read_csv("dataset/kategori_a_dengan_alamat_google_maps.csv")

        df_maps = df_maps.rename(columns={
            "ALAMAT": "Alamat",
            "URL": "Google Maps"
        })

        kolom_maps = ambil_kolom_tersedia(
            df_maps,
            [
                "Nama Tempat",
                "Alamat",
                "Google Maps",
                "Peringkat Validasi",
                "Platform",
                "KET"
                ]
)

        df_maps = df_maps[kolom_maps].copy()
        df_maps["Nama Tempat"] = df_maps["Nama Tempat"].astype(str).str.strip()

        # Menghindari kolom ganda jika data utama sudah punya alamat/link
        df = df.drop(columns=["Alamat", "Google Maps"], errors="ignore")

        df = df.merge(
            df_maps,
            on="Nama Tempat",
            how="left"
        )

    except FileNotFoundError:
        df["Alamat"] = ""
        df["Google Maps"] = ""

    # Mengurutkan berdasarkan skor popularitas
    df = df.sort_values(
        by="Skor Popularitas",
        ascending=False
    ).reset_index(drop=True)

    # Membuat ulang urutan popularitas agar konsisten
    df = df.drop(columns=["Urutan Popularitas"], errors="ignore")
    df.insert(0, "Urutan Popularitas", range(1, len(df) + 1))

    return df


df = load_data()

# =========================
# HEADER UTAMA
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
        "Hasil ABC Analysis",
        "Validasi Referensi",
        "Preprocessing"
    ]
)

st.sidebar.markdown("---")
st.sidebar.header("Filter Data")

kategori_filter = st.sidebar.selectbox(
    "Kategori Wisata",
    ["Semua"] + sorted(df["Kategori Tempat"].dropna().unique())
)

abc_filter = st.sidebar.selectbox(
    "Klasifikasi ABC",
    ["Semua"] + sorted(df["Klasifikasi ABC"].dropna().unique())
)

max_budget = int(df["Harga Masuk"].max()) if len(df) > 0 else 0

budget = st.sidebar.slider(
    "💰 Budget Maksimal",
    min_value=0,
    max_value=max_budget,
    value=50000,
    step=5000
)

# =========================
# FILTER DATA UMUM
# =========================

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

    if len(df_filter) == 0:
        st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")

    else:
        # =========================
        # METRIC RINGKASAN
        # =========================

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Wisata", len(df_filter))
        col2.metric("Kategori A (Paling Populer)", len(df_filter[df_filter["Klasifikasi ABC"] == "A"]))
        col3.metric("Kategori B (Cukup Populer)", len(df_filter[df_filter["Klasifikasi ABC"] == "B"]))
        col4.metric("Kategori C (Kurang Populer)", len(df_filter[df_filter["Klasifikasi ABC"] == "C"]))

        col5, col6 = st.columns(2)

        col5.metric(
            "Rating Tertinggi",
            f"{df_filter['Rating Tempat'].max():.1f}"
        )

        col6.metric(
            "Harga Termurah",
            format_rupiah(df_filter["Harga Masuk"].min())
        )

        st.markdown("---")

        # =========================
        # PROPORSI ABC DAN TOP 10
        # =========================

        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("Proporsi Klasifikasi ABC")

            abc_count = (
                df_filter.groupby("Klasifikasi ABC")
                .size()
                .reset_index(name="Jumlah")
            )
            
            abc_count["Label"] = abc_count["Klasifikasi ABC"].map({
                "A": "A (Paling Populer)",
                "B": "B (Cukup Populer)",
                "C": "C (Kurang Populer)"
                }
            )

            fig_pie_abc = px.pie(
                abc_count,
                names="Label",      
                values="Jumlah",
                hole=0.35,
                color="Klasifikasi ABC",      
                color_discrete_map={
                    "A": "#2056A7",
                    "B": "#70AB0B",
                    "C": "#BC4A19"
    }
)

            fig_pie_abc.update_traces(textinfo="label+percent+value")
            st.plotly_chart(fig_pie_abc, use_container_width=True)

        with col_right:
            st.subheader("Top 10 Tempat Wisata Kategori A")

            data_top10 = df.copy()

            data_top10 = data_top10[
                (data_top10["Harga Masuk"] <= budget) &
                (data_top10["Klasifikasi ABC"] == "A")
            ]

            if kategori_filter != "Semua":
                data_top10 = data_top10[
                    data_top10["Kategori Tempat"] == kategori_filter
                ]

            top10 = (
                data_top10
                .sort_values(
                    by=["Skor Popularitas", "Urutan Popularitas"],
                    ascending=[False, True]
                )
                .head(10)
            )

            if len(top10) == 0:
                st.warning("Tidak ada data Top 10 yang sesuai dengan budget dan kategori wisata.")
            else:
                top10_plot = top10.sort_values(
                    by=["Skor Popularitas", "Urutan Popularitas"],
                    ascending=[True, False]
                )

                fig_top10 = px.bar(
                    top10_plot,
                    x="Skor Popularitas",
                    y="Nama Tempat",
                    orientation="h",
                    text="Skor Popularitas",
                    color_discrete_sequence=["#06429A"]
                    )

                fig_top10.update_traces(
                    texttemplate="%{text:.3f}",
                    textposition="outside"
                )

                fig_top10.update_layout(
                    xaxis_title="Skor Popularitas",
                    yaxis_title="Nama Tempat Wisata"
                )

                st.plotly_chart(fig_top10, use_container_width=True)

        st.markdown("---")

        # =========================
        # DISTRIBUSI KATEGORI A
        # =========================

        kategori_a = df.copy()

        kategori_a = kategori_a[kategori_a["Klasifikasi ABC"] == "A"]

        if kategori_filter != "Semua":
            kategori_a = kategori_a[kategori_a["Kategori Tempat"] == kategori_filter]

        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("Distribusi Wisata Kategori A Berdasarkan Kategori Wisata")

            kategori_a_count = (
                kategori_a.groupby("Kategori Tempat")
                .size()
                .reset_index(name="Jumlah")
                .sort_values(by="Jumlah", ascending=False)
            )

            if len(kategori_a_count) == 0:
                st.warning("Tidak ada data kategori A untuk kategori wisata yang dipilih.")
            else:
                fig_kategori_a = px.bar(
                    kategori_a_count,
                    x="Kategori Tempat",
                    y="Jumlah",
                    color="Kategori Tempat",
                    color_discrete_map=COLOR_KATEGORI,
                    text="Jumlah"
                    )

                fig_kategori_a.update_traces(textposition="outside")

                fig_kategori_a.update_layout(
                    xaxis_title="Kategori Tempat",
                    yaxis_title="Jumlah",
                    showlegend=True
                )

                st.plotly_chart(fig_kategori_a, use_container_width=True)

        with col_right:
            st.subheader("Distribusi Wisata Kategori A Berdasarkan Wilayah")

            wilayah_a_count = (
                kategori_a.groupby("Wilayah")
                .size()
                .reset_index(name="Jumlah")
                .sort_values(by="Jumlah", ascending=False)
            )

            if len(wilayah_a_count) == 0:
                st.warning("Tidak ada data kategori A untuk wilayah yang dipilih.")
            else:
                fig_wilayah_a = px.bar(
                    wilayah_a_count,
                    x="Wilayah",
                    y="Jumlah",
                    text="Jumlah",
                    color_discrete_sequence=["#4F81BD"]
                    )

                fig_wilayah_a.update_traces(textposition="outside")

                fig_wilayah_a.update_layout(
                    xaxis_title="Wilayah",
                    yaxis_title="Jumlah",
                    showlegend=True
                )

                st.plotly_chart(fig_wilayah_a, use_container_width=True)

        # =========================
        # REKOMENDASI WISATA
        # =========================

        st.markdown("---")
        st.header("🎯 Rekomendasi Tempat Wisata")

        st.write(
            "Rekomendasi yang ditampilkan merupakan tempat wisata kategori A berdasarkan hasil klasifikasi ABC "
            "yang sesuai dengan budget pengguna, kategori wisata yang dipilih, serta memiliki status validasi "
            "\"Sesuai\" terhadap platform referensi."
        )

        rekomendasi = df.copy()

        rekomendasi = rekomendasi[
            (rekomendasi["Harga Masuk"] <= budget) &
            (rekomendasi["Klasifikasi ABC"] == "A")
        ]

        if kategori_filter != "Semua":
            rekomendasi = rekomendasi[
                rekomendasi["Kategori Tempat"] == kategori_filter
            ]

        rekomendasi = rekomendasi[
            rekomendasi["KET"].str.strip().str.lower() == "sesuai"
]
        rekomendasi = rekomendasi.reset_index(drop=True)
        rekomendasi["Peringkat"] = range(1, len(rekomendasi) + 1)
        
        rekomendasi = rekomendasi.sort_values(
            by=["Skor Popularitas", "Urutan Popularitas"],
            ascending=[False, True]
)

        col1, col2, col3 = st.columns(3)

        col1.metric("Jumlah Rekomendasi", len(rekomendasi))

        if len(rekomendasi) > 0:
            col2.metric("Rating Tertinggi", f"{rekomendasi['Rating Tempat'].max():.1f}")
            col3.metric("Harga Termurah", format_rupiah(rekomendasi["Harga Masuk"].min()))

            st.success(f"Ditemukan {len(rekomendasi)} tempat wisata sesuai budget dan kategori.")

            kolom_rekomendasi = ambil_kolom_tersedia(
                rekomendasi,
                [
                    "Peringkat",
                    "Nama Tempat",
                    "Kategori Tempat",
                    "Wilayah",
                    "Rating Tempat",
                    "Jumlah Ulasan",
                    "Harga Masuk",
                    "Skor Popularitas",
                    "Klasifikasi ABC",
                    "Alamat",
                    "Google Maps"
                ]
            )

            st.dataframe(
                rekomendasi[kolom_rekomendasi],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Google Maps": st.column_config.LinkColumn(
                        "Google Maps",
                        help="Klik untuk membuka lokasi wisata di Google Maps",
                        display_text="Buka Maps"
                    )
                }
            )

        else:
            col2.metric("Rating Tertinggi", "-")
            col3.metric("Harga Termurah", "-")

            st.warning(
                "Tidak ditemukan rekomendasi yang sesuai. Coba naikkan budget atau pilih kategori lain."
            )

# =========================
# PREPROCESSING
# =========================

elif menu == "Preprocessing":

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
    11. Penambahan alamat dan tautan Google Maps untuk mendukung rekomendasi wisata.
    """)

    st.markdown("---")

    st.subheader("Data Hasil Preprocessing dan ABC Analysis")

    kolom_preprocessing = ambil_kolom_tersedia(
        df_filter,
        [
            "Urutan Popularitas",
            "Nama Tempat",
            "Kategori Tempat",
            "Wilayah",
            "Rating Tempat",
            "Jumlah Ulasan",
            "Harga Masuk",
            "Skor Popularitas",
            "Persentase Kumulatif",
            "Klasifikasi ABC"
            ]
        )
    
    tab_a, tab_b, tab_c = st.tabs(
        ["Kategori A (Paling Populer)", "Kategori B (Cukup Populer)", "Kategori C (Kurang Populer)"]
        )

    with tab_a:
        data_a = (
            df_filter[df_filter["Klasifikasi ABC"] == "A"]
            .sort_values(
                by=["Skor Popularitas", "Urutan Popularitas"],
                ascending=[False, True]
                )
            )
        
        st.dataframe(
            data_a[kolom_preprocessing],
            use_container_width=True,
            hide_index=True
            )

    with tab_b:
        data_b = (
            df_filter[df_filter["Klasifikasi ABC"] == "B"]
            .sort_values(
                by=["Skor Popularitas", "Urutan Popularitas"],
                ascending=[False, True]
                )
            )
        
        st.dataframe(
            data_b[kolom_preprocessing],
            use_container_width=True,
            hide_index=True
            )

    with tab_c:
        data_c = (
            df_filter[df_filter["Klasifikasi ABC"] == "C"]
            .sort_values(
                by=["Skor Popularitas", "Urutan Popularitas"],
                ascending=[False, True]
                )
            )
        st.dataframe(
            data_c[kolom_preprocessing],
            use_container_width=True,
            hide_index=True
            )

# =========================
# HASIL ABC ANALYSIS
# =========================

elif menu == "Hasil ABC Analysis":

    st.header("📌 Hasil ABC Analysis")

    if len(df_filter) == 0:
        st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")

    else:
        # =========================
        # RINGKASAN ABC
        # =========================

        st.subheader("Ringkasan Klasifikasi ABC")

        abc_summary = (
            df_filter.groupby("Klasifikasi ABC")
            .agg(
                Jumlah_Tempat=("Nama Tempat", "count"),
                Rata_Rata_Popularitas=("Skor Popularitas", "mean")
            )
            .reset_index()
        )

        if "Persentase Kumulatif" in df_filter.columns:
            kumulatif_summary = (
                df_filter.groupby("Klasifikasi ABC")
                .agg(
                    Min_Kumulatif=("Persentase Kumulatif", "min"),
                    Max_Kumulatif=("Persentase Kumulatif", "max")
                )
                .reset_index()
            )

            abc_summary = abc_summary.merge(
                kumulatif_summary,
                on="Klasifikasi ABC",
                how="left"
            )

        abc_summary["Persentase Data (%)"] = (
            abc_summary["Jumlah_Tempat"] / len(df_filter) * 100
        )

        st.dataframe(
            abc_summary.round(2),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        # =========================
        # DISTRIBUSI KATEGORI
        # =========================

        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("Distribusi Kategori Wisata per Kategori ABC")

            distribusi_kategori = (
                df_filter.groupby(["Kategori Tempat", "Klasifikasi ABC"])
                .size()
                .reset_index(name="Jumlah")
            )

            fig_distribusi_kategori = px.bar(
                distribusi_kategori,
                x="Kategori Tempat",
                y="Jumlah",
                color="Klasifikasi ABC",
                barmode="group",
                text="Jumlah",
                color_discrete_map=COLOR_ABC
            )

            fig_distribusi_kategori.update_traces(textposition="outside")

            fig_distribusi_kategori.update_layout(
                xaxis_title="Kategori Tempat",
                yaxis_title="Jumlah Tempat Wisata"
            )

            st.plotly_chart(fig_distribusi_kategori, use_container_width=True)


        # =========================
        # DISTRIBUSI ABC BERDASARKAN WILAYAH
        # =========================

        with col_right:
            st.subheader("Distribusi Klasifikasi ABC Berdasarkan Wilayah")
            wilayah_abc = (
            df_filter.groupby(["Wilayah", "Klasifikasi ABC"])
            .size()
            .reset_index(name="Jumlah")
        )

            fig_wilayah_abc = px.bar(
                wilayah_abc,
                x="Wilayah",
                y="Jumlah",
                color="Klasifikasi ABC",
                text="Jumlah",
                barmode="group",
                color_discrete_map=COLOR_ABC
        )

            fig_wilayah_abc.update_traces(textposition="outside")

            fig_wilayah_abc.update_layout(
                xaxis_title="Wilayah",
                yaxis_title="Jumlah Tempat Wisata"
        )

            st.plotly_chart(fig_wilayah_abc, use_container_width=True)

        st.markdown("---")

        # =========================
        # BOXPLOT
        # =========================

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
                color_discrete_map=COLOR_ABC
            )

            fig_box_pop.update_layout(
                xaxis_title="Klasifikasi ABC",
                yaxis_title="Skor Popularitas"
            )

            st.plotly_chart(fig_box_pop, use_container_width=True)

        with col_right:
            st.subheader("Boxplot Harga Masuk Wisata")

            fig_box_harga = px.box(
                df_filter,
                x="Klasifikasi ABC",
                y="Harga Masuk",
                color="Klasifikasi ABC",
                points="all",
                hover_name="Nama Tempat",
                color_discrete_map=COLOR_ABC
            )

            fig_box_harga.update_layout(
                xaxis_title="Klasifikasi ABC",
                yaxis_title="Harga Masuk"
            )

            st.plotly_chart(fig_box_harga, use_container_width=True)

        st.markdown("---")

        # =========================
        # SCATTER 
        # =========================

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
                "Harga Masuk": True,
                "Skor Popularitas": ":.3f"
                },
            color_discrete_map=COLOR_ABC
            )

        fig_scatter.update_layout(
            xaxis_title="Rating Tempat",
            yaxis_title="Jumlah Ulasan"
            )

        st.plotly_chart(fig_scatter, use_container_width=True)


# =========================
# VALIDASI REFERENSI
# =========================

elif menu == "Validasi Referensi":

    st.header("✅ Validasi Hasil Rekomendasi dengan Platform Referensi")

    st.write(
        "Validasi dilakukan dengan membandingkan wisata kategori A terhadap platform referensi seperti "
        "Tripadvisor, Traveloka, Trip.com, dan Agoda."
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
            "Ditemukan": "#2E8B57",
            "Tidak Ditemukan": "#D9534F"
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
        "Hal ini menunjukkan bahwa hasil klasifikasi ABC memiliki kesesuaian dengan rekomendasi wisata populer "
        "pada platform digital."
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