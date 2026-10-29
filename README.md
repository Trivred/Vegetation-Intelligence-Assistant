# Vegetation Intelligence Assistant

## About the Project

A web-based assistant for exploring vegetation data in Saudi Arabia, including rare plants, toxic plants, beneficial plants, and plant distribution across different regions.

## Technologies

* Python
* Django
* Django REST Framework
* Model Context Protocol (MCP)
* Pandas
* HTML, CSS, JavaScript
* Excel

## Features

* Explore rare plants and their rarity levels.
* Search for toxic and beneficial plants.
* View plant distribution by region.
* Submit predefined questions and view structured results.

## Project Structure

```text
VegetationIntelligenceAssistant/
├── config/
├── chatbot/
│   ├── views.py
│   ├── urls.py
│   └── data_service.py
├── templates/
│   └── assistant.html
├── manage.py
└── README.md
```

## Installation

### 1. Create a Virtual Environment

```bash
python -m venv .venv
```

### 2. Activate the Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If Pandas is not included in `requirements.txt`, install it using:

```bash
pip install pandas openpyxl
```

### 4. Apply Migrations

```bash
python manage.py migrate
```

### 5. Run the Server

```bash
python manage.py runserver
```

Open the application at:

http://127.0.0.1:8000/api/

## API Endpoints

| Endpoint                  | Description                 |
| ------------------------- | --------------------------- |
| `/api/`                   | Main interface              |
| `/api/status/`            | Assistant status            |
| `/api/plants/`            | Plant search                |
| `/api/agents/plants/`     | Plant agent                 |
| `/api/agents/vegetation/` | Vegetation agent            |
| `/api/agents/trends/`     | Trends agent                |
| `/api/chat/`              | Submit predefined questions |
| `/api/mcp/tools/`         | MCP tools                   |
| `/api/mcp/resources/`     | MCP resources               |
| `/api/mcp/resource/`      | Read an MCP resource        |
| `/api/mcp/prompt/`        | MCP prompt                  |

## Data Source

Vegetation data stored in Excel files and processed using Pandas.

## Project Information

* **Name:** Vegetation Intelligence Assistant
* **Domain:** Vegetation Data Analysis and Biodiversity
* **Framework:** Django REST Framework
* **Data Processing:** Pandas
* **Interface Language:** Arabic
