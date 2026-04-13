Cara menjalankan aplikasi:
1. Buat venv
2. Lakukan pip install pada requirements.txt
3. Lakukan setup terhadap .env, berisikan:
    - EIU
        - EIU_API_KEY
        - EIU_EMAIL
        - EIU_PASSWORD
        - EIU_BASE_URL (Opsional)
    - UNCTAD
        - UNCTAD_CLIENT_ID
        - UNCTAD_CLIENT_SECRET
        - UNCTAD_BULK_BASE
4. Buka terminal dan gunakan command <code>cd .\EIU_APP</code> untuk masuk ke dalam folder EIU_APP, setelah itu kita gunakan command <code>streamlit run main.py</code> agar menjalankan script streamlit-nya
5. Click kiri mouse sembari menekan ctrl pada link url di Local URL, seharusnya berisikan <code>Local URL: http://localhost:port</code>