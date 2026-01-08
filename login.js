function checkLoginRequirement() {
    const token = localStorage.getItem('eduplan_token');
    
    if (!token) {
        alert("Silakan Login atau Daftar dulu ya! 🔒");
        
        // 2. Buka Modal Login
        toggleAuthModal(true);
        
        // 3. Pastikan yang terbuka adalah tab "Masuk", bukan "Daftar"
        switchAuthMode('login'); 
        
        // 4. Kembalikan false (artinya: GAGAL, jangan lanjut)
        return false;
    }
    
    // Jika ada token, kembalikan true (lanjutkan proses)
    return true;
}