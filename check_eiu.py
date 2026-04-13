import requests
import json
import urllib3

# Mematikan peringatan SSL (sering bermasalah di jaringan kantor)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Gunakan data asli kamu
API_KEY = "6abZhbjMYB7lORxp5NSSM1zG1f2rMMs83Z9Lf0zW"
BASE_URL = "https://api.eiu.com/v1" # <--- URL Baru dari Sachi
EMAIL = "data1.pskikad@kemlu.go.id"
PASSWORD = "Ik@d4taSatu"

def fetch_eiu_catalog():
    login_url = f"{BASE_URL}/login"
    
    # Header yang lebih lengkap untuk menghindari Error 500
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "PostmanRuntime/7.32.3" # Pura-pura jadi Postman supaya tidak diblok
    }
    
    payload = {
        "emailAddress": EMAIL,
        "password": PASSWORD
    }
    
    print(f"🚀 Mencoba login ke: {login_url}")

    try:
        # 1. LOGIN
        response = requests.post(
            login_url, 
            data=json.dumps(payload), # Gunakan json.dumps agar lebih aman
            headers=headers, 
            verify=False,
            timeout=20
        )
        
        print(f"📊 Login Status: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json().get("token")
            print("✅ Login Berhasil!")
            
            # 2. AMBIL DATA INDIKATOR
            print("📦 Menarik daftar indikator...")
            data_url = f"{BASE_URL}/data/referencedata"
            auth_headers = {
                "x-api-key": API_KEY,
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }
            
            res_data = requests.get(data_url, headers=auth_headers, verify=False)
            
            if res_data.status_code == 200:
                # Ambil format full untuk grouping manual
                full_json = res_data.json()
                
                with open("full_catalog.json", "w") as f:
                    json.dump(full_json, f, indent=4)
                
                print(f"✅ SUKSES! File 'full_catalog.json' tersimpan.")
                print("Silakan buka file tersebut untuk melihat format grouping aslinya.")
            else:
                print(f"❌ Gagal ambil data: {res_data.status_code}")
                print(f"Respon: {res_data.text}")
                
        else:
            print(f"❌ Gagal Login!")
            print(f"Pesan Server: {response.text}")

    except Exception as e:
        print(f"🔥 Error: {e}")

if __name__ == "__main__":
    fetch_eiu_catalog()