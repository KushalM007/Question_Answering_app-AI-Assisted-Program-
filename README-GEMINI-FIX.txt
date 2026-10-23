GEMINI FIX — INSTALLATION

IMPORTANT: Do not copy or upload your real .env file into this bundle. Keep the API key private.

Copy these files into the existing question_answering_app folder, preserving the folder paths:

1. app/main.py                         -> replace existing app/main.py
2. app/config/settings.py              -> replace existing app/config/settings.py
3. app/services/gemini_service.py      -> create this new file
4. requirements.txt                    -> replace existing requirements.txt
5. .env.example                        -> replace existing .env.example (optional but recommended)

Then open question_answering_app/.env locally and set:
GEMINI_API_KEY=YOUR_NEW_GEMINI_API_KEY
GEMINI_MODEL=gemini-2.5-flash
TEMPERATURE=0.2

Use a model identifier currently available to your key in Google AI Studio if gemini-2.5-flash is not available. Never share the real key.

In VS Code terminal, from question_answering_app with your .venv activated, run:
python -m pip install -r requirements.txt
python -m streamlit run app/main.py

Stop an already running server first with Ctrl+C. Do not replace .env with .env.example; edit .env itself.

This bundle does not include or modify app/prompts/qa_prompt.py or app/utils/logging_config.py. Keep those existing files in place.
