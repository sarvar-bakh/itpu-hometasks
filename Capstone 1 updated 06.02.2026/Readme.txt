# Data Insights Agent - Capstone Project 01 (Sarvar Baxtiyorov)

## 📋 Project Overview
A Streamlit-based AI agent that helps users analyze business data through natural language queries. The agent uses function calling with DeepSeek API to safely query a SQLite database and provide insights.

## 🚀 Features

### Core Features
- **Natural Language Queries**: Ask questions about your data in plain English
- **Safe Database Operations**: Built-in safety to prevent dangerous operations
- **Function Calling**: Uses 4 different tools for data interaction
- **Support Ticket System**: Create tickets for human assistance
- **Real-time Visualizations**: Interactive charts and graphs
- **Database Statistics**: Sidebar with key metrics and insights

### Safety Features
- Blocks dangerous SQL operations (DELETE, DROP, TRUNCATE, etc.)
- Read-only query execution by default
- Agent suggests support tickets for complex queries

📸 Usage Workflow (Screenshots)

Screenshot 01
The application starts with a clean and intuitive interface displaying key database statistics along with sample queries to guide the user.

Screenshot 02
A live data visualization showing sales distribution by region, allowing users to quickly understand regional performance.

Screenshot 03
The agent retrieves and presents aggregated database statistics based on the user’s request, without exposing raw data to the language model.

Screenshot 04
Creation of a support ticket, enabling the user to escalate the issue to a human operator through the integrated support system.

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- DeepSeek API key

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/data-insights-app.git
cd data-insights-app

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py