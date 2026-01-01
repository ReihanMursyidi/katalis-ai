const BASE_URL = "https://reihanmursyidi-guru-ai.hf.space";

// LOGIKA NAVIGASI
function switchTab(tabName) {
    // Ambil elemen form dan tombol
    const formRPP = document.getElementById('form-rpp');
    const formQuiz = document.getElementById('form-quiz');
    const btns = document.querySelectorAll('.tab-btn');
    
    // Reset Tampilan Hasil (Kembali ke layar sambutan saat pindah tab)
    document.getElementById('welcome-screen').classList.remove('hidden');
    document.getElementById('result-content').classList.add('hidden');

    if (tabName === 'rpp') {
        // Tampilkan Form RPP
        formRPP.classList.remove('hidden-form');
        formRPP.classList.add('active-form');
        formQuiz.classList.remove('active-form');
        formQuiz.classList.add('hidden-form');
        
        // Highlight Tombol RPP
        btns[0].classList.add('active');
        btns[1].classList.remove('active');
    } else {
        // Tampilkan Form Quiz
        formRPP.classList.remove('active-form');
        formRPP.classList.add('hidden-form');
        formQuiz.classList.remove('hidden-form');
        formQuiz.classList.add('active-form');

        // Highlight Tombol Quiz
        btns[0].classList.remove('active');
        btns[1].classList.add('active');
    }
}

// LOGIKA KELAS DINAMIS
function updateKelas(type) {
    // type = 'rpp' atau 'quiz'
    const jenjang = document.getElementById(`${type}_jenjang`).value;
    const kelasSelect = document.getElementById(`${type}_kelas`);
    
    // Kosongkan opsi lama
    kelasSelect.innerHTML = '';
    
    // Tentukan opsi berdasarkan jenjang
    let opsi = [];
    if (jenjang === 'SD') {
        opsi = [1, 2, 3, 4, 5, 6];
    } else if (jenjang === 'SMP') {
        opsi = [7, 8, 9];
    } else if (jenjang === 'SMA') {
        opsi = [10, 11, 12];
    }

    // Masukkan opsi baru ke dropdown
    opsi.forEach(k => {
        const option = document.createElement('option');
        option.value = `Kelas ${k}`;
        option.text = `Kelas ${k}`;
        kelasSelect.appendChild(option);
    });
}

// FETCH API
async function sendRequest(endpoint, dataPayload) {
    // Ambil elemen-elemen UI
    const loader = document.getElementById('loading-overlay');
    const welcome = document.getElementById('welcome-screen');
    const resultContent = document.getElementById('result-content');
    
    // PERBAIKAN: Definisi outputDiv sekarang ada di sini
    const outputDiv = document.getElementById('markdown-output');
    
    const allButtons = document.querySelectorAll('.btn-submit');

    // STATE 1: MULAI LOADING
    loader.classList.remove('hidden');      // Munculkan loading
    welcome.classList.add('hidden');        // Sembunyikan welcome
    resultContent.classList.add('hidden');  // Sembunyikan hasil lama

    // Matikan tombol agar tidak di-spam klik
    allButtons.forEach(btn => {
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Memproses...';
    });

    try {
        // Kirim data ke Backend
        const response = await fetch(`${BASE_URL}/api/${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dataPayload)
        });

        const result = await response.json();

        if (result.status === 'success') {
            // STATE 2: SUKSES
            resultContent.classList.remove('hidden');
            // Konversi Markdown ke HTML
            outputDiv.innerHTML = marked.parse(result.data);
        } else {
            // STATE 3: ERROR DARI BACKEND
            alert("Terjadi kesalahan: " + result.detail);
        }

    } catch (error) {
        // STATE 4: ERROR KONEKSI
        alert("Gagal terhubung ke server. Pastikan internet lancar atau backend aktif.");
        console.error(error);
    } finally {
        // STATE 5: SELESAI (Apapun yang terjadi)
        loader.classList.add('hidden'); // Hilangkan loading

        // Hidupkan tombol kembali
        allButtons.forEach(btn => {
            btn.disabled = false;
            
            // Kembalikan teks tombol sesuai jenisnya
            if(btn.classList.contains('btn-purple')) {
                btn.innerHTML = '<i class="fa-solid fa-puzzle-piece"></i> Buat Soal Otomatis';
            } else {
                btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Buat Modul Ajar';
            }
        });
    }
}

// TRIGGER TOMBOL GENERATE RPP
function generateRPP() {
    const data = {
        jenjang: document.getElementById('rpp_jenjang').value,
        kelas: document.getElementById('rpp_kelas').value,
        mapel: document.getElementById('rpp_mapel').value,
        materi: document.getElementById('rpp_materi').value,
        capaian: document.getElementById('rpp_capaian').value,
        durasi: document.getElementById('rpp_durasi').value
    };

    // Validasi
    if(!data.materi) {
        alert("Mohon isi Materi Pembelajaran terlebih dahulu!");
        return;
    }
    
    // Ubah judul hasil & Panggil API
    document.getElementById('result-title').innerText = "📄 Modul Ajar (RPP)";
    sendRequest('generate-rpp', data);
}

// TRIGGER TOMBOL GENERATE QUIZ
function generateQuiz() {
    const data = {
        jenjang: document.getElementById('quiz_jenjang').value,
        kelas: document.getElementById('quiz_kelas').value,
        topik: document.getElementById('quiz_topik').value,
        jumlah_soal: parseInt(document.getElementById('quiz_jumlah').value),
        jenis_soal: document.getElementById('quiz_jenis').value,
        kesulitan: document.getElementById('quiz_kesulitan').value
    };
    
    // Validasi
    if(!data.topik) {
        alert("Mohon isi Topik/Materi Soal terlebih dahulu!");
        return;
    }

    // Ubah judul hasil & Panggil API
    document.getElementById('result-title').innerText = "📝 Soal Kuis Otomatis";
    sendRequest('generate-quiz', data); 
}

// FITUR COPY TEXT
function copyToClipboard() {
    const text = document.getElementById('markdown-output').innerText;
    navigator.clipboard.writeText(text).then(() => {
        alert("Teks berhasil disalin!");
    });
}

// --- INISIALISASI SAAT LOAD ---
// Isi dropdown kelas saat halaman pertama kali dibuka
updateKelas('rpp');
updateKelas('quiz');