import json
import os
import re
from pathlib import Path
from flask import Flask, jsonify, render_template, render_template_string, request, session, redirect, url_for
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
DATA_DIR = BASE_DIR / "static" / "data"
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or os.urandom(32)


def load_json(filename):
    with (DATA_DIR / filename).open(encoding="utf-8") as handle:
        return json.load(handle)


TITLES = {"dr", "mr", "ms", "mrs", "prof"}


def has_any(text, terms):
    """Whole-word/phrase match, so 'gr' doesn't match 'great' and '1:00' doesn't match '11:00'."""
    return any(re.search(rf"(?<![\w:]){re.escape(term)}(?![\w:])", text) for term in terms)


def find_people(q, people):
    words = set(re.findall(r"[a-z]+", q))
    found = []
    for p in people:
        name_words = {w for w in re.findall(r"[a-z]+", p["name"].lower()) if len(w) > 2 and w not in TITLES}
        if words & name_words:
            found.append(p)
    return found


def local_answer(question, event, people):
    q = question.lower()
    found = find_people(q, people)
    if found:
        return "\n".join(f"{p['name']} — {p['role']}" + (f" · {p['phone']}" if p.get('phone') else "") for p in found)
    if has_any(q, ["1 pm", "1pm", "1:00", "workshop", "workshops"]):
        items = [x for x in event["schedule"] if "Workshop:" in x["title"]]
        return "The workshops run from 1:00 PM to 3:00 PM:\n" + "\n".join(f"• {x['title']} — {x['venue']} (Resource person: {x.get('people','Details not listed')})" for x in items)
    if has_any(q, ["panel", "cool", "speaker", "speakers", "panellist", "panellists", "panelist", "panelists"]):
        return "The panel discussion ‘The Cost of Being Cool’ is from 10:30 AM to 12:00 PM in the Mini Auditorium on the second floor. Speakers: " + "; ".join(event["panel"]["speakers"])
    if has_any(q, ["stall", "stalls", "artisan", "artisans", "weaving", "leatherwork"]):
        return "Artisan Stalls & Demonstrations run from 12:00 PM to 2:30 PM outside the campus near the additional entry gate. When entering campus, take the left-side route; the stalls are arranged just before that gate."
    if has_any(q, ["where", "venue", "location", "floor", "direction", "directions", "venues", "auditorium"]):
        return "Venue guide:\n" + "\n".join(f"• {v['place']}: {v['detail']}" for v in event["venue_notes"])
    if has_any(q, ["date", "when", "time", "day", "schedule", "programme"]):
        return f"LIBERNIUM 2026 takes place on {event['date']}, from {event['time']}, at {event['venue']}. See the Programme section for the full schedule."
    if has_any(q, ["theme", "about", "libernium", "concept", "objective", "objectives"]):
        return f"The theme is {event['theme']}. The tagline is ‘{event['tagline']}’. {event['about']}"
    if has_any(q, ["registration", "fee", "register", "certificate"]):
        reg = event["registration"]
        return f"Registration is open to {reg['openTo']}. The brochure states a workshop registration fee of {reg['fee']}. {reg['certificate']} For details, contact {reg['email']}."
    if has_any(q, ["contact", "email", "phone", "coordinator", "coordinators"]):
        return f"For event enquiries, contact {event['contact']['email']}. Student coordinators: Jiyaa P. Shah (GR), +91 84310 13872; Sifat Puri, +91 92166 66136."
    if has_any(q, ["faculty", "phd", "scholar", "research", "people", "who", "team"]):
        return "The Faculty & Team section contains the supplied faculty, PhD scholar, event guest and student coordinator profiles. Dr. Embassy Lawbei is listed as Overall Event Coordinator."
    return "I can help with the event date, programme, workshops, panel speakers, artisan stalls, venues, registration information and people. Try asking ‘Where are the artisan stalls?’ or ‘What happens at 1 PM?’"


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/api/ask")
def ask():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()[:1200]
    if not question:
        return jsonify({"answer": "Please enter a question about LIBERNIUM 2026."}), 400
    event = load_json("event.json")
    people = load_json("people.json")

    # Optional live AI: the key stays on the server and is never sent to the browser.
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            response = client.responses.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
                instructions=(
                    "You are the LIBERNIUM 2026 event assistant. Answer only from the supplied event and people data. "
                    "Do not invent dates, names, venues, roles or timings. If a detail is missing or ambiguous, say so. "
                    "Be concise, friendly and helpful. No registration or payment workflow is performed on this site.\n\n"
                    f"EVENT DATA:\n{json.dumps(event, ensure_ascii=False)}\n\nPEOPLE DATA:\n{json.dumps(people, ensure_ascii=False)}"
                ),
                input=question,
                max_output_tokens=350,
            )
            return jsonify({"answer": response.output_text, "mode": "ai"})
        except Exception as exc:
            app.logger.warning("AI response unavailable; using verified local answer: %s", exc)

    return jsonify({"answer": local_answer(question, event, people), "mode": "verified-data"})



