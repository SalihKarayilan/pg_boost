# 🐘 PG_Boost

## Project Title & Description
**PG_Boost** is an AI-powered PostgreSQL performance optimization tool. It analyzes your EXPLAIN query plans, table DDLs, and existing indexes to suggest database engine-level optimizations. Crucially, PG_Boost identifies bottlenecks and provides configuration suggestions (such as `CREATE INDEX`, `ANALYZE`, and `work_mem` adjustments) without modifying your application's business logic or query structure.

## Key Features
* **Multi-Provider AI Support:** Seamlessly connect to your preferred LLM provider, including Gemini, OpenAI, and Claude.
* **Engine-Level Optimizations:** Generates standard SQL index scripts (strictly adhering to standard `CREATE INDEX` syntax), statistics updates, and memory parameter tuning.
* **Modern Streamlit UI:** A clean, tab-based layout separating your SQL, DDL, and EXPLAIN inputs for an intuitive user experience.
* **Secure Authentication:** Built-in session-based login screen to protect the dashboard.
* **Modular Architecture:** A highly maintainable structure separating frontend UI components from backend business logic and configurations.
* **Docker Containerization:** Ready-to-use Docker and Docker Compose setups for continuous background execution.

## Architecture Overview
The project has been refactored from a monolithic script into a modern, scalable architecture:

* `app.py`: The main entry point and router for the Streamlit application.
* `ui/`: Contains the frontend view components.
  * `login.py`: Handles session-based user authentication.
  * `dashboard.py`: Manages the main application layout and user inputs.
* `services/`: Contains the core business logic.
  * `llm_service.py`: Asynchronously manages interactions and routing for Gemini, OpenAI, and Claude APIs.
* `utils/`: Contains helpers, configurations, and constants.
  * `config.py`: Handles environment variable loading and provider settings.
  * `prompts.py`: Stores the system instructions and user message templates for the LLMs.

## Prerequisites
Before you begin, ensure you have the following installed on your machine:
* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/)
* A valid API Key from [Google AI Studio (Gemini)](https://aistudio.google.com/), [OpenAI](https://platform.openai.com/), or [Anthropic (Claude)](https://console.anthropic.com/).

*(If running locally without Docker: Python 3.12+)*

## Environment Setup
PG_Boost uses a `.env` file to securely manage secrets and API keys.

1. Create a file named `.env` in the root directory of the project.
2. Add your desired configuration variables. For example:

```env
# Authentication
APP_USERNAME=admin
APP_PASSWORD=your_secure_password

# Provider API Keys (Add the ones you plan to use)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_claude_api_key_here
```
*Note: The `.env` file is included in `.gitignore` and should never be committed to version control.*

## How to Run

To run PG_Boost continuously in the background without tying up your terminal, use the provided Docker Compose configuration.

1. **Build and Start the Container:**
   Open your terminal in the project root directory and run:
   ```bash
   docker-compose up -d --build
   ```
   *The `-d` flag runs the container in detached mode (in the background).*

2. **Access the Application:**
   Once the container is running, open your web browser and navigate to:
   [http://localhost:8501](http://localhost:8501)

3. **Stop the Application:**
   If you need to stop the application, run:
   ```bash
   docker-compose down
   ```
