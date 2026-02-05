import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
from datetime import datetime
import sqlite3
import threading
import random
from datetime import timedelta

# ============================================
# CONFIGURATION
# ============================================
DEEPSEEK_API_KEY = "sk-735cd736d5a241d68d81d2a09afb247b"
USE_API = True  # Set to False for demo mode without API

# ============================================
# DATABASE SETUP (Thread-Safe)
# ============================================
thread_local = threading.local()


def get_db_connection():
    """Get thread-local SQLite connection"""
    if not hasattr(thread_local, "conn"):
        thread_local.conn = sqlite3.connect(
            "business_data.db",
            check_same_thread=False,
            timeout=10
        )
    return thread_local.conn


def init_database():
    """Initialize database with sample data"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS sales
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       date
                       TEXT,
                       product
                       TEXT,
                       category
                       TEXT,
                       region
                       TEXT,
                       quantity
                       INTEGER,
                       revenue
                       REAL,
                       profit
                       REAL,
                       customer_id
                       TEXT
                   )
                   ''')

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS customers
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       customer_id
                       TEXT,
                       name
                       TEXT,
                       email
                       TEXT,
                       region
                       TEXT,
                       join_date
                       TEXT,
                       loyalty_score
                       INTEGER
                   )
                   ''')

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS support_tickets
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       ticket_id
                       TEXT
                       UNIQUE,
                       title
                       TEXT,
                       description
                       TEXT,
                       status
                       TEXT
                       DEFAULT
                       'Open',
                       priority
                       TEXT
                       DEFAULT
                       'Medium',
                       created_date
                       TEXT
                   )
                   ''')

    # Generate sample data if needed
    cursor.execute("SELECT COUNT(*) FROM sales")
    count = cursor.fetchone()[0]

    if count < 500:
        generate_sample_data(cursor, 600)

    conn.commit()
    return conn


def generate_sample_data(cursor, num_records):
    """Generate sample sales data"""
    products = ["Laptop", "Smartphone", "Tablet", "Monitor", "Keyboard",
                "Mouse", "Headphones", "Printer", "Router", "Camera"]
    categories = ["Electronics", "Computers", "Accessories", "Networking", "Photography"]
    regions = ["North", "South", "East", "West", "Central"]

    print(f"Generating {num_records} sample records...")

    # Generate sales data
    for i in range(num_records):
        date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
        product = random.choice(products)
        category = random.choice(categories)
        region = random.choice(regions)
        quantity = random.randint(1, 10)
        revenue = round(random.uniform(100, 5000), 2)
        profit = round(revenue * random.uniform(0.1, 0.4), 2)
        customer_id = f"CUST{random.randint(1000, 9999)}"

        cursor.execute('''
                       INSERT INTO sales (date, product, category, region, quantity, revenue, profit, customer_id)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                       ''', (date, product, category, region, quantity, revenue, profit, customer_id))

    print(f"Generated {num_records} sales records")

    # Generate some sample tickets
    sample_tickets = [
        ("Data export issue", "Cannot export sales report for Q3", "High"),
        ("Dashboard loading slow", "Dashboard takes 30+ seconds to load", "Medium"),
        ("User permissions", "Need access to customer database", "Low")
    ]

    for title, description, priority in sample_tickets:
        ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100, 999)}"
        created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
                       INSERT
                       OR IGNORE INTO support_tickets (ticket_id, title, description, priority, created_date)
            VALUES (?, ?, ?, ?, ?)
                       ''', (ticket_id, title, description, priority, created_date))


# Initialize database
conn = init_database()

# ============================================
# STREAMLIT APP CONFIG
# ============================================
st.set_page_config(
    page_title="Data Insights Agent 🤖",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1.5rem;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 5px solid #4F46E5;
    }
    .stButton button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 8px;
        font-weight: 600;
        margin: 0.25rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-message {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        border-left: 5px solid #2196F3;
        margin-left: 10%;
    }
    .agent-message {
        background: linear-gradient(135deg, #F3E5F5 0%, #E1BEE7 100%);
        border-left: 5px solid #9C27B0;
        margin-right: 10%;
    }
    .demo-badge {
        background: #FF9800;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# DATABASE FUNCTIONS
# ============================================
def get_database_stats():
    """Get database statistics"""
    cursor = conn.cursor()
    stats = {}

    # Table counts
    cursor.execute("SELECT COUNT(*) FROM sales")
    stats["sales_count"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM customers")
    stats["customers_count"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM support_tickets")
    stats["tickets_count"] = cursor.fetchone()[0]

    # Sales stats
    cursor.execute("SELECT SUM(revenue), SUM(profit), AVG(revenue) FROM sales")
    total_rev, total_profit, avg_rev = cursor.fetchone()
    stats["total_revenue"] = round(total_rev or 0, 2)
    stats["total_profit"] = round(total_profit or 0, 2)
    stats["avg_sale"] = round(avg_rev or 0, 2)

    # Unique customers
    cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM sales")
    stats["unique_customers"] = cursor.fetchone()[0]

    # Top products
    cursor.execute("""
                   SELECT product, SUM(quantity) as total_qty
                   FROM sales
                   GROUP BY product
                   ORDER BY total_qty DESC LIMIT 5
                   """)
    stats["top_products"] = cursor.fetchall()

    # Recent tickets
    cursor.execute("""
                   SELECT ticket_id, title, priority
                   FROM support_tickets
                   ORDER BY created_date DESC LIMIT 3
                   """)
    stats["recent_tickets"] = cursor.fetchall()

    return stats


def execute_safe_query(query):
    """Execute a safe SQL query"""
    query_lower = query.strip().lower()

    # Block dangerous operations
    dangerous = ['drop', 'delete', 'truncate', 'alter', 'update', 'insert']
    if any(op in query_lower for op in dangerous):
        return {"success": False, "error": "This operation is blocked for safety."}

    if not query_lower.startswith('select'):
        return {"success": False, "error": "Only SELECT queries are allowed."}

    try:
        df = pd.read_sql_query(query, conn)
        return {
            "success": True,
            "data": df.to_dict('records'),
            "columns": df.columns.tolist(),
            "row_count": len(df)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_support_ticket(title, description, priority="Medium"):
    """Create a support ticket"""
    cursor = conn.cursor()
    ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
                   INSERT INTO support_tickets (ticket_id, title, description, priority, created_date)
                   VALUES (?, ?, ?, ?, ?)
                   ''', (ticket_id, title, description, priority, created_date))

    conn.commit()

    return {
        "success": True,
        "ticket_id": ticket_id,
        "message": f"✅ Support ticket '{ticket_id}' created with {priority} priority."
    }


# ============================================
# AI AGENT FUNCTIONS (With Demo Fallback)
# ============================================
def get_agent_tools():
    """Define agent tools for function calling"""
    return [
        {
            "type": "function",
            "function": {
                "name": "query_database",
                "description": "Execute safe SELECT queries to get data from database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "SQL SELECT query"}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_database_stats",
                "description": "Get database statistics and insights",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_support_ticket",
                "description": "Create a support ticket for human assistance",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "priority": {
                            "type": "string",
                            "enum": ["Low", "Medium", "High", "Critical"]
                        }
                    },
                    "required": ["title", "description"]
                }
            }
        }
    ]


def get_ai_response_with_tools(user_query, use_api=True):
    """
    Get AI response using DeepSeek API or demo simulation
    """
    if not use_api:
        # DEMO MODE: Simulate AI responses
        return get_demo_response(user_query)

    # REAL API MODE
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        messages = [
            {"role": "system", "content": """You are a Data Insights Assistant. Help users analyze business data.
            Use tools to query database. Only use SELECT queries.
            Be concise and helpful. If unsure, suggest creating a support ticket."""},
            {"role": "user", "content": user_query}
        ]

        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "tools": get_agent_tools(),
            "max_tokens": 1000,
            "temperature": 0.1
        }

        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]

        # If API fails, fallback to demo mode
        print(f"API Error: {response.status_code}")
        return get_demo_response(user_query)

    except Exception as e:
        print(f"API Exception: {e}")
        return get_demo_response(user_query)


def get_demo_response(user_query):
    """Generate demo responses without API"""
    user_query_lower = user_query.lower()

    if "sales" in user_query_lower and "region" in user_query_lower:
        result = execute_safe_query("SELECT region, SUM(revenue) as total FROM sales GROUP BY region")
        if result["success"]:
            df = pd.DataFrame(result["data"])
            response = f"**Sales by Region:**\n\n"
            for _, row in df.iterrows():
                response += f"- {row['region']}: ${row['total']:,.2f}\n"
            response += f"\nTotal: ${df['total'].sum():,.2f}"
            return {"content": response}

    elif "top" in user_query_lower and "product" in user_query_lower:
        result = execute_safe_query(
            "SELECT product, SUM(quantity) as total FROM sales GROUP BY product ORDER BY total DESC LIMIT 5")
        if result["success"]:
            df = pd.DataFrame(result["data"])
            response = "**Top 5 Products by Sales Volume:**\n\n"
            for idx, row in df.iterrows():
                response += f"{idx + 1}. {row['product']}: {row['total']} units sold\n"
            return {"content": response}

    elif "stat" in user_query_lower or "insight" in user_query_lower:
        stats = get_database_stats()
        response = "**Database Insights:**\n\n"
        response += f"📊 Total Sales Records: {stats['sales_count']:,}\n"
        response += f"💰 Total Revenue: ${stats['total_revenue']:,.2f}\n"
        response += f"📈 Average Sale: ${stats['avg_sale']:,.2f}\n"
        response += f"👥 Unique Customers: {stats['unique_customers']}\n"
        response += f"🎫 Open Support Tickets: {stats['tickets_count']}"
        return {"content": response}

    elif "support" in user_query_lower or "ticket" in user_query_lower:
        return {
            "content": "To create a support ticket, click the 'Create Support Ticket' button in the sidebar or tell me what you need help with."}

    elif "hello" in user_query_lower or "hi" in user_query_lower:
        return {
            "content": "Hello! I'm your Data Insights Agent. I can help you analyze sales data, show trends, create support tickets, and more. Try asking about 'sales by region' or 'top products'."}

    else:
        return {
            "content": f"I can help you analyze your business data. You asked: '{user_query}'\n\nTry asking:\n- 'Show sales by region'\n- 'What are top products?'\n- 'Get database statistics'\n- 'Create a support ticket'\n\nOr use the sample queries in the sidebar."}


def execute_tool_call(tool_name, arguments):
    """Execute a tool call"""
    if tool_name == "query_database":
        query = arguments.get("query", "")
        return execute_safe_query(query)
    elif tool_name == "get_database_stats":
        return {"success": True, "stats": get_database_stats()}
    elif tool_name == "create_support_ticket":
        title = arguments.get("title", "")
        description = arguments.get("description", "")
        priority = arguments.get("priority", "Medium")
        return create_support_ticket(title, description, priority)
    else:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}


# ============================================
# STREAMLIT UI COMPONENTS
# ============================================
def display_sidebar():
    """Display sidebar with business information"""
    with st.sidebar:
        st.markdown("## 📊 Business Dashboard")

        # Demo mode badge
        if not USE_API:
            st.markdown('<div class="demo-badge">DEMO MODE</div>', unsafe_allow_html=True)
            st.info("Using simulated AI responses")

        try:
            stats = get_database_stats()

            # Key metrics in cards
            col1, col2 = st.columns(2)
            with col1:
                st.metric("💰 Revenue", f"${stats['total_revenue']:,.0f}")
                st.metric("📦 Products", len(stats['top_products']))
            with col2:
                st.metric("👥 Customers", stats['unique_customers'])
                st.metric("🎫 Tickets", stats['tickets_count'])

            st.divider()

            # Top Products
            st.markdown("### 🏆 Top Products")
            for product, qty in stats.get('top_products', []):
                st.progress(min(qty / 100, 1.0), text=f"{product}: {qty} units")

            st.divider()

            # Sample Queries
            st.markdown("### 💡 Sample Queries")
            queries = [
                "Show sales by region",
                "What are top 5 products?",
                "Show monthly revenue trend",
                "Get database statistics"
            ]

            for query in queries:
                if st.button(f"🔍 {query}", key=f"query_{query}"):
                    st.session_state.messages.append({"role": "user", "content": query})
                    st.rerun()

            st.divider()

            # Quick Actions
            st.markdown("### ⚡ Quick Actions")
            if st.button("📋 Create Support Ticket", type="primary"):
                st.session_state.show_ticket_form = True
                st.rerun()

            if st.button("🔄 Refresh Dashboard"):
                st.rerun()

            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = []
                st.rerun()

            st.divider()

            # Recent Tickets
            if stats.get('recent_tickets'):
                st.markdown("### 📝 Recent Tickets")
                for ticket_id, title, priority in stats['recent_tickets'][:3]:
                    st.caption(f"**{ticket_id}** - {priority}")
                    st.text(f"{title[:30]}...")

        except Exception as e:
            st.error(f"Error loading sidebar: {str(e)}")


def display_visualizations():
    """Display data visualizations"""
    try:
        # Revenue by region
        result = execute_safe_query(
            "SELECT region, SUM(revenue) as total_revenue FROM sales GROUP BY region"
        )

        if result["success"] and result["data"]:
            df = pd.DataFrame(result["data"])
            if not df.empty:
                fig1 = px.pie(df, values='total_revenue', names='region',
                              title='Revenue Distribution by Region',
                              color_discrete_sequence=px.colors.sequential.Blues)
                st.plotly_chart(fig1, use_container_width=True)

        # Monthly trend
        result2 = execute_safe_query("""
                                     SELECT strftime('%Y-%m', date) as month, 
                   SUM(revenue) as monthly_revenue
                                     FROM sales
                                     GROUP BY month
                                     ORDER BY month
                                         LIMIT 6
                                     """)

        if result2["success"] and result2["data"]:
            df2 = pd.DataFrame(result2["data"])
            if not df2.empty:
                fig2 = px.line(df2, x='month', y='monthly_revenue',
                               title='Monthly Revenue Trend (Last 6 Months)',
                               markers=True)
                fig2.update_traces(line=dict(width=3))
                st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.info("📊 Charts will update as you query data")


def display_support_ticket_form():
    """Display support ticket creation form"""
    with st.form("support_ticket_form", clear_on_submit=True):
        st.subheader("🎫 Create Support Ticket")

        title = st.text_input("Title*", placeholder="Brief description of your issue")
        description = st.text_area("Description*", height=100,
                                   placeholder="Detailed description of what you need help with")
        priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"], index=1)

        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("✅ Create Ticket", type="primary")
        with col2:
            cancel = st.form_submit_button("❌ Cancel")

        if submit and title and description:
            result = create_support_ticket(title, description, priority)
            if result["success"]:
                st.success(result["message"])
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["message"]
                })
                st.session_state.show_ticket_form = False
                st.rerun()

        if cancel:
            st.session_state.show_ticket_form = False
            st.rerun()


# ============================================
# MAIN APPLICATION
# ============================================
def main():
    """Main application"""
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "show_ticket_form" not in st.session_state:
        st.session_state.show_ticket_form = False

    # Header
    st.markdown('<h1 class="main-header">🤖 Data Insights Agent</h1>', unsafe_allow_html=True)

    if not USE_API:
        st.info(
            "🔶 Running in **Demo Mode** with simulated AI responses. Set `USE_API = True` and configure your API key for real AI interactions.")

    # Main layout
    col1, col2 = st.columns([2, 1])

    with col1:
        # Chat interface container
        chat_container = st.container(height=500, border=True)

        with chat_container:
            # Display chat history
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>👤 You:</strong><br>
                        {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message agent-message">
                        <strong>🤖 Agent:</strong><br>
                        {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)

        # Support ticket form (if active)
        if st.session_state.show_ticket_form:
            display_support_ticket_form()

        # User input
        user_input = st.chat_input("Ask about your data...")

        if user_input:
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Get AI response
            response = get_ai_response_with_tools(user_input, use_api=USE_API)

            # Handle tool calls (for real API mode)
            if USE_API and "tool_calls" in response:
                tool_calls = response["tool_calls"]
                for tool_call in tool_calls:
                    tool_name = tool_call["function"]["name"]
                    arguments = json.loads(tool_call["function"]["arguments"])

                    print(f"LOG | Executing tool: {tool_name}")
                    print(f"LOG | Arguments: {arguments}")

                    # Execute tool
                    tool_result = execute_tool_call(tool_name, arguments)

                    # In a full implementation, you would send tool results back to API
                    # For simplicity, we'll just use the tool result directly
                    if tool_name == "query_database" and tool_result["success"]:
                        df = pd.DataFrame(tool_result["data"])
                        response = {"content": f"Query results:\n\n{df.to_string()}"}

            # Add assistant response to chat
            assistant_message = response.get("content", "I apologize, but I couldn't generate a response.")
            st.session_state.messages.append({"role": "assistant", "content": assistant_message})

            st.rerun()

    with col2:
        # Visualizations
        st.markdown("### 📈 Live Visualizations")
        display_visualizations()

        # Quick data preview
        st.markdown("### 📋 Quick Data Preview")
        if st.button("Show Sample Data"):
            result = execute_safe_query("SELECT product, region, revenue FROM sales LIMIT 10")
            if result["success"]:
                df = pd.DataFrame(result["data"])
                st.dataframe(df, use_container_width=True)

    # Display sidebar
    display_sidebar()

    # Footer
    st.divider()
    st.caption("🤖 Data Insights Agent | 🛡️ Safe SQL Operations | 🎫 Support System | 📊 Real-time Analytics")

    # Log session info
    print(f"LOG | Session active | Messages: {len(st.session_state.messages)} | API Mode: {USE_API}")

# ============================================
# RUN APPLICATION
# ============================================
if __name__ == "__main__":
    main()