import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getFirestore, doc, getDoc, setDoc, collection, query, orderBy, onSnapshot, enableIndexedDbPersistence } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";

// ARCHITECTURE: Key injection placeholder for GitHub Actions
const GEMINI_API_KEY = "AIzaSyBLGx6dSsSS698lcDLHyMUmKTORP5Ju9ts";

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