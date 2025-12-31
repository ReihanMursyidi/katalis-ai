const BASE_URL = "https://reihanmursyidi-guru-ai.hf.space";

// LOGIKA NAVIGASI
function switchTab(tabName) {
    const formRPP = document.getElementById('form-rpp');
    const formQuiz = document.getElementById('form-quiz');
    const btns = document.querySelectorAll('.tab-btn');

    document.getElementById('welcome-screen').classList.remove('hidden');
    document.getElementById('result-content').classList.add('hidden');

    if (tabName === 'rpp') {
        formRPP.classList.remove('hidden-form');
        formRPP.classList.add('active-form');
        formQuiz.classList.remove('active-form');
        formQuiz.classList.add('hidden-form');

        btns[0].classList.add('active');
        btns[1].classList.remove('active');
    } else {
        formRPP.classList.remove('active-form');
        formRPP.classList.add('hidden-form');
        formQuiz.classList.remove('hidden-form');
        formQuiz.classList.add('active-form');

        btns[0].classList.remove('active');
        btns[1].classList.add('active');
    }
}

// LOGIKA KELAS JENJANG
function updateKelas(type) {
    const jenjang = document.getElementById(`${type}_jenjang`).value;
    const kelasSelect = document.getElementById(`${type}_kelas`);

    kelasSelect.innerHTML = '';

    let opsi = [];
    if (jenjang === 'SD') {
        opsi = ['1', '2', '3', '4', '5', '6'];
    } else if (jenjang === 'SMP') {
        opsi = ['7', '8', '9'];
    } else if (jenjang === 'SMA') {
        opsi = ['10', '11', '12'];
    }

    opsi.forEach(k => {
        const option = document.createElement('option');
        option.value = `Kelas ${k}`;
        option.text = `Kelas ${k}`;
        kelasSelect.appendChild(option);
    });
}

// FETCH API
async function sendRequest(endpoint, dataPayload) {
    const loader = document.getElementById('loading-overlay');
    const welcome = document.getElementById('welcome-screen');
    const resultContent = document.getElementById('result-content');

    // Ambil semua elemen form untuk dinonaktifkan
    const allButtons = document.querySelectorAll('.btn-submit');

    loader.classList.remove('hidden');
    welcome.classList.add('hidden');
    resultContent.classList.add('hidden');

    allButtons.forEach(btn => {
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Memproses...';
    });

    try {
        // Kirim permintaan ke backend
        const response = await fetch(`${BASE_URL}/api/${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dataPayload)
        });

        const result = await response.json();

        if (result.status === 'success') {
            resultContent.classList.remove('hidden');
            outputDiv.innerHTML = marked.parse(result.data);
        } else {
            alert('Terjadi kesalahan: ' + result.detail);
        }

    } catch (error) {
        alert('Gagal terhubung ke server. Pastikan backend Python sudah berjalan.');
        console.error('Terjadi kesalahan:', error);
    } finally {
        loader.classList.add('hidden');
        allButtons.forEach(btn => {
            btn.disabled = false;

            if(btn.classList.contains('btn-purple')) {
                btn.innerHTML = '<i class="fa-solid fa-puzzle-piece"></i> Generate Soal';
            } else {
                btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Generate RPP';
            }
        });
    }
}

// TRIGGER TOMBOL GENERATE RPP
function generateRPP() {
    // Ambil data dari form RPP (perhatikan ID-nya pakai prefix rpp_)
    const data = {
        jenjang: document.getElementById('rpp_jenjang').value,
        kelas: document.getElementById('rpp_kelas').value,
        mapel: document.getElementById('rpp_mapel').value,
        materi: document.getElementById('rpp_materi').value,
        capaian: document.getElementById('rpp_capaian').value,
        durasi: document.getElementById('rpp_durasi').value
    };

    // Validasi input kosong
    if(!data.materi) {
        alert("Harap isi materi pelajaran terlebih dahulu!");
        return;
    }
    
    // Ubah judul hasil & Panggil API
    document.getElementById('result-title').innerText = "📄 Modul Ajar (RPP)";
    sendRequest('generate-rpp', data);
}

// TRIGGER TOMBOL GENERATE QUIZ
function generateQuiz() {
    // Ambil data dari form Quiz
    const data = {
        jenjang: document.getElementById('quiz_jenjang').value,
        kelas: document.getElementById('quiz_kelas').value,
        topik: document.getElementById('quiz_topik').value,
        jumlah_soal: parseInt(document.getElementById('quiz_jumlah').value),
        jenis_soal: document.getElementById('quiz_jenis').value,
        kesulitan: document.getElementById('quiz_kesulitan').value
    };
    
    // Validasi input kosong
    if(!data.topik) {
        alert("Harap isi topik soal terlebih dahulu!");
        return;
    }

    // Ubah judul hasil & Panggil API
    document.getElementById('result-title').innerText = "📝 Soal Kuis Otomatis";
    sendRequest('generate-quiz', data); 
}

// --- 6. FITUR SALIN TEKS ---
function copyToClipboard() {
    const text = document.getElementById('markdown-output').innerText;
    navigator.clipboard.writeText(text).then(() => {
        alert("Teks berhasil disalin ke clipboard!");
    });
}

// --- 7. INISIALISASI AWAL ---
// Jalankan fungsi ini saat halaman pertama dibuka agar dropdown kelas terisi
updateKelas('rpp');
updateKelas('quiz');
