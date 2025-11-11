from fastapi import FastAPI, WebSocket, WebSocketDisconnect # type: ignore
from fastapi.responses import JSONResponse, PlainTextResponse # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from pydantic import BaseModel, Field # type: ignore
from typing import Optional, Set
import asyncio, json, random
from datetime import datetime, timedelta
from fastapi.staticfiles import StaticFiles # type: ignore


app = FastAPI(title="Kampus Parkir WS + REST")
app.mount("/", StaticFiles(directory="public", html=True), name="static")


# --- CORS: izinkan akses dari dev server (live server, dll) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # batasi ke domain kamu di production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====== STATE ======
state = {
    "stats": {"total": 250, "available": 178, "used": 72, "avgDuration": "1j 42m"},
    "slots": [
        {"id":"A-01","status":"free","meta":"Dekat gerbang"},
        {"id":"A-02","status":"busy","meta":"Terisi • 45m"},
        {"id":"A-03","status":"reserved","meta":"Reservasi"},
        {"id":"A-04","status":"free","meta":"Tersedia"},
        {"id":"A-05","status":"free","meta":"Tersedia"},
        {"id":"A-06","status":"busy","meta":"Terisi • 12m"},
        {"id":"B-01","status":"free","meta":"Tersedia"},
        {"id":"B-02","status":"busy","meta":"Terisi • 2j"},
        {"id":"B-03","status":"reserved","meta":"Reservasi"},
        {"id":"B-04","status":"free","meta":"Tersedia"},
        {"id":"B-05","status":"free","meta":"Tersedia"},
        {"id":"B-06","status":"busy","meta":"Terisi • 28m"},
    ],
    "history": [
        {"time":"07:42","type":"Masuk","npm":"21.11.1234","plate":"D 1234 GIL","area":"Gerbang Utama","duration":"—"},
        {"time":"08:05","type":"Masuk","npm":"22.22.5678","plate":"D 5678 ULB","area":"Gedung A","duration":"—"},
        {"time":"10:13","type":"Keluar","npm":"21.11.1234","plate":"D 1234 GIL","area":"Gerbang Utama","duration":"2j 31m"},
    ],
    "summary": {"in":"08:05","duration":"2j 31m"}
}

# penyimpanan check-in aktif: key = npm (atau tiket id), value = datetime masuk
checkins: dict[str, dict] = {}

# ====== UTIL ======
def now_str() -> str:
    return datetime.now().strftime("%H:%M")

def human_duration(delta: timedelta) -> str:
    total_minutes = int(delta.total_seconds() // 60)
    h, m = divmod(total_minutes, 60)
    if h and m: return f"{h}j {m}m"
    if h: return f"{h}j"
    return f"{m}m"

def cap_history():
    # simpan maksimum 200 baris riwayat agar tak membengkak
    if len(state["history"]) > 200:
        state["history"][:] = state["history"][-200:]

async def broadcast(payload: dict):
    data = json.dumps(payload)
    dead = []
    for ws in clients:
        try:
            await ws.send_text(data)
        except Exception:
            dead.append(ws)
    for ws in dead:
        clients.discard(ws)

# ====== WEBSOCKET ======
clients: Set[WebSocket] = set()

@app.websocket("/ws/parkir")
async def ws_parkir(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        # kirim state awal
        await ws.send_text(json.dumps(state))
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except Exception:
                continue
            if msg.get("type") == "ping":
                await ws.send_text(json.dumps({"type": "pong", "ts": datetime.now().isoformat()}))
    except WebSocketDisconnect:
        clients.discard(ws)

# ====== REST MINIMAL ======
@app.get("/")
async def root():
    return PlainTextResponse("Parkir WS OK")

@app.get("/api/state")
async def current_state():
    return JSONResponse(state)

# Payload masuk/keluar
class ScanMasuk(BaseModel):
    npm: str = Field(..., description="ID/NPM pengguna")
    plate: Optional[str] = Field(None, description="Nomor polisi")
    area: Optional[str] = Field("Gerbang Utama")
    time: Optional[str] = Field(None, description="Override waktu HH:MM (opsional)")

class ScanKeluar(BaseModel):
    npm: str
    time: Optional[str] = None  # HH:MM
    area: Optional[str] = None

@app.post("/api/scan/masuk")
async def scan_masuk(data: ScanMasuk):
    t = data.time or now_str()
    # simpan checkin
    checkins[data.npm] = {"time": datetime.now(), "area": data.area, "plate": data.plate}
    # tambah ke riwayat
    state["history"].append({
        "time": t, "type": "Masuk", "npm": data.npm, "plate": data.plate or "—",
        "area": data.area or "—", "duration": "—"
    })
    cap_history()
    # (opsional) update statistik & slot acak buat demo
    # tandai satu slot jadi busy
    free_slots = [s for s in state["slots"] if s["status"] == "free"]
    if free_slots:
        random.choice(free_slots)["status"] = "busy"
    used = sum(1 for s in state["slots"] if s["status"] == "busy")
    state["stats"]["used"] = used
    state["stats"]["available"] = state["stats"]["total"] - used

    # broadcast ke semua klien
    await broadcast({"history": state["history"], "stats": state["stats"], "slots": state["slots"]})
    return {"ok": True}

@app.post("/api/scan/keluar")
async def scan_keluar(data: ScanKeluar):
    t = data.time or now_str()
    # cari checkin
    ci = checkins.pop(data.npm, None)
    duration_txt = "—"
    if ci:
        delta = datetime.now() - ci["time"]
        duration_txt = human_duration(delta)
    # tambah ke riwayat keluar
    state["history"].append({
        "time": t, "type": "Keluar", "npm": data.npm, "plate": ci["plate"] if ci else "—",
        "area": (data.area or ci["area"]) if ci else (data.area or "—"),
        "duration": duration_txt
    })
    cap_history()

    # (opsional) ringkasan untuk panel 'Keluar'
    state["summary"] = {"in": ci["time"].strftime("%H:%M") if ci else "—", "duration": duration_txt}

    # (opsional) bebaskan slot acak untuk demo
    busy_slots = [s for s in state["slots"] if s["status"] == "busy"]
    if busy_slots:
        random.choice(busy_slots)["status"] = "free"
    used = sum(1 for s in state["slots"] if s["status"] == "busy")
    state["stats"]["used"] = used
    state["stats"]["available"] = state["stats"]["total"] - used

    await broadcast({
        "history": state["history"],
        "summary": state["summary"],
        "stats": state["stats"],
        "slots": state["slots"],
    })
    return {"ok": True, "summary": state["summary"]}

# ====== SIMULASI OTOMATIS (bisa dimatikan kalau sudah real) ======
async def demo_updater():
    # jalankan rotasi kecil tiap 15 dtk agar terlihat hidup
    while True:
        idx = random.randrange(len(state["slots"]))
        before = state["slots"][idx]["status"]
        state["slots"][idx]["status"] = "free" if before == "busy" else "busy"
        used = sum(1 for s in state["slots"] if s["status"] == "busy")
        state["stats"]["used"] = used
        state["stats"]["available"] = state["stats"]["total"] - used
        await broadcast({"slots": state["slots"], "stats": state["stats"]})
        await asyncio.sleep(15)

@app.on_event("startup")
async def on_start():
    # boleh dimatikan: demo bergerak
    asyncio.create_task(demo_updater())
