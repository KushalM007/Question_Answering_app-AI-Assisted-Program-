# AI Question & Answering System

## Overview

A modular Streamlit chat application that sends questions and conversation context to an OpenAI GPT model using the official OpenAI Python SDK. Conversation history is kept in Streamlit session state for follow-up questions.

## Features

- Chat-style Streamlit interface with separate user and assistant messages.
- Multi-turn conversation history for the lifetime of a Streamlit session.
- Clear Conversation control.
- Configurable model and generation temperature.
- API key loaded from a local `.env` file; no credential is hard-coded.
- Input validation and friendly, sanitized errors.
- Standard-library logging that does not record prompts or credentials.
- Unit tests mock the OpenAI SDK; tests do not need a real API key.

## Architecture

- `app/main.py` contains the Streamlit presentation and session-state handling.
- `app/config/settings.py` loads and validates environment configuration.
- `app/services/openai_service.py` encapsulates calls to the OpenAI Responses API.
- `app/prompts/qa_prompt.py` holds the system instructions separately from the UI.
- `app/utils/logging_config.py` configures application logging.
- `tests/` contains configuration and mocked service tests.

## Project structure

```text
question_answering_app/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── openai_service.py
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── qa_prompt.py
│   └── utils/
│       ├── __init__.py
│       └── logging_config.py
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   └── test_openai_service.py
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── run.sh
```

## Prerequisites

- Python 3.10 or newer.
- An OpenAI API key with access to the selected model.
- Internet access when running the application to call the OpenAI API.

## Setup

Run commands from the `question_answering_app` directory.

### Create and activate a virtual environment

```powershell
python -m venv .venv
```

macOS/Linux:

```sh
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
.\.venv\Scripts\activate.bat
```

### Install dependencies

```sh
python -m pip install -r requirements.txt
```

### Configure `.env`

Copy `.env.example` to `.env`:

macOS/Linux:

```sh
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and replace `your_openai_api_key_here` with your own key. A local `.env` template is included for convenience. The application detects the unchanged placeholder and will not send it to the API. Do not commit or share `.env`. Optional settings are `OPENAI_MODEL` (default: `gpt-6-luna`) and `TEMPERATURE` (default: `0.2`, range: `0` to `2`). Temperature is sent when supported; if the API specifically rejects that parameter for the selected model, the service retries once using the model default.

## Run the application

With the virtual environment activated:

```sh
streamlit run app/main.py
```

The `run.sh` helper can also start Streamlit on macOS/Linux:

```sh
./run.sh
```

Streamlit prints the local URL (usually `http://localhost:8501`) in the terminal and opens it in a browser.

## Run tests

```sh
pytest
```

Tests use mocked OpenAI clients and do not make network requests or require a real API key.

## Example questions

- What is the difference between mitosis and meiosis?
- Explain the causes of the French Revolution in five bullet points.
- Help me understand this algebra step: `2(x + 3) = 14`.
- Follow-up: Can you give an example of the second point?

## Troubleshooting

- **Missing API key:** Copy `.env.example` to `.env` and set `OPENAI_API_KEY`. Restart Streamlit after changing configuration.
- **Authentication or access error:** Check that the key is valid and your OpenAI account has access to the configured model. The app intentionally hides detailed API errors.
- **Model or temperature error:** Set `OPENAI_MODEL` to a model available to your account that supports temperature, or use that model's supported setting.
- **Dependency/import error:** Confirm the virtual environment is active, then run `python -m pip install -r requirements.txt` from this directory.
- **Streamlit command not found:** Activate `.venv` or run `python -m streamlit run app/main.py`.
- **Port already in use:** Start Streamlit with another port, for example `streamlit run app/main.py --server.port 8502`.

## Security considerations

- Store the API key only in the local `.env` file; `.env` is ignored by Git. `.env.example` contains placeholders only.
- Never paste API keys into source code, screenshots, logs, or issue reports.
- The application does not log full questions or answers. OpenAI failures are logged by error type, while the UI receives a generic message.
- Conversation data lives in Streamlit session state and is not written to application files. OpenAI receives submitted questions and the conversation context needed to answer them.
- The default Streamlit server is intended for local development. Before exposing it to a network, add appropriate authentication, HTTPS, rate limiting, monitoring, and deployment secret management.

## Stop the application and deactivate the environment

- Stop Streamlit with `Ctrl+C` in the terminal running the application.
- Deactivate the virtual environment with:

```sh
deactivate
```

## Future enhancements

- Add configurable response-length limits and conversation truncation.
- Add optional conversation export with explicit user consent.
- Add deployment-ready authentication, usage limits, and observability.
- Add integration tests against a controlled staging endpoint.
