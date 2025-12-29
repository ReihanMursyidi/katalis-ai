// --- 1. Logika Dropdown Kelas Dinamis ---
function updateKelas() {
    const jenjang = document.getElementById('jenjang').value;
    const kelasSelect = document.getElementById('kelas');
    
    // Kosongkan opsi saat ini
    kelasSelect.innerHTML = '<option value="" disabled selected>-</option>';
    
    let opsi = [];
    if (jenjang === 'SD') {
        opsi = [1, 2, 3, 4, 5, 6];
    } else if (jenjang === 'SMP') {
        opsi = [7, 8, 9];
    } else if (jenjang === 'SMA') {
        opsi = [10, 11, 12];
    }

    // Tambahkan opsi baru
    opsi.forEach(k => {
        const option = document.createElement('option');
        option.value = `Kelas ${k}`;
        option.text = `Kelas ${k}`;
        kelasSelect.appendChild(option);
    });
}

// --- 2. Fungsi Utama: Generate RPP ---
async function generateRPP() {
    const btnText = document.getElementById('btnText');
    const spinner = document.getElementById('loadingSpinner');
    const btn = document.getElementById('btnGenerate');
    const welcomeScreen = document.getElementById('welcome-screen');
    const resultContent = document.getElementById('result-content');
    const outputDiv = document.getElementById('markdown-output');

    // Ambil Data Form
    const data = {
        jenjang: document.getElementById('jenjang').value,
        kelas: document.getElementById('kelas').value,
        mapel: document.getElementById('mapel').value,
        materi: document.getElementById('materi').value,
        capaian: document.getElementById('capaian').value,
        durasi: document.getElementById('durasi').value
    };

    // Validasi Sederhana
    if (!data.jenjang || !data.kelas || !data.materi) {
        alert("Harap lengkapi Jenjang, Kelas, dan Materi Utama!");
        return;
    }

    // UI State: Loading
    btn.disabled = true;
    btnText.classList.add('hidden');
    spinner.classList.remove('hidden');
    resultContent.classList.add('hidden');
    
    try {
        // Panggil API Backend (Pastikan main.py sudah berjalan)
        const response = await fetch('http://127.0.0.1:8000/api/generate-rpp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.status === 'success') {
            // Sembunyikan welcome screen, tampilkan hasil
            welcomeScreen.classList.add('hidden');
            resultContent.classList.remove('hidden');

            // Render Markdown ke HTML menggunakan library 'marked'
            // result.data adalah string Markdown dari Gemini
            outputDiv.innerHTML = marked.parse(result.data);
        } else {
            alert("Terjadi kesalahan: " + result.detail);
        }

    } catch (error) {
        console.error(error);
        alert("Gagal terhubung ke server. Pastikan backend Python (main.py) menyala!");
    } finally {
        // UI State: Reset
        btn.disabled = false;
        btnText.classList.remove('hidden');
        spinner.classList.add('hidden');
    }
}

// --- 3. Fitur Copy Text ---
function copyToClipboard() {
    const text = document.getElementById('markdown-output').innerText;
    navigator.clipboard.writeText(text).then(() => {
        alert("Teks RPP berhasil disalin!");
    });
}

// --- 1. LOGIKA NAVIGASI (SPA) ---
function switchTab(tabName) {
    // Ambil elemen
    const formRPP = document.getElementById('form-rpp');
    const formQuiz = document.getElementById('form-quiz');
    const btns = document.querySelectorAll('.tab-btn');
    
    // Reset Tampilan Hasil (Biar tidak bingung)
    document.getElementById('welcome-screen').classList.remove('hidden');
    document.getElementById('result-content').classList.add('hidden');

    if (tabName === 'rpp') {
        // Tampilkan Form RPP
        formRPP.classList.remove('hidden-form');
        formRPP.classList.add('active-form');
        formQuiz.classList.remove('active-form');
        formQuiz.classList.add('hidden-form');
        
        // Update Tombol Active
        btns[0].classList.add('active');
        btns[1].classList.remove('active');
    } else {
        // Tampilkan Form Quiz
        formRPP.classList.remove('active-form');
        formRPP.classList.add('hidden-form');
        formQuiz.classList.remove('hidden-form');
        formQuiz.classList.add('active-form');

        // Update Tombol Active
        btns[0].classList.remove('active');
        btns[1].classList.add('active');
    }
}

