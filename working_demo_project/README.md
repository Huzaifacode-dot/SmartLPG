# Smart Gas Refill Predictor (Local Working Backup)

This folder contains a complete local clone and backup of **[Smart Gas Refill Predictor](https://smart-gas-refill-predictor.vercel.app/)** (originally authored by Enoch Oyewo).

## 🎯 Purpose
1. **Offline / Permanent Backup**: Guarantees we have a working, permanent copy even if the Vercel deployment goes offline or changes.
2. **Project Reference**: Serves as a reference implementation alongside our **SmartLPG** societal mini-project.

## 🚀 How to Run Locally

### Option 1: Python (Recommended, Zero Dependencies)
Run the bundled server launcher:
```bash
python serve.py
```
Then open your browser at:
```
http://127.0.0.1:8080/
```

### Option 2: Python Simple HTTP Server
```bash
python -m http.server 8080
```

### Option 3: Node.js / NPX
```bash
npx serve -s . -p 8080
```

---

## 📁 File Structure
```
working_demo_project/
├── index.html                   # Core single-page application entry point
├── assets/
│   ├── index-Co7s4JfJ.js        # Bundled React application logic and calculation engine
│   └── index-CLFXTPwS.css       # Tailwind & custom CSS stylesheet
├── manifest.json                # PWA web manifest
├── robots.txt                   # Search crawler directives
├── sitemap.xml                  # XML sitemap
├── serve.py                     # Python local development server
├── package.json                 # Optional npm scripts
└── README.md                    # Documentation
```
