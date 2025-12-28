from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()
api_key=os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""
    Bertindaklah sebagai Ahli Kurikulum Pendidikan Indonesia.
    Sekolah di Indonesia menggunakan Kurikulum 2013 (K-13) dan Kurikulum Merdeka secara bersamaan.
    Tugasmu adalah menyusun Modul Ajar (RPP) yang lengkap, terstruktur, dan siap pakai.
    Gunakan bahasa Indonesia yang formal, edukatif, namun mudah dipahami guru.
    """
)

class RPPGenerator(BaseModel):
    jenjang: str = Field(..., description="SD, SMP, SMA")
    kelas: str = Field(..., description="Kelas 1-12")
    mapel: str = Field(..., description="Mata Pelajaran")
    materi: str = Field(..., description="Materi Utama")
    capaian: str = Field(..., description="Capaian Pembelajaran")
    durasi: str = Field(..., description="Durasi Pembelajaran")

# Fungsi Generator
def generate_rpp(data: RPPGenerator):
    prompt = f"""
    Buatkan Modul Ajar untuk data berikut:
    
    INFORMASI KELAS:
    - Jenjang: {data.jenjang}
    - Kelas: {data.kelas}
    - Mata Pelajaran: {data.mapel}
    - Materi: {data.materi}
    - Capaian Pembelajaran: {data.capaian}
    - Alokasi Waktu: {data.durasi}

    STRUKTUR OUTPUT (Format Markdown):
    1. **Identitas Modul**: (Rangkum info di atas)
    2. **Profil Pelajar Pancasila**: (Pilih dimensi yang relevan dengan materi ini)
    3. **Media & Sumber Belajar**: (Alat, buku, link yang dibutuhkan)
    4. **Langkah Pembelajaran**:
       - Pendahuluan (Apersepsi, Pertanyaan Pemantik)
       - Kegiatan Inti (Gunakan pendekatan saintifik atau PBL)
       - Penutup (Refleksi siswa & guru)
    5. **Asesmen**: (Ide penilaian formatif/sumatif)

    ATURAN PENTING (STRICT MODE):
    1. JANGAN berikan kalimat pembuka apa pun (seperti "Tentu", "Berikut adalah", "Sebagai ahli kurikulum").
    2. JANGAN berikan kalimat penutup atau kesimpulan di luar konteks RPP.
    3. Langsung mulai output dengan Judul Utama (Header 1).
    4. Gunakan Bahasa Indonesia yang baku dan format Markdown yang rapi.
    """

    try:
        # Kirim ke Gemini (Direct Call)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Terjadi kesalahan saat menghubungi AI: {str(e)}"