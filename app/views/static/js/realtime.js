// =====================================================
// SOCKET.IO CLIENT — REALTIME DASHBOARD PARKIR
// =====================================================

// Pastikan socket.io sudah diload sebelum file ini
// <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>

const socket = io();   // koneksi ke Flask SocketIO
const tbody = document.getElementById("riwayat-body");

// =====================================================
// EVENT: QR UPDATE (MASUK / KELUAR)
// =====================================================
socket.on("qr_update", (data) => {
    console.log("QR UPDATE:", data);

    if (!tbody) {
        console.warn("Element #riwayat-body tidak ditemukan");
        return;
    }

    // Buat baris baru
    const tr = document.createElement("tr");
    tr.className = "hover:bg-blue-50";

    tr.innerHTML = `
    <td class="px-3 py-3 border-t">${data.waktu}</td>
    <td class="px-3 py-3 border-t">${data.status}</td>
    <td class="px-3 py-3 border-t">${data.npm}</td>
    <td class="px-3 py-3 border-t">${data.nama}</td>
    <td class="px-3 py-3 border-t">${data.durasi}</td>
  `;

    // Tambahkan ke baris PALING ATAS
    tbody.prepend(tr);
});

// =====================================================
// EVENT: UPDATE STATISTIK DASHBOARD
// =====================================================
socket.on("stats_update", (stats) => {
    console.log("STATS UPDATE:", stats);

    // Contoh update card dashboard
    const terpakaiEl = document.getElementById("slot-terpakai");
    const tersediaEl = document.getElementById("slot-tersedia");
    const rataEl = document.getElementById("rata-rata");

    if (terpakaiEl) terpakaiEl.innerText = stats.terpakai;
    if (tersediaEl) tersediaEl.innerText = stats.tersedia;
    if (rataEl) rataEl.innerText = stats.rata_rata_str;
});

// =====================================================
// EVENT: ERROR QR (QR TIDAK VALID / USER TIDAK ADA)
// =====================================================
socket.on("qr_error", (err) => {
    console.error("QR ERROR:", err);

    alert(err.pesan || "Terjadi kesalahan saat memproses QR");
});

// =====================================================
// OPTIONAL: LOG SAAT TERKONEKSI
// =====================================================
socket.on("connect", () => {
    console.log("🔌 Socket.IO connected:", socket.id);
});

socket.on("disconnect", () => {
    console.log("🔌 Socket.IO disconnected");
});
