AI Interview Prep Coach
A Streamlit app that helps users practice interview questions with Google Gemini. It generates role-appropriate questions, reviews answers, highlights mistakes, suggests a stronger answer, and tracks practice scores during the current session.
Features
- Choose a target role, experience level, interview type, and optional focus areas.
- Generate one interview question at a time.
- Submit an answer and receive a score out of 10.
- Review a breakdown for relevance, examples, structure, and impact.
- See strengths, mistakes/gaps, an example improved answer, and next steps.
- Track scores across reviewed answers in the current session.
- Keep your API key outside source code using Streamlit secrets or an environment variable.
Project files
- app.py — Streamlit application.
- requirements.txt — Python dependencies.
- README.md — setup, GitHub, and deployment guide.
Requirements
- Python 3.10 or newer (Python 3.11 is a good choice).
- A Google Gemini API key from Google AI Studio.
- A GitHub account for the UI-based upload/deployment route.
- A Streamlit Community Cloud account for hosting.
Run locally
1. Download or clone this project and open a terminal in the project folder.
2. Create and activate a virtual environment (recommended).
   Windows
   py -m venv .venv
   .venv\\Scripts\\activate
   macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
3. Install packages:
   pip install -r requirements.txt
4. Set your Gemini API key.
   Windows PowerShell (current terminal only):
   $env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
   macOS/Linux:
   export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
5. Start the app:
   streamlit run app.py
   Streamlit will show a local URL, usually http://localhost:8501.
You can also create .streamlit/secrets.toml locally:
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
Do not upload this secrets file or your real key to GitHub. Add .streamlit/secrets.toml to .gitignore if you create it.
Push to GitHub using the website UI (no Git commands)
1. Sign in to GitHub and click New repository.
2. Give it a name such as ai-interview-prep-coach. Choose Public or Private, then create the repository.
3. On the new repository page, select Add file → Create new file.
4. Enter app.py as the filename, paste the complete contents of your local app.py, then choose Commit changes.
5. Repeat Add file → Create new file for requirements.txt and README.md. Paste the contents of each file and commit each one.
   - If GitHub displays an upload option, you can instead use Add file → Upload files to upload all three files together.
6. Check that app.py, requirements.txt, and README.md appear in the repository root.
7. Never paste your Gemini API key into any of these files or commit a .streamlit/secrets.toml containing the key.
Deploy on Streamlit Community Cloud
1. Push the three files to GitHub using the steps above.
2. Sign in to Streamlit Community Cloud at https://share.streamlit.io/ using the account connection flow.
3. Choose Create app (or New app) and select your GitHub repository, branch (usually main), and main file path app.py.
4. Open the app's Advanced settings / Secrets area before or during deployment, depending on the current interface.
5. Add the secret in TOML format:
   GEMINI_API_KEY = "YOUR_REAL_GEMINI_API_KEY"
6. Deploy the app. Wait for the build to finish, then open the generated app URL.
7. If deployment fails, open Manage app → Logs and check the error. Confirm that requirements.txt is in the repository root, the main file path is app.py, and the secret name is exactly GEMINI_API_KEY.
8. After changing code in GitHub, Streamlit Community Cloud normally rebuilds/restarts the app automatically. Check the app logs if the update does not appear.
Interface labels can change over time; follow the current Streamlit Community Cloud workflow if a button name differs.
Configuration
Optional model override:
- Default model: gemini-2.5-flash
- Environment variable: GEMINI_MODEL
For example, set GEMINI_MODEL to a Gemini model that is currently enabled for your API key if the default model is unavailable. Model names and availability can change, so confirm the current model name in Google AI Studio or the Gemini API documentation.
Testing and troubleshooting
- Syntax check: run python -m py_compile app.py.
- Dependency check: run pip install -r requirements.txt.
- Launch check: run streamlit run app.py.
- End-to-end AI requests require a valid Gemini API key and internet access. Do not expose your key when sharing logs or screenshots.
- If you receive an API/model error, verify that the key is valid, billing/quota limits are appropriate for your account, and GEMINI_MODEL names an available model.
- AI scores are coaching estimates and may vary between attempts. Use feedback as practice guidance, not as a guarantee of interview performance.
How the app handles data
Practice state and score history are kept in Streamlit session state and are not intentionally written to a database by this app. A session can reset when the app restarts or the session is refreshed. The app sends the role, question, and answer text to Google's Gemini API to generate feedback. Do not submit se
