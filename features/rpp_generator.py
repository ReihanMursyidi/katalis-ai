from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()
api_key=os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)

MODEL_PRO = "gemini-2.5-pro"
MODEL_FLASH = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = """
Bertindaklah sebagai Ahli Kurikulum Pendidikan Indonesia.
Sekolah di Indonesia menggunakan Kurikulum 2013 (K-13) dan Kurikulum Merdeka secara bersamaan.
Tugasmu adalah menyusun Modul Ajar (RPP) yang lengkap, terstruktur, dan siap pakai.
Gunakan bahasa Indonesia yang formal, edukatif, namun mudah dipahami guru.
"""

class RPPGenerator(BaseModel):
    jenjang: str = Field(..., description="SD, SMP, SMA")
    kelas: str = Field(..., description="Kelas 1-12")
    mapel: str = Field(..., description="Mata Pelajaran")
    ki: str = Field(..., description="Kompetensi Inti")
    kd: str = Field(..., description="Kompetensi Dasar")
    materi: str = Field(..., description="Materi Pokok (Max 100 chars)")
    model_pembelajaran: str = Field(..., description="Model Pembelajaran (PBL, PjBL, dll)")
    jumlah_jp: int = Field(..., description="Jumlah Jam Pelajaran")
    durasi_per_jp: int = Field(..., description="Menit per JP")

# Fungsi Generator
def generate_rpp(data: RPPGenerator, is_pro_user: bool = False):
    selected_model = MODEL_PRO if is_pro_user else MODEL_FLASH

    model = genai.GenerativeModel(
        model_name=selected_model,
        system_instruction=SYSTEM_INSTRUCTION
    )

    # Hitung total waktu
    total_menit = data.jumlah_jp * data.durasi_per_jp
    alokasi_waktu_str = f"{data.jumlah_jp} JP x {data.durasi_per_jp} Menit ({total_menit} Menit)"

    prompt = f"""
    Buatkan Rencana Pelaksanaan Pembelajaran (RPP) / Modul Ajar Lengkap dengan spesifikasi berikut:
    
    INFORMASI UMUM:
    - Jenjang/Kelas: {data.jenjang} / {data.kelas}
    - Mata Pelajaran: {data.mapel}
    - Alokasi Waktu: {alokasi_waktu_str}
    - Model Pembelajaran: {data.model_pembelajaran} (Pastikan sintaks pembelajaran mengikuti model ini)

    KOMPETENSI:
    - Kompetensi Inti: {data.ki}
    - Kompetensi Dasar / Tujuan Pembelajaran: {data.kd}
    - Materi Pokok: {data.materi}
    
    STRUKTUR OUTPUT (Format Markdown):
    1. **Identitas Modul**: (Rangkum info di atas)
    2. **Tujuan Pembelajaran**: (Turunkan dari KD menjadi indikator yang dapat diukur)
    3. **Media, Alat, & Sumber Belajar**: (Sesuaikan dengan materi)
    4. **Langkah-Langkah Pembelajaran**:
       *PENTING: Langkah pembelajaran HARUS menerapkan sintaks model {data.model_pembelajaran} secara eksplisit.*
       - Pendahuluan (10-15% waktu): Apersepsi, Motivasi, Pertanyaan Pemantik.
       - Kegiatan Inti (70-80% waktu): Bagi menjadi fase-fase sesuai sintaks {data.model_pembelajaran}.
       - Penutup (10-15% waktu): Refleksi, Kesimpulan, Penugasan.
    5. **Penilaian (Asesmen)**:
       - Sikap (Observasi)
       - Pengetahuan (Tes Tulis/Lisan)
       - Keterampilan (Unjuk Kerja/Proyek/Portofolio)

    ATURAN PENTING (STRICT MODE):
    1. JANGAN berikan kalimat pembuka apa pun (seperti "Tentu", "Berikut adalah", "Sebagai ahli kurikulum").
    2. JANGAN berikan kalimat penutup atau kesimpulan di luar konteks RPP.
    3. Langsung mulai output dengan Judul Utama (Header 1).
    4. Pastikan sintaks model pembelajaran terlihat jelas di Kegiatan Inti.
    """

    try:
        # Kirim ke Gemini (Direct Call)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Terjadi kesalahan saat menghubungi AI: {str(e)}"