PRIVATE_SCANNER_HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Private QR Scanner · LIBERNIUM</title><script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script><style>body{margin:0;background:#f7f4ec;color:#25152d;font:15px Arial,sans-serif;padding:28px}.wrap{max-width:760px;margin:30px auto;background:#fff;padding:28px;border-top:5px solid #4b1268;box-shadow:0 12px 45px #21152a18}h1{color:#4b1268}button,input{font:inherit;padding:12px;border-radius:8px;border:1px solid #cfc3d4}button{background:#4b1268;color:white;cursor:pointer;margin:6px 6px 6px 0}#qr-reader{max-width:520px;min-height:250px;margin:20px auto;background:#f5f1f6}#result{overflow-wrap:anywhere;background:#f1f4eb;padding:14px;margin-top:16px}.muted{color:#6f6872;font-size:13px}</style></head><body><main class="wrap"><p><b>LIBERNIUM 2026 · PRIVATE ADMIN TOOL</b></p><h1>Private QR Scanner</h1><p class="muted">This page is not linked or displayed on the public website. Access is password-protected.</p><div id="qr-reader"></div><button id="start">Start camera</button><button id="stop">Stop camera</button><label><input id="file" type="file" accept="image/*"> Upload QR image</label><div id="result">No QR code scanned yet.</div><p><a href="/admin/logout">Log out</a> · <a href="/">Public website</a></p></main><script>let scanner=null;const result=document.getElementById('result');document.getElementById('start').onclick=async()=>{try{if(!scanner)scanner=new Html5Qrcode('qr-reader');await scanner.start({facingMode:'environment'},{fps:10,qrbox:240},async text=>{result.textContent=text;try{await scanner.stop()}catch(e){}})}catch(e){result.textContent='Camera unavailable. Use HTTPS/localhost and allow camera permission.'}};document.getElementById('stop').onclick=async()=>{if(scanner){try{await scanner.stop()}catch(e){}}};document.getElementById('file').onchange=async e=>{if(!e.target.files[0])return;try{if(!scanner)scanner=new Html5Qrcode('qr-reader');result.textContent=await scanner.scanFile(e.target.files[0],true)}catch(err){result.textContent='No readable QR code found in that image.'}e.target.value=''};</script></body></html>"""

@app.route("/admin/scanner", methods=["GET", "POST"])
def private_scanner():
    password = os.getenv("ADMIN_PASSWORD", "").strip()
    if not password or password.startswith("replace-with"):
        return ("Private scanner is disabled. Set ADMIN_PASSWORD in the .env file, then restart the app.", 503)
    if session.get("private_scanner_authenticated") is True:
        return render_template_string(PRIVATE_SCANNER_HTML)
    if request.method == "POST":
        supplied = str(request.form.get("password", ""))
        import hmac
        if hmac.compare_digest(supplied, password):
            session["private_scanner_authenticated"] = True
            return redirect(url_for("private_scanner"))
        return render_template_string("""<html><body style='font-family:Arial;background:#f7f4ec;padding:30px'><h2>Private LIBERNIUM Scanner</h2><p style='color:#a22'>Incorrect password.</p><form method='post'><input name='password' type='password' placeholder='Admin password' required><button>Enter</button></form></body></html>""")
    return render_template_string("""<!doctype html><html><meta name='viewport' content='width=device-width,initial-scale=1'><body style='font-family:Arial;background:#f7f4ec;padding:30px'><main style='max-width:420px;margin:10vh auto;background:white;padding:28px;border-top:5px solid #4b1268'><h2 style='color:#4b1268'>Private LIBERNIUM Scanner</h2><p>Admin access only.</p><form method='post'><input name='password' type='password' placeholder='Admin password' required style='padding:12px;width:90%'><p><button style='padding:12px 20px;background:#4b1268;color:white;border:0'>Enter</button></p></form></main></body></html>""")

@app.get("/admin/logout")
def private_scanner_logout():
    session.pop("private_scanner_authenticated", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    # macOS uses port 5000 for AirPlay Receiver, so the port can be changed: PORT=5050 python app.py
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=False)
