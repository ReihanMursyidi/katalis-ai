import os
import google.generativeai as genai
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Konfigurasi Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""
    Bertindaklah sebagai Guru Profesional pembuat soal ujian. 
    Tugasmu adalah membuat daftar soal kuis yang berkualitas, sesuai kurikulum di Indonesia, 
    dan akurat secara akademik.
    Sekolah di Indonesia menggunakan Kurikulum 2013 (K-13) dan Kurikulum Merdeka secara bersamaan.
    """
)

# Model Data Input (Harus sama dengan yang dikirim dari Frontend script.js)
class QuizRequest(BaseModel):
    jenjang: str
    kelas: str
    topik: str
    jumlah_soal: int
    jenis_soal: str = Field(..., description="Pilihan Ganda atau Essay")
    kesulitan: str = Field(..., description="Mudah, Sedang, atau Sulit")

def generate_quiz_content(data: QuizRequest):
    # Prompt Engineering Khusus Soal
    prompt = f"""
    Buatkan Soal Kuis dengan spesifikasi berikut:
    
    - Jenjang: {data.jenjang}
    - Kelas: {data.kelas}
    - Mata Pelajaran/Topik: {data.topik}
    - Jumlah Soal: {data.jumlah_soal}
    - Jenis Soal: {data.jenis_soal}
    - Tingkat Kesulitan: {data.kesulitan}

    Instruksi Output (Format Markdown):
    1. Judul Kuis (Topik & Kelas)
    2. Daftar Soal (Nomor 1 sampai {data.jumlah_soal})
       - Jika Pilihan Ganda: Berikan opsi A, B, C, D (dan E jika SMA).
    3. Kunci Jawaban & Pembahasan (Letakkan di bagian paling bawah, terpisah garis).
    
    Pastikan bahasa soal jelas, tidak ambigu, dan sesuai dengan tingkat kesulitan {data.kesulitan}.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gagal membuat soal: {str(e)}"