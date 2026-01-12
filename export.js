/* =================================================================
   EXPORT.JS - Logika Unduh Dokumen (Word & PDF)
   ================================================================= */

// 1. Export ke Microsoft Word (.doc)
function exportToWord() {
    const contentElement = document.getElementById('markdown-output');
    const titleElement = document.getElementById('result-title');
    
    // Validasi sederhana jika elemen belum ada
    if (!contentElement || !titleElement) {
        alert("Konten tidak ditemukan!");
        return;
    }

    const content = contentElement.innerHTML;
    const title = titleElement.innerText || 'Dokumen EduPlan';

    // Template HTML khusus untuk Word agar margin dan font rapi
    const preHtml = `
        <html xmlns:o='urn:schemas-microsoft-com:office:office' 
              xmlns:w='urn:schemas-microsoft-com:office:word' 
              xmlns='http://www.w3.org/TR/REC-html40'>
        <head>
            <meta charset='utf-8'>
            <title>${title}</title>
            <style>
                body { font-family: 'Calibri', sans-serif; line-height: 1.5; color: #000000; }
                h1, h2, h3 { color: #2E74B5; }
                ul, ol { margin-left: 20px; }
                table { border-collapse: collapse; width: 100%; }
                td, th { border: 1px solid #000; padding: 8px; }
            </style>
        </head>
        <body>
            <h1>${title}</h1>
            ${content}
        </body>
        </html>
    `;

    const blob = new Blob(['\ufeff', preHtml], {
        type: 'application/msword'
    });

    const url = 'data:application/vnd.ms-word;charset=utf-8,' + encodeURIComponent(preHtml);
    const downloadLink = document.createElement("a");
    document.body.appendChild(downloadLink);
    
    if(navigator.msSaveOrOpenBlob) {
        navigator.msSaveOrOpenBlob(blob, `${title}.doc`);
    } else {
        downloadLink.href = url;
        downloadLink.download = `${title}.doc`;
        downloadLink.click();
    }
    
    document.body.removeChild(downloadLink);
}

// 2. Export ke PDF
async function exportToPDF() {
    // 1. Ambil Data
    const titleElement = document.getElementById('result-title');
    const contentElement = document.getElementById('markdown-output');

    if (!contentElement) {
        alert("Tidak ada konten untuk diunduh!");
        return;
    }

    const title = titleElement.innerText || 'Dokumen';
    const contentText = contentElement.innerText; // Ambil teks bersih (bukan HTML)

    // 2. Ubah Tombol jadi Loading
    const btn = document.querySelector('button[onclick*="exportToPDF"]');
    const oldContent = btn ? btn.innerHTML : '';
    if(btn) btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i>';

    try {
        // 3. Request ke Backend
        const response = await fetch(`${BASE_URL}/api/export-pdf`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: title,
                content: contentText
            })
        });

        if (response.ok) {
            // 4. Download File dari Blob Response
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${title}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove(); // Bersihkan elemen link
            window.URL.revokeObjectURL(url); // Bersihkan memori blob
        } else {
            const err = await response.json();
            alert("Gagal export PDF: " + (err.detail || "Server Error"));
        }
    } catch (error) {
        console.error(error);
        alert("Terjadi kesalahan koneksi ke server.");
    } finally {
        // 5. Kembalikan Tombol
        if(btn) btn.innerHTML = oldContent;
    }
}