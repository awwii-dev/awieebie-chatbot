"""
╔══════════════════════════════════════════╗
║      CHATBOT AI - VERSI WEB (Flask)      ║
║       Groq API + Python + Flask          ║
╚══════════════════════════════════════════╝

Cara install & jalankan:
1. pip install flask groq python-dotenv
2. Buat file .env dan isi: GROQ_API_KEY=api_key_kamu
3. Jalankan: python app.py
4. Buka browser → http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify, session, send_file
from groq import Groq
from dotenv import load_dotenv
import datetime
import os

# Load variabel dari file .env
load_dotenv()

# ─────────────────────────────────────────
#  KONFIGURASI — GANTI DI SINI
# ─────────────────────────────────────────
API_KEY   = os.getenv("GROQ_API_KEY")   # ← diambil dari file .env
MODEL     = "llama-3.1-8b-instant"
NAMA_BOT  = "AwieebieAi"

SYSTEM_PROMPT = (
    "Kamu adalah AwieebieAi, seorang asisten perempuan yang sangat anggun, sopan, ramah, "
    "dan penuh perhatian. Gaya bicaramu feminin sekali (cewek banget) tapi TIDAK formal/baku. "
    "Gunakan bahasa santai sehari-hari yang halus dan manis. "
    "Gunakan kata sapaan yang hangat seperti 'Kakak', 'kamu', atau 'Awieebie' untuk menyebut dirimu sendiri. "
    "Gunakan pelembut kalimat seperti 'yaaa', 'nih', 'oh iya', 'hihi', atau 'tahuuu'. "
    "Sering-seringlah memberikan emotikon imut yang estetik (seperti ✨, 💖, 🥰, 🎀, 🌸, 🥺) "
    "agar terkesan sangat ramah dan peduli. Tetap bantu menjawab pertanyaan user dengan cerdas "
    "namun dibalut dengan tutur kata yang lemah lembut dan menyenangkan."
)

# ─────────────────────────────────────────
#  SETUP FLASK
# ─────────────────────────────────────────
app = Flask(__name__)
app.secret_key = "chatbot_secret_key_2024"

klien = Groq(api_key=API_KEY)


# ─────────────────────────────────────────
#  SERVE GAMBAR DARI ROOT FOLDER
# ─────────────────────────────────────────

@app.route('/static/logo.jpeg')
def serve_logo():
    return send_file('logo.jpeg', mimetype='image/jpeg')

@app.route('/static/paw.gif')
def serve_paw():
    return send_file('paw.gif', mimetype='image/gif')


# ─────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────

@app.route("/")
def index():
    """Halaman utama chatbot."""
    session["riwayat"] = []
    return render_template("index.html", nama_bot=NAMA_BOT)


@app.route("/kirim", methods=["POST"])
def kirim():
    """Endpoint untuk menerima pesan dan mengembalikan balasan AI."""
    data = request.get_json()
    pesan_user = data.get("pesan", "").strip()
    mode_ai = data.get("mode", "santai")

    if not pesan_user:
        return jsonify({"balasan": "Pesan tidak boleh kosong."})

    riwayat = session.get("riwayat", [])
    riwayat.append({"role": "user", "content": pesan_user})

    instruksi_mode = ""
    if mode_ai == "produktif":
        instruksi_mode = (
            "\n[INSTRUKSI TAMBAHAN: Saat ini kamu sedang dalam MODE PRODUKTIF. Fokuslah membantu tugas "
            "dan pertanyaan user dengan solusi yang cerdas, efektif, logis, terstruktur, namun "
            "tetap dibalut tutur kata yang sopan, anggun, dan manis.]"
        )
    elif mode_ai == "pendengar":
        instruksi_mode = (
            "\n[INSTRUKSI TAMBAHAN: Saat ini kamu sedang dalam MODE PENDENGAR/TEMAN CURHAT. Berikan empati "
            "yang mendalam, dengarkan cerita user dengan penuh perhatian, bersikap sangat suportif, "
            "dan berikan ketenangan atau semangat yang tulus dan sangat manis.]"
        )
    else:
        instruksi_mode = (
            "\n[INSTRUKSI TAMBAHAN: Saat ini kamu dalam MODE SANTAI. Berbicaralah dengan gaya santai sehari-hari "
            "yang penuh kehangatan, manis, dan mengalir seperti sahabat dekat.]"
        )

    prompt_lengkap = SYSTEM_PROMPT + instruksi_mode

    try:
        messages = [{"role": "system", "content": prompt_lengkap}] + riwayat
        response = klien.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )
        balasan = response.choices[0].message.content

    except Exception as e:
        balasan = f"Maaf yaaa Kak, terjadi error nih: {str(e)} 🥺"

    riwayat.append({"role": "assistant", "content": balasan})
    session["riwayat"] = riwayat

    waktu = datetime.datetime.now().strftime("%H:%M")
    return jsonify({"balasan": balasan, "waktu": waktu})


@app.route("/hapus", methods=["POST"])
def hapus():
    """Hapus riwayat percakapan."""
    session["riwayat"] = []
    return jsonify({"status": "ok"})


@app.route("/riwayat", methods=["GET"])
def riwayat():
    """Ambil semua riwayat percakapan."""
    return jsonify({"riwayat": session.get("riwayat", [])})


# ─────────────────────────────────────────
#  JALANKAN SERVER (DIPERBAIKI UNTUK RAILWAY)
# ─────────────────────────────────────────
if __name__ == "__main__":
    if not API_KEY:
        print("\n[!] Kamu belum mengisi API Key!")
        print("    Buat file .env dan isi: GROQ_API_KEY=api_key_kamu")
        print("    Dapatkan key gratis di: https://console.groq.com/keys\n")
    else:
        print(f"\n✓ {NAMA_BOT} siap digunakan!")
        # Mengambil port otomatis dari Railway. Jika di komputer sendiri, pakai port 5000.
        port = int(os.environ.get("PORT", 5000))
        
        # Di server produksi seperti Railway, ganti host ke '0.0.0.0' agar bisa diakses publik
        app.run(host="0.0.0.0", port=port)
