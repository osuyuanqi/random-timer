import os

# Create directory structure
folders = ["css", "js", ".github/workflows"]
for folder in folders:
    os.makedirs(folder, exist_ok=True)

files = {
    # 1. CLEAN HTML
    "index.html": """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Random Timer Pro | AI Integrated</title>
    <link rel="stylesheet" href="css/style.css">
    <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@800&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <h1 class="logo">RANDOM TIMER</h1>
        <div id="monthBadge" class="badge">...</div>
    </header>

    <main class="timer-container">
        <div class="clock-wrap">
            <svg viewBox="0 0 100 100">
                <circle class="track" cx="50" cy="50" r="44"/>
                <circle id="progressRing" class="progress" cx="50" cy="50" r="44"/>
            </svg>
            <div class="time-display">
                <div id="digits" class="digits">00:00:00</div>
                <div class="label">REMAINING</div>
            </div>
        </div>

        <div id="status" class="status-pill">IDLE</div>
        <p id="chosenLabel" class="ai-info">&nbsp;</p>

        <div class="controls">
            <button id="startBtn" class="btn-primary">▶ START</button>
            <button id="resetBtn" class="btn-secondary">↺ RESET</button>
        </div>
    </main>

    <section class="history-container">
        <h3>Session History</h3>
        <table>
            <thead><tr><th>Date</th><th>Timers</th><th>Daily Total</th></tr></thead>
            <tbody id="historyBody"></tbody>
        </table>
    </section>

    <!-- Project logic bundled as a module -->
    <script type="module" src="js/timer.js"></script>
</body>
</html>
""",

    # 2. SEPARATED CSS
    "css/style.css": """
:root {
    --bg: #0f0f0f; --text: #f0ece4; --accent: #e8c547;
    --border: #2e2e2e; --surface: #1a1a1a; --muted: #6b6560;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    background: var(--bg); color: var(--text);
    font-family: 'DM Mono', monospace;
    display: flex; flex-direction: column; align-items: center;
    padding: 40px 20px; min-height: 100vh;
}
.logo { font-family: 'Syne', sans-serif; letter-spacing: -1px; margin-bottom: 5px; }
.badge { font-size: 0.6rem; color: var(--muted); border: 1px solid var(--border); padding: 4px 12px; border-radius: 20px; margin-bottom: 20px; }
.clock-wrap { position: relative; width: 240px; height: 240px; }
svg { transform: rotate(-90deg); width: 100%; height: 100%; }
.track { fill: none; stroke: var(--border); stroke-width: 5; }
.progress { 
    fill: none; stroke: var(--accent); stroke-width: 5; 
    stroke-dasharray: 276.46; stroke-dashoffset: 0;
    transition: stroke-dashoffset 1s linear; 
}
.time-display { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.digits { font-size: 2.2rem; font-weight: 500; }
.label { font-size: 0.5rem; color: var(--muted); letter-spacing: 2px; }
.status-pill { margin-top: 20px; font-size: 0.7rem; color: var(--accent); letter-spacing: 1px; }
.ai-info { font-size: 0.8rem; margin: 10px 0; min-height: 1.2rem; color: var(--muted); }
.controls { display: flex; gap: 15px; margin-top: 10px; }
button { font-family: inherit; font-weight: bold; padding: 14px 28px; border-radius: 8px; cursor: pointer; border: none; transition: 0.2s; }
.btn-primary { background: var(--accent); color: #000; }
.btn-secondary { background: var(--surface); color: var(--text); border: 1px solid var(--border); }
button:hover { opacity: 0.9; transform: translateY(-1px); }
.history-container { width: 100%; max-width: 600px; margin-top: 50px; background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 20px; }
table { width: 100%; border-collapse: collapse; font-size: 0.75rem; margin-top: 15px; }
th { text-align: left; color: var(--muted); padding-bottom: 10px; border-bottom: 1px solid var(--border); }
td { padding: 12px 0; border-bottom: 1px solid var(--border); }
""",

    # 3. SEPARATED JS (WITH PLACEHOLDER LOGIC)
    "js/timer.js": """
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getFirestore, doc, getDoc, setDoc, collection, query, orderBy, onSnapshot, enableIndexedDbPersistence } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";

// ARCHITECTURE: Key injection placeholder for GitHub Actions
const GEMINI_API_KEY = "__GEMINI_API_KEY_PLACEHOLDER__";

const FIREBASE_CONFIG = {
    apiKey: "AIzaSyB7iC9fWtvJMWpVZPIsC6EHcBWrWZ4UIec",
    authDomain: "random-timer-df0e3.firebaseapp.com",
    projectId: "random-timer-df0e3",
    storageBucket: "random-timer-df0e3.firebasestorage.app",
    messagingSenderId: "191030765693",
    appId: "1:191030765693:web:514f83ae69eaf669a32914"
};

// 1. Database Setup
const app = initializeApp(FIREBASE_CONFIG);
const db = getFirestore(app);
enableIndexedDbPersistence(db).catch(() => console.warn("Offline sync active."));

// 2. Logic Helpers
const calcMax = () => 90 + Math.max(0, ((new Date().getFullYear() - 2026) * 12 + (new Date().getMonth() + 1 - 5))) * 30;

async function getSeconds() {
    const maxSecs = calcMax() * 60;
    
    // Check if key was injected by CI/CD
    if (GEMINI_API_KEY && !GEMINI_API_KEY.includes("PLACEHOLDER")) {
        try {
            document.getElementById('status').innerText = 'AI CONSULTING...';
            const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GEMINI_API_KEY}`;
            const resp = await fetch(url, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ contents: [{ parts: [{ text: `Pick random integer between 1 and ${maxSecs}. Return only number.` }] }] })
            });
            const data = await resp.json();
            const val = parseInt(data.candidates[0].content.parts[0].text.trim());
            if (!isNaN(val)) {
                document.getElementById('chosenLabel').innerHTML = `AI ROLLED: <b>${val}s</b>`;
                return val;
            }
        } catch (e) { console.error("AI Fallback triggered"); }
    }
    
    const local = Math.floor(Math.random() * maxSecs) + 1;
    document.getElementById('chosenLabel').innerHTML = `LOCAL ROLL: <b>${local}s</b>`;
    return local;
}

// 3. UI State
let totalSec = 0, remaining = 0, running = false, timerInterval = null;

const tick = () => {
    if (remaining <= 0) {
        clearInterval(timerInterval);
        document.getElementById('status').innerText = "DONE";
        document.getElementById('startBtn').innerText = '▶ NEW';
        return;
    }
    remaining--;
    document.getElementById('digits').innerText = new Date(remaining * 1000).toISOString().substr(11, 8);
    document.getElementById('progressRing').style.strokeDashoffset = 276.46 * (1 - (remaining/totalSec));
};

window.handleStart = async () => {
    if (running) {
        clearInterval(timerInterval);
        running = false;
        document.getElementById('startBtn').innerText = '▶ START';
        return;
    }
    if (remaining <= 0) {
        totalSec = await getSeconds();
        remaining = totalSec;
        saveToDB(totalSec);
    }
    running = true;
    document.getElementById('startBtn').innerText = '⏸ PAUSE';
    document.getElementById('status').innerText = 'RUNNING';
    timerInterval = setInterval(tick, 1000);
};

const saveToDB = async (s) => {
    const key = new Date().toISOString().slice(0, 10);
    const ref = doc(db, "sessions", key);
    const m = Math.ceil(s/60);
    const snap = await getDoc(ref);
    const timers = snap.exists() ? (snap.data().timers || []) : [];
    timers.push(m);
    await setDoc(ref, { date: key, timers, total: timers.reduce((a,b)=>a+b, 0) });
};

// 4. Initialization
document.getElementById('monthBadge').innerText = `LIMIT: ${calcMax()} MIN`;
document.getElementById('startBtn').onclick = window.handleStart;
document.getElementById('resetBtn').onclick = () => location.reload();

onSnapshot(query(collection(db, "sessions"), orderBy("date", "desc")), (snap) => {
    document.getElementById('historyBody').innerHTML = snap.docs.map(d => {
        const r = d.data();
        return `<tr><td>${r.date}</td><td>${r.timers.join(', ')}m</td><td><b>${r.total}m</b></td></tr>`;
    }).join('');
});
""",

    # 4. GITHUB ACTIONS WORKFLOW (THE CI/CD SECRET INJECTOR)
    ".github/workflows/deploy.yml": """
name: Deploy Secure Timer
on:
  push:
    branches: [ main ]
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Inject Gemini API Key
        run: |
          sed -i "s/__GEMINI_API_KEY_PLACEHOLDER__/${{ secrets.GEMINI_API_KEY }}/g" js/timer.js

      - name: Deploy to GitHub Pages
        uses: JamesIves/github-pages-deploy-action@v4
        with:
            folder: .
            branch: gh-pages
"""
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"Generated: {path}")

print("\nArchitecture Ready. Next Steps for Strategy B:")
print("1. Create a GitHub Repo and push these files.")
print("2. In GitHub: Settings > Secrets and variables > Actions.")
print("3. Add 'New repository secret' named GEMINI_API_KEY (value from AI Studio).")
print("4. The Action will automatically inject the key and deploy a 'Smooth' version for your wife.")