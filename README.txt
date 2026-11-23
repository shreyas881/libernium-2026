LIBERNIUM 2026 — WEBSITE PROJECT
================================

EVENT IDENTITY
Official poster-inspired design using the original Liberati and CHRIST logos, university identification and LIBERNIUM 2026 wordmark.
Event date: 24 November 2026 | 9:00 AM–4:00 PM
Department: Department of Liberal Arts
Campus: CHRIST (Deemed to be University), Bangalore Bannerghatta Road Campus
Theme: Responsible Consumption & Production
Tagline: Building a Sustainable Future Through Conscious Choices

RUN ON WINDOWS / VS CODE
1. Extract this ZIP folder.
2. Open the extracted Libernium_2026_Updated folder in VS Code.
3. Open Terminal in that folder and run:
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
4. Open http://127.0.0.1:5000 in Chrome or Edge.

RUN ON macOS / LINUX
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   PORT=5050 python app.py
Then open http://127.0.0.1:5050. (macOS's AirPlay Receiver already uses port 5000,
so pick another port with PORT=..., or turn off AirPlay Receiver in System Settings.)

FEATURES
- Wide, white Home page with the Liberati logo, CHRIST logo, institutional heading and LIBERNIUM 2026 wordmark; no registration QR or extra poster content.
- No QR code, registration QR, Register Now button, or QR promotion block is displayed anywhere on the public website.
- Home page also shows the Researchers section below the banner. Separate pages/sections for Faculty & Team, Programme, Venues, Event Assistant and Concept Note.
- Concept Note remains its own independent page and is the final page in the website navigation and page order.
- The Researchers section on the Home page includes the five event contributors shown in the brochure.
- People profiles show names and professional roles only; internal photo-source notes and editorial comments are not displayed.
- Dr. Prerana Srimaal appears first in the faculty order. The rejected circular avatar is not used.
- Event schedule entries and venue cards include the confirmed floor labels: Mini Auditorium (Second Floor), Idea Nexus (Fourth Floor), Seminar Hall (First Floor), Auditorium Balcony (Second Floor), and Artisan Stalls near the additional entry gate.
- Event schedule, workshops, panel speakers, venue notes and concept note are stored in static/data/event.json.
- People information is stored in static/data/people.json.
- Event assistant uses verified local event data without requiring an API key. An optional OpenAI API key can enable live AI responses.

ENVIRONMENT SETUP
1. Copy .env.example to .env.
2. Set ADMIN_PASSWORD and FLASK_SECRET_KEY to your own private values.
3. Add OPENAI_API_KEY only if you want live AI responses.
4. Never share your .env file or passwords. This ZIP intentionally does not include a populated .env file.

PRIVATE ADMIN SCANNER
A password-protected scanner route exists at /admin/scanner for private admin use only. It is not linked from the public website and no QR scanner UI is displayed to event visitors. Set ADMIN_PASSWORD in your local .env before using it.

EDITING PEOPLE
Open static/data/people.json. Each profile supports name, role, group, photo and optional phone. Put portrait files in static/images/people/.

EDITING EVENT DETAILS
Open static/data/event.json. The schedule, workshops, speakers, venue notes, contact information and concept note are stored there.
