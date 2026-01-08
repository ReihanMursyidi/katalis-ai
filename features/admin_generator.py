import google.generativeai as genai
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL_PRO = "gemini-2.5-pro"
MODEL_FLASH = "gemini-2.5-flash"

class RaportRequest(BaseModel):
    nama_siswa: str
    kelas: str
    nilai_rata: float
    sikap: str
    catatan_guru: str = "" # Optional

def generate_rapor_comment(request: RaportRequest, is_pro_user: bool = False) -> str:
    selected_model = MODEL_PRO if is_pro_user else MODEL_FLASH

    model = genai.GenerativeModel(selected_model)

    prompt = f"""
    Bertindaklah sebagai Guru Wali Kelas yang bijaksana dan memotivasi.
    Buatlah deskripsi rapor (Narasi) untuk siswa berikut:
    Nama Siswa: {request.nama_siswa}
    Kelas: {request.kelas}
    Nilai Rata-rata: {request.nilai_rata}
    Sikap: {request.sikap}
    Catatan Guru: {request.catatan_guru}

    Panduan:
    1. Gunakan bahasa yang santun, santai, namun menyentuh hati.
    2. Awali dengan apresiasi, lalu bahas kemajuan akademis, jika nilai rata-ratanya di bawah 70, sampaikan rencana perbaikan.
    3. Jangan sebutkan angka nilai secara mentah, tapi deskripsikan (Sangat Baik, Perlu ditingkatkan).
    4. Akhiri dengan motivasi untuk semester/tahun depan.
    5. Buatlah narasi sepanjang 150-200 kata.
    """

    response = model.generate_content(prompt)
    
    # Return data beserta info model yang dipakai (untuk debug/display)
    return {
        "content": response.text,
        "model_used": selected_model
    }