// --- 2. LOGIKA KELAS DINAMIS (Bisa dipakai kedua form) ---
function updateKelas(type) {
    // type bisa 'rpp' atau 'quiz'
    const jenjang = document.getElementById(`${type}_jenjang`).value;
    const kelasSelect = document.getElementById(`${type}_kelas`);
    
    kelasSelect.innerHTML = '';
    
    let opsi = [];
    if (jenjang === 'SD') opsi = [1, 2, 3, 4, 5, 6];
    else if (jenjang === 'SMP') opsi = [7, 8, 9];
    else if (jenjang === 'SMA') opsi = [10, 11, 12];

    opsi.forEach(k => {
        const option = document.createElement('option');
        option.value = `Kelas ${k}`;
        option.text = `Kelas ${k}`;
        kelasSelect.appendChild(option);
    });
}

// --- 3. FUNGSI FETCH API (Reusable) ---
async function sendRequest(endpoint, dataPayload) {
    const loader = document.getElementById('loading-overlay');
    const welcome = document.getElementById('welcome-screen');
    const resultContent = document.getElementById('result-content');
    const outputDiv = document.getElementById('markdown-output');

    const allButtons = document.querySelectorAll('.btn-submit');

    // Show Loading
    loader.classList.remove('hidden');
    welcome.classList.add('hidden');
    resultContent.classList.add('hidden');

    // Disable all buttons during request
    allButtons.forEach(btn => {
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Memproses...';
    })

    try {
        const response = await fetch(`http://127.0.0.1:8000/api/${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dataPayload)
        });

        const result = await response.json();

        if (result.status === 'success') {
            resultContent.classList.remove('hidden');
            // Render Markdown
            outputDiv.innerHTML = marked.parse(result.data);
        } else {
            alert("Error: " + result.detail);
        }

    } catch (error) {
        alert("Gagal koneksi ke server Backend.");
        console.error(error);
    } finally {
        loader.classList.add('hidden');

        // Enable all buttons after request
        allButtons.forEach(btn => {
            btn.disabled = false;
            if(btn.classList.contains('btn-purple')) {
                btn.innerHTML = '<i class="fa-solid fa-puzzle-piece"></i> Buat Soal Otomatis';
            } else {
                btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Buat Modul Ajar';
            }
        });
    }
}

// --- 4. TRIGGER TOMBOL ---
function generateRPP() {
    const data = {
        jenjang: document.getElementById('rpp_jenjang').value,
        kelas: document.getElementById('rpp_kelas').value,
        mapel: document.getElementById('rpp_mapel').value,
        materi: document.getElementById('rpp_materi').value,
        capaian: document.getElementById('rpp_capaian').value,
        durasi: document.getElementById('rpp_durasi').value
    };
    // Validasi RPP
    if(!data.materi) return alert("Isi Materi dulu!");
    
    document.getElementById('result-title').innerText = "📄 Modul Ajar (RPP)";
    sendRequest('generate-rpp', data);
}

function generateQuiz() {
    const data = {
        jenjang: document.getElementById('quiz_jenjang').value,
        kelas: document.getElementById('quiz_kelas').value,
        topik: document.getElementById('quiz_topik').value,
        jumlah_soal: parseInt(document.getElementById('quiz_jumlah').value),
        jenis_soal: document.getElementById('quiz_jenis').value,
        kesulitan: document.getElementById('quiz_kesulitan').value
    };
    
    // Validasi Quiz
    if(!data.topik) return alert("Isi Topik soal dulu!");

    document.getElementById('result-title').innerText = "📝 Soal Kuis Otomatis";
    // Nanti endpoint ini akan aktif setelah kita update backend python-nya
    sendRequest('generate-quiz', data); 
}

function copyToClipboard() {
    const text = document.getElementById('markdown-output').innerText;
    navigator.clipboard.writeText(text).then(() => alert("Teks tersalin!"));
}

// Inisialisasi awal
updateKelas('rpp');
updateKelas('quiz');