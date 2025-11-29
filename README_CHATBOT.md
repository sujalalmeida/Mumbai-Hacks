# Fitness Tracker AI Agent

This document provides instructions for setting up and testing the AI-powered fitness chatbot in the Fit Tracker app.

## Overview

The AI agent analyzes the last 7 days of fitness data and provides personalized suggestions or a summary of the user's performance. It can:

- Automatically provide suggestions without specific user input
- Respond to user questions about their fitness data
- Use Ollama with a Mistral model through LangChain

## Installation

1. Install the required packages:

```bash
pip install -r requirements.txt
```

2. Make sure Ollama is installed on your system. If not, follow the installation instructions at [https://ollama.ai/](https://ollama.ai/).

3. Pull the Mistral model:

```bash
ollama pull mistral
```

## Running the Chatbot

1. Start the Ollama server:

```bash
ollama serve
```

2. Start the Django development server:

```bash
python manage.py runserver
```

3. Visit the dashboard at http://127.0.0.1:8000/fit/

## Usage

The chatbot appears at the bottom of the dashboard page and provides:

1. An automatic suggestion based on your last 7 days of fitness data
2. The ability to ask specific questions via the text input field

Example questions you can ask:
- "Am I making progress with my steps?"
- "How many calories did I burn yesterday?"
- "What can I do to improve my activity level?"
- "Have I been meeting my step goals?"

## Implementation Details

The AI agent implementation consists of:

- `fit_tracker/utils/ai_agent.py`: Core AI logic using LangChain and Ollama
- `fit_tracker/views.py`: Django view for handling chatbot requests
- `fit_tracker/urls.py`: URL configuration for the chatbot endpoint
- `fit_tracker/templates/fit_tracker/dashboard.html`: UI for the chatbot
- `fit_tracker/static/fit_tracker/css/style.css`: Styling for the chatbot
- `fit_tracker/static/fit_tracker/js/charts.js`: JavaScript for chatbot interactions

## Troubleshooting

- If you receive a "Connection refused" error, make sure the Ollama server is running with `ollama serve`.
- If the chatbot doesn't respond, check your browser console for errors.
- For slow responses, consider using a lighter model with Ollama or adjusting server resources.

## Dependencies

- Python 3.6+
- Django 5.0+
- LangChain 0.1.0+
- LangChain-Community 0.0.13+
- LangChain-Ollama 0.0.1+
- Ollama with Mistral model 