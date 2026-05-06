# Gemini Blind Timer 🧠⏳

![License](https://img.shields.io/badge/license-MIT-blue)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Gemini AI](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-purple)

## 📖 The Story
This project was born out of a real-world problem: solving my wife's study workflow. She prefers a "blind" study method where the timer duration is unpredictable, forcing deeper focus and removing the distraction of clock-watching. **Gemini Blind Timer** automates this by using Google's Gemini AI to roll unpredictable time intervals, wrapped in a professional-grade study tracker.

---

## 🚀 Interview Highlights (Technical Specs)

### 🤖 Generative AI Integration
The core randomization is handled by the **Gemini 2.5 Flash** model. Unlike standard `Math.random()`, this integrates a real-world LLM to determine study durations, showcasing proficiency in RESTful AI API consumption.

### 🛡️ Secure CI/CD & Secret Management
To prevent GitHub's secret scanners from revoking API keys, I implemented a custom **Base64 injection pipeline**:
- The production API key is stored as a GitHub Secret.
- The GitHub Actions workflow (`deploy.yml`) encodes the key and uses `sed` to inject it into the production build during deployment.
- This ensures the source code remains clean and secure for public portfolio viewing.

### 🐍 Python Logic Validation
While the frontend is JavaScript, the core business logic (aggregation, monthly grouping, and boundary math) is validated by a **Python 3.11** test suite using `pytest`.
- **Pre-commit Hooks:** Tests run locally before every commit.
- **Deployment Gate:** The CI/CD pipeline executes the full test suite; if any logic check fails, the deployment to GitHub Pages is automatically aborted.

### 🔥 Serverless Architecture
- **Frontend:** Vanilla JS / HTML5 / CSS3.
- **Database:** Firebase Firestore (Real-time synchronization).
- **Hosting:** GitHub Pages.

---

## 🛠️ Tech Stack
- **Frontend:** HTML5, CSS3, Vanilla JavaScript.
- **AI:** Google Gemini 2.5 Flash API.
- **Backend/DB:** Firebase Firestore.
- **DevOps:** GitHub Actions, Git Hooks.
- **Testing:** Python 3.11, Pytest.

---

## ⚙️ CI/CD Workflow
1. **Developer Pushes Code**
2. **GitHub Actions Triggers**
3. **Environment Setup** (Python + Dependencies)
4. **Logic Validation** (Running `pytest`)
5. **Secret Injection** (Gemini API Key Base64 encoding)
6. **Deploy** (Push to `gh-pages` branch)

---

## 🎨 UI Design
Designed with a "Focus-First" aesthetic:
- **Dark Mode** default to reduce eye strain.
- **Glassmorphic** UI elements.
- **Dynamic Progress Ring** (SVG-based).
- **Endless Alarm** with manual "Stop to Save" trigger for focused study cycles.

---

## 🔮 Future Roadmap
Even as a completed MVP, there are clear paths for architectural scaling:
- **High-Precision Analytics:** Transition the database schema from rounded minutes to raw Unix timestamps/total seconds to provide millisecond-accurate study reporting.
- **AI-Driven Coaching:** Utilize Gemini's long-context window to analyze study patterns over months and provide personalized focus coaching.
- **Native Notifications:** Integrate Web Push API to provide focus reminders even when the browser tab is backgrounded.

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
