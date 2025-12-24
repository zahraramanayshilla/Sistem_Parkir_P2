// =====================================================
// SOCKET.IO CLIENT — REALTIME DASHBOARD PARKIR
// =====================================================
const socket = io();
const tbody = document.getElementById("riwayat-body");

// =====================================================
// LOAD DATA AWAL DARI MONGODB (PERSISTEN)
// =====================================================
if (tbody) {
    fetch("/api/riwayat-parkir")
        .then(res => res.json())
        .then(rows => {
            rows.forEach(data => {
                const warna =
                    data.status === "MASUK" ? "text-green-600" : "text-blue-600";

                const tr = document.createElement("tr");
                tr.dataset.key = `${data.npm}-${data.waktu}`;

                tr.innerHTML = `
                    <td class="px-3 py-3 border-t">${data.waktu}</td>
                    <td class="px-3 py-3 border-t font-semibold ${warna}">
                        ${data.status}
                    </td>
                    <td class="px-3 py-3 border-t">${data.npm}</td>
                    <td class="px-3 py-3 border-t">${data.nama}</td>
                    <td class="px-3 py-3 border-t">${data.durasi}</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Gagal load riwayat:", err));
}

// =====================================================
// REALTIME UPDATE (SCAN BARU)
// =====================================================
socket.on("qr_update", (data) => {
    if (!tbody) return;
    if (!["MASUK", "KELUAR"].includes(data.status)) return;

    const key = `${data.npm}-${data.waktu}`;
    if (document.querySelector(`[data-key="${key}"]`)) return;

    const warna =
        data.status === "MASUK" ? "text-green-600" : "text-blue-600";

    const tr = document.createElement("tr");
    tr.dataset.key = key;

    tr.innerHTML = `
        <td class="px-3 py-3 border-t">${data.waktu}</td>
        <td class="px-3 py-3 border-t font-semibold ${warna}">
            ${data.status}
        </td>
        <td class="px-3 py-3 border-t">${data.npm}</td>
        <td class="px-3 py-3 border-t">${data.nama}</td>
        <td class="px-3 py-3 border-t">${data.durasi}</td>
    `;

    tbody.prepend(tr);
});

// =====================================================
// STATISTIK DASHBOARD (REALTIME)
// =====================================================
socket.on("stats_update", (stats) => {
    const terpakaiEl = document.getElementById("slot-terpakai");
    const tersediaEl = document.getElementById("slot-tersedia");
    const rataEl = document.getElementById("rata-rata");

    if (terpakaiEl) terpakaiEl.innerText = stats.sedang_di_dalam ?? "-";
    if (tersediaEl)
        tersediaEl.innerText = 250 - (stats.sedang_di_dalam ?? 0);
    if (rataEl) rataEl.innerText = stats.rata_rata_str ?? "—";
});

// =====================================================
// STATUS SISTEM (READY / VALID / INVALID)
// =====================================================
const systemStatusEl = document.getElementById("system-status");
const activityLogEl = document.getElementById("activity-log");


function addActivityLog(iconBg, icon, title, desc, titleColor) {
    if (!activityLogEl) return;

    const time = new Date().toLocaleTimeString("id-ID", {
        hour: "2-digit",
        minute: "2-digit",
    });

    const div = document.createElement("div");
    div.className = "flex items-start gap-3";

    div.innerHTML = `
        <div class="${iconBg} p-2 rounded-full ${titleColor}">
            <i class="${icon} text-xs"></i>
        </div>
        <div>
            <p class="font-semibold ${titleColor}">${title}</p>
            <p class="text-xs text-gray-500">${desc} • ${time}</p>
        </div>
    `;

    activityLogEl.prepend(div);

    // batasi agar tidak numpuk
    if (activityLogEl.children.length > 6) {
        activityLogEl.removeChild(activityLogEl.lastChild);
    }
}


socket.on("qr_status", (data) => {
    if (!systemStatusEl) return;

    switch (data.status) {
        case "READY":
            systemStatusEl.innerHTML = `
                <span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span>
                Perangkat siap digunakan
            `;
            addActivityLog(
                "bg-blue-100",
                "fa-solid fa-video",
                "Kamera Aktif",
                "ESP32 siap digunakan",
                "text-blue-700"
            );
            break;

        case "VALID":
            systemStatusEl.innerHTML = `
                <span class="w-2.5 h-2.5 rounded-full bg-green-500"></span>
                Akses diterima
            `;
            addActivityLog(
                "bg-green-100",
                "fa-solid fa-arrow-right-to-bracket",
                "Motor Masuk",
                data.nama,
                "text-green-700"
            );
            break;

        case "INVALID":
            systemStatusEl.innerHTML = `
                <span class="w-2.5 h-2.5 rounded-full bg-red-500"></span>
                QR tidak valid
            `;
            addActivityLog(
                "bg-red-100",
                "fa-solid fa-triangle-exclamation",
                "QR Tidak Valid",
                "Scan ditolak",
                "text-red-600"
            );
            break;
    }
});

// =====================================================
// DROPDOWN NOTIFIKASI (BELL)
// =====================================================
const notifBtn = document.getElementById("notifBtn");
const notifDropdown = document.getElementById("notifDropdown");
const notifList = document.getElementById("notifList");
const notifCount = document.getElementById("notifCount");

let unreadNotif = 0;

notifBtn?.addEventListener("click", () => {
    notifDropdown.classList.toggle("hidden");
    unreadNotif = 0;
    updateNotifCount();
});

function updateNotifCount() {
    if (!notifCount) return;

    if (unreadNotif > 0) {
        notifCount.classList.remove("hidden");
        notifCount.innerText = unreadNotif;
    } else {
        notifCount.classList.add("hidden");
    }
}

function addNotification(title, desc, color) {
    if (!notifList) return;

    const time = new Date().toLocaleTimeString("id-ID", {
        hour: "2-digit",
        minute: "2-digit",
    });

    const li = document.createElement("li");
    li.className = "px-4 py-3 border-b hover:bg-blue-50";

    li.innerHTML = `
        <div class="font-semibold ${color}">${title}</div>
        <div class="text-xs text-gray-500">${desc} • ${time}</div>
    `;

    notifList.prepend(li);
    unreadNotif++;
    updateNotifCount();
}

// =====================================================
// AUTO CLOSE DROPDOWN SAAT KLIK DI LUAR
// =====================================================
document.addEventListener("click", (e) => {
    if (!notifBtn || !notifDropdown) return;

    if (
        !notifBtn.contains(e.target) &&
        !notifDropdown.contains(e.target)
    ) {
        notifDropdown.classList.add("hidden");
    }
});

// =====================================================
// STATUS KONEKSI SOCKET
// =====================================================
socket.on("connect", () => {
    console.log("🔌 Socket.IO connected:", socket.id);
});

socket.on("disconnect", () => {
    console.log("🔌 Socket.IO disconnected");
});
