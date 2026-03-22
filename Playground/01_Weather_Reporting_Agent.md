# 01 — Weather Reporting Agent

> **Difficulty:** Beginner | **Pattern:** ReAct Agent with Tool Use  
> **LangChain Components Used:** `ChatOllama`, `@tool`, `create_react_agent` (LangGraph), `ChatPromptTemplate`

---

## Table of Contents

1. [Use Case Description](#1-use-case-description)
2. [Objective](#2-objective)
3. [Step-by-Step Thought Process](#3-step-by-step-thought-process)
4. [Pseudo Code](#4-pseudo-code)
5. [Implementation Steps](#5-implementation-steps)
6. [Code Snippets](#6-code-snippets)
7. [Expected Outcomes](#7-expected-outcomes)

---

## 1. Use Case Description

A user wants to ask a conversational AI assistant for the **current weather of any city** by typing a natural language question such as:

- _"What is the weather like in Tokyo today?"_
- _"Tell me the temperature in London right now."_
- _"Is it raining in Sydney?"_

The assistant must:
1. **Understand** the intent from the natural language input
2. **Identify** the city name
3. **Call** a weather tool to fetch real data
4. **Respond** in natural language with the weather information

This is a classic **tool-using agent** use case — the LLM cannot know real-time weather from training data alone, so it must call an external tool to get the answer.

---

## 2. Objective

| Item | Detail |
|---|---|
| **Primary Goal** | Build a ReAct agent that answers weather questions for any city using a live weather API |
| **Agent Type** | Single-agent with one tool |
| **Reasoning Pattern** | ReAct (Thought → Action → Observation → Final Answer) |
| **LLM Used** | `ChatOllama` via `get_chat_llm()` |
| **Tool** | `get_weather(city)` — calls the Open-Meteo API (free, no API key needed) |
| **Input** | Natural language question from the user |
| **Output** | Natural language weather report |

### Why This Is a Good First Agent

- It demonstrates the **core value of agents over plain LLMs**: an LLM alone cannot answer "what is the weather right now" correctly — it needs a tool
- It uses **exactly one tool** — simple enough to trace the full ReAct loop clearly
- The tool call involves **real HTTP data** — not a mock — making the output genuinely dynamic
- It maps directly to the concepts in [01_What_Is_Agentic_AI.md](../Quick-Reference/01_What_Is_Agentic_AI.md) and [02_ReAct_Pattern_Deep_Dive.md](../Quick-Reference/02_ReAct_Pattern_Deep_Dive.md)

---

## 3. Step-by-Step Thought Process

### How a Human Would Solve This

```
1. User asks: "What is the weather in Paris?"
2. I recognise the intent: weather query for city = "Paris"
3. I open a weather website or app and search "Paris"
4. I read the result: "18°C, partly cloudy, wind 12 km/h"
5. I form a natural response: "It is currently 18°C and partly cloudy in Paris."
```

### How the Agent Solves This (ReAct Trace)

```
User: "What is the weather in Paris right now?"

Thought:   The user wants to know the current weather in Paris.
           I should call the get_weather tool with city = "Paris".

Action:    get_weather(city="Paris")

Observation: {
               "city": "Paris",
               "temperature_c": 18.2,
               "windspeed_kmh": 12.4,
               "weathercode": 2,
               "description": "Partly cloudy"
             }

Thought:   I now have the current weather data for Paris.
           I can form a complete answer.

Final Answer: The current weather in Paris is 18.2°C with partly cloudy skies
              and a wind speed of 12.4 km/h.
```

### Decision Points in the Loop

```
┌────────────────────────────────────┐
│ User sends weather question        │
└──────────────┬─────────────────────┘
               │
               ▼
┌────────────────────────────────────┐
│ Agent (LLM): parse city from input │
│ Decide: call get_weather tool      │
└──────────────┬─────────────────────┘
               │
               ▼
┌────────────────────────────────────┐
│ Tool: HTTP GET Open-Meteo API      │
│ Geocode city → lat/lon             │
│ Fetch current weather data         │
└──────────────┬─────────────────────┘
               │
               ▼
┌────────────────────────────────────┐
│ Observation returned to agent      │
│ Agent: no more tool calls needed   │
│ Generate Final Answer              │
└──────────────┬─────────────────────┘
               │
               ▼
        Natural language response
```

---

## 4. Pseudo Code

```
FUNCTION weather_agent(user_question):

    # Tool definition
    TOOL get_weather(city: string) -> dict:
        coords = geocode(city)               # city name → latitude, longitude
        weather = fetch_weather(coords)      # call Open-Meteo API
        RETURN weather data as dict

    # Agent setup
    llm = ChatOllama(model=OLLAMA_MODEL)
    agent = ReActAgent(llm=llm, tools=[get_weather])

    # Agent loop (handled internally by LangGraph)
    LOOP:
        thought = llm.think(user_question, previous_observations)
        IF thought requires tool call:
            observation = get_weather(extracted_city)
            append observation to context
        ELSE:
            final_answer = llm.respond(user_question, all_observations)
            RETURN final_answer
        END IF
    END LOOP

END FUNCTION
```

---

## 5. Implementation Steps

### Prerequisites

```
1. Virtual environment activated (.venv)
2. Base dependencies installed: pip install -r requirements-base.txt
3. Project dependencies installed (see Step 1 below)
4. .env file configured with OLLAMA_BASE_URL and OLLAMA_MODEL
5. Ollama server running with your chosen model available
```

### Step 1 — Install Additional Dependencies

The Open-Meteo API is accessed via HTTP. Add `requests` to your project's requirements:

```bash
pip install requests
```

No API key or account is needed — Open-Meteo is a free, open-source weather API.

### Step 2 — Create the Project File

Create `Playground/01_weather_agent.py` (the runnable implementation — see Section 6).

### Step 3 — Understand the Two API Calls

The weather tool makes two sequential HTTP calls:

```
1. Geocoding API
   URL:  https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1
   Returns: latitude, longitude, timezone for the city name

2. Weather API
   URL:  https://api.open-meteo.com/v1/forecast
         ?latitude={lat}&longitude={lon}
         &current=temperature_2m,windspeed_10m,weathercode
         &timezone=auto
   Returns: current temperature, windspeed, and a WMO weather code
```

### Step 4 — Map WMO Weather Codes to Descriptions

The weather API returns a numeric **WMO weather code** (e.g., `0` = Clear sky, `61` = Rain).
The tool maps these to human-readable descriptions before returning to the agent.

### Step 5 — Run and Test

```bash
cd Langchain_Development_Projects
python Playground/01_weather_agent.py
```

Test with several cities to observe the full ReAct trace.

---

## 6. Code Snippets

### Full Implementation — `Playground/01_weather_agent.py`

```python
"""
01_weather_agent.py
Practice use case: ReAct agent that reports current weather for any city.
Uses Open-Meteo API (free, no API key required).
"""

import sys
import os
import requests
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

# Allow imports from the repo root (common/)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common.llm_factory import get_chat_llm

# ── WMO Weather Code → Human-readable description ─────────────────────────────
WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Icy fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}


# ── Tool Definition ────────────────────────────────────────────────────────────
@tool
def get_weather(city: str) -> str:
    """
    Get the current weather for a given city name.
    Returns temperature in Celsius, wind speed in km/h, and weather description.
    """
    # Step 1: Geocode the city name to lat/lon
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_response = requests.get(geo_url, params={"name": city, "count": 1}, timeout=10)
    geo_response.raise_for_status()
    geo_data = geo_response.json()

    if not geo_data.get("results"):
        return f"City '{city}' not found. Please check the spelling."

    result = geo_data["results"][0]
    lat = result["latitude"]
    lon = result["longitude"]
    resolved_name = result["name"]
    country = result.get("country", "")

    # Step 2: Fetch current weather
    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_response = requests.get(
        weather_url,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,windspeed_10m,weathercode",
            "timezone": "auto",
        },
        timeout=10,
    )
    weather_response.raise_for_status()
    weather_data = weather_response.json()

    current = weather_data["current"]
    temperature = current["temperature_2m"]
    windspeed = current["windspeed_10m"]
    code = current["weathercode"]
    description = WMO_CODES.get(code, f"Weather code {code}")

    return (
        f"Current weather in {resolved_name}, {country}: "
        f"{temperature}°C, {description}, wind speed {windspeed} km/h."
    )


# ── Agent Setup ────────────────────────────────────────────────────────────────
def build_agent():
    llm = get_chat_llm()
    return create_react_agent(model=llm, tools=[get_weather])


# ── Run ────────────────────────────────────────────────────────────────────────
def ask(agent, question: str) -> str:
    result = agent.invoke({"messages": [HumanMessage(content=question)]})
    return result["messages"][-1].content


if __name__ == "__main__":
    agent = build_agent()

    questions = [
        "What is the weather like in Tokyo right now?",
        "Tell me the current temperature in London.",
        "Is it raining in Sydney today?",
    ]

    for question in questions:
        print(f"\nQ: {question}")
        print(f"A: {ask(agent, question)}")
        print("-" * 60)
```

### Snippet — Tool Only (for unit testing)

```python
# Test the tool in isolation without running the full agent
from Playground.weather_agent import get_weather

result = get_weather.invoke({"city": "Berlin"})
print(result)
# → "Current weather in Berlin, Germany: 12.4°C, Partly cloudy, wind speed 18.2 km/h."
```

### Snippet — Single Interactive Question

```python
agent = build_agent()
city = input("Enter a city: ")
answer = ask(agent, f"What is the weather in {city}?")
print(answer)
```

---

## 7. Expected Outcomes

### What You Should See

Running `python Playground/01_weather_agent.py` will print three Q&A pairs:

```
Q: What is the weather like in Tokyo right now?
A: The current weather in Tokyo, Japan is 22.1°C with partly cloudy skies
   and a wind speed of 8.5 km/h.
------------------------------------------------------------

Q: Tell me the current temperature in London.
A: The current temperature in London, United Kingdom is 14.3°C.
   The sky is overcast with a wind speed of 21.0 km/h.
------------------------------------------------------------

Q: Is it raining in Sydney today?
A: Currently in Sydney, Australia it is not raining. The temperature is 26.8°C
   with mainly clear skies and a wind speed of 15.2 km/h.
------------------------------------------------------------
```

> Exact values will vary — they are live weather readings at the time of execution.

### ReAct Trace (What Happens Internally)

For the question _"What is the weather like in Tokyo right now?"_:

```
[HumanMessage]  "What is the weather like in Tokyo right now?"

[AIMessage]     tool_calls=[{name: "get_weather", args: {"city": "Tokyo"}}]

[ToolMessage]   "Current weather in Tokyo, Japan: 22.1°C, Partly cloudy,
                 wind speed 8.5 km/h."

[AIMessage]     "The current weather in Tokyo, Japan is 22.1°C with partly
                 cloudy skies and a wind speed of 8.5 km/h."
```

### Verification Checklist

| Check | Expected Result |
|---|---|
| Agent calls `get_weather` tool | ✅ `ToolMessage` appears in message history |
| Tool returns real weather data | ✅ Values change between runs and match actual conditions |
| LLM responds in natural language | ✅ Final message is a coherent sentence, not raw JSON |
| Unknown city handled gracefully | ✅ Tool returns "City not found" message; agent relays this to user |
| Network error handled | ✅ `requests` raises `HTTPError`; agent surfaces the error in its response |

### What to Experiment With Next

| Experiment | How |
|---|---|
| Add a second tool | Create `get_forecast(city, days)` for multi-day forecasts |
| Add memory | Pass a `MemorySaver` checkpointer so the agent remembers conversation history |
| Multi-city query | Ask "Compare the weather in Paris and Berlin" — watch the agent call the tool twice |
| Streaming output | Use `agent.stream(...)` instead of `agent.invoke(...)` to print tokens as they arrive |
| Error handling | Pass an invalid city name ("Xyzabc123") and observe how the agent handles the "not found" response |

---

*Back to Playground index → [`Playground/`](../Playground/)*  
*Related Quick-Reference → [02_ReAct_Pattern_Deep_Dive.md](../Quick-Reference/02_ReAct_Pattern_Deep_Dive.md)*
