import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import plotly.express as px


# KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Analisis Wisata Bandung",
    layout="wide"
)


# LOAD DATA
df = pd.read_csv(r"dataset/final dataset wisata bandung.csv")


# PREPROCESSING
df = df[
    [
        'Nama Tempat',
        'Kategori Tempat',
        'Rating Tempat',
        'Harga Masuk',
        'User Rating'
    ]
]

df = df.dropna()


# NORMALISASI
scaler = MinMaxScaler()

df[
    [
        'RatingNorm',
        'ReviewNorm',
        'TicketNorm'
    ]
] = scaler.fit_transform(
    df[
        [
            'Rating Tempat',
            'User Rating',
            'Harga Masuk'
        ]
    ]
)

# Harga murah = skor lebih tinggi
df['TicketScore'] = 1 - df['TicketNorm']


# HITUNG POPULARITAS
df['Popularitas'] = (
    (0.5 * df['RatingNorm']) +
    (0.3 * df['ReviewNorm']) +
    (0.2 * df['TicketScore'])
)


# ABC ANALYSIS
df = df.sort_values(
    by='Popularitas',
    ascending=False
)

total_pop = df['Popularitas'].sum()

df['Persentase'] = (
    df['Popularitas'] / total_pop
) * 100

df['Kumulatif'] = (
    df['Persentase']
    .cumsum()
)

def kategori_abc(nilai):

    if nilai <= 80:
        return "A"

    elif nilai <= 95:
        return "B"

    else:
        return "C"

df['Kategori ABC'] = (
    df['Kumulatif']
    .apply(kategori_abc)
)


# JUDUL DASHBOARD
st.title(
    "📍 Analisis Tempat Wisata Bandung"
)

st.write(
    "ABC Analysis Berdasarkan Rating, User Rating, dan Budget Pengunjung"
)


# SIDEBAR FILTER
st.sidebar.header("Filter Wisata")

budget = st.sidebar.slider(
    "Budget Maksimal",
    0,
    int(df['Harga Masuk'].max()),
    50000
)

kategori = st.sidebar.selectbox(
    "Kategori Wisata",
    ["Semua"] +
    sorted(
        list(
            df['Kategori Tempat']
            .unique()
        )
    )
)


# FILTER DATA
hasil = df[
    df['Harga Masuk'] <= budget
]

if kategori != "Semua":

    hasil = hasil[
        hasil['Kategori Tempat']
        == kategori
    ]


# METRIC
col1, col2, col3 = st.columns(3)

col1.metric(
    "Kategori A",
    len(
        df[
            df['Kategori ABC']
            == 'A'
        ]
    )
)

col2.metric(
    "Kategori B",
    len(
        df[
            df['Kategori ABC']
            == 'B'
        ]
    )
)

col3.metric(
    "Kategori C",
    len(
        df[
            df['Kategori ABC']
            == 'C'
        ]
    )
)


# GRAFIK DISTRIBUSI ABC
st.subheader(
    "Distribusi Kategori ABC"
)

abc_count = (
    df.groupby('Kategori ABC')
    .size()
    .reset_index(name='Jumlah')
)

fig1 = px.bar(
    abc_count,
    x='Kategori ABC',
    y='Jumlah',
    title='Distribusi Kategori ABC'
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# TOP 10 WISATA
st.subheader(
    "Top 10 Tempat Wisata Terpopuler"
)

top10 = df.head(10)

fig2 = px.bar(
    top10,
    x='Nama Tempat',
    y='Popularitas',
    title='Top 10 Wisata Terpopuler'
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


# REKOMENDASI
st.subheader(
    "Rekomendasi Wisata"
)

rekomendasi = hasil[
    hasil['Kategori ABC']
    == 'A'
]

st.dataframe(
    rekomendasi[
        [
            'Nama Tempat',
            'Kategori Tempat',
            'Rating Tempat',
            'Harga Masuk',
            'Kategori ABC'
        ]
    ],
    use_container_width=True
)


# TABEL HASIL ANALISIS
st.subheader(
    "Hasil Analisis ABC"
)

st.dataframe(
    hasil[
        [
            'Nama Tempat',
            'Kategori Tempat',
            'Rating Tempat',
            'User Rating',
            'Harga Masuk',
            'Popularitas',
            'Kategori ABC'
        ]
    ],
    use_container_width=True
)


# COPYRIGHT
st.markdown("---")

st.caption(
    "© 2026 Nadine Assyra & Thia Nadela | "
    "Program Studi S1 Sains Data ULBI"
)