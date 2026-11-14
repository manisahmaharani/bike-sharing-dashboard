# Proyek Analisis Data: Bike Sharing Dataset

Analisis data Capital Bikeshare (Washington D.C., 2011-2012) beserta dashboard Streamlit.

## Pertanyaan Bisnis
1. Bagaimana pola rata-rata penyewaan sepeda per jam pada hari kerja dibandingkan hari libur sepanjang 2012, untuk menentukan peak hours operasional?
2. Bagaimana perbedaan proporsi penyewaan pengguna casual dan registered berdasarkan kondisi cuaca selama 2011-2012?

## Struktur Folder
```
submission
├── dashboard
│   ├── dashboard.py
│   ├── main_data.csv      # data harian bersih
│   └── hour_data.csv      # data per jam bersih
├── data
│   ├── day.csv
│   └── hour.csv
├── notebook.ipynb
├── README.md
└── requirements.txt
```

## Setup Environment
```
python -m venv venv
venv\Scripts\activate        # Windows (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
```

## Menjalankan Notebook
Buka `notebook.ipynb` dari folder `submission` (agar path `data/day.csv` terbaca), lalu Run All.

## Menjalankan Dashboard
```
streamlit run dashboard/dashboard.py
```

## Dashboard Online
URL Streamlit Cloud: (isi setelah deploy)
