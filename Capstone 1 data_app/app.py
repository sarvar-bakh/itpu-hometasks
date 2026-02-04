# app.py - Data Insights Chat Application
import streamlit as st
import pandas as pd
import sqlite3
import json
import numpy as np
from datetime import datetime

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Data Insights Chat",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# SIDEBAR - BUSINESS INFORMATION
# ============================================
with st.sidebar:
    st.title("📈 Business Dashboard")

    # Database stats (will be populated after database creation)
    if "db_stats" in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Records", st.session_state.db_stats["total_records"])
        with col2:
            st.metric("Total Sales", f"${st.session_state.db_stats['total_sales']:,.2f}")

    st.divider()

    st.subheader("📋 Sample Queries")
    sample_queries = [
        "What are total sales?",
        "Show me the best selling product",
        "What's the average order value?",
        "How many sales per region?",
        "Show sales trend by month"
    ]
    for query in sample_queries:
        st.code(query, language="text")

    st.divider()

    st.subheader("🛠️ Support System")
    # Support ticket creation
    ticket_description = st.text_area("Describe your issue:", height=100,
                                      placeholder="Enter details for the support ticket...")

    if st.button("📝 Create Support Ticket", type="primary", use_container_width=True):
        if ticket_description.strip():
            ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            ticket_data = {
                "id": ticket_id,
                "time": datetime.now().isoformat(),
                "description": ticket_description,
                "status": "open",
                "priority": "medium"
            }

            # Save to JSON file (simulates ticket system)
            try:
                with open("support_tickets.json", "a") as f:
                    f.write(json.dumps(ticket_data) + "\n")

                st.success(f"Ticket **{ticket_id}** created successfully!")
                st.info("A support agent will contact you within 24 hours.")
                print(f"[TICKET LOG] New ticket created: {ticket_id}")

                # Clear the text area
                st.rerun()
            except Exception as e:
                st.error(f"Error creating ticket: {str(e)}")
        else:
            st.warning("Please enter a description for the ticket.")


# ============================================
# DATABASE FUNCTIONS
# ============================================
@st.cache_resource
def create_database():
    """Create and populate the sales database with 550+ rows"""
    print("[DATABASE LOG] Creating sales database...")

    # FIX: Add check_same_thread=False to handle Streamlit threading
    conn = sqlite3.connect('sales_data.db', check_same_thread=False)

    # Generate 550+ rows of realistic sales data
    np.random.seed(42)
    n_rows = 550

    # Create date range for the past 18 months
    dates = pd.date_range(start='2023-07-01', end='2024-12-31', periods=n_rows)

    # Product distribution with realistic pricing
    products = ['Laptop', 'Smartphone', 'Tablet', 'Monitor', 'Keyboard',
                'Mouse', 'Headphones', 'Printer', 'Scanner', 'Router']
    product_prices = {
        'Laptop': (800, 2500),
        'Smartphone': (400, 1200),
        'Tablet': (200, 800),
        'Monitor': (150, 600),
        'Keyboard': (20, 150),
        'Mouse': (10, 80),
        'Headphones': (50, 300),
        'Printer': (100, 500),
        'Scanner': (150, 700),
        'Router': (60, 250)
    }

    regions = ['North America', 'Europe', 'Asia Pacific', 'South America', 'Middle East']

    # Generate data
    data = []
    for i in range(n_rows):
        product = np.random.choice(products)
        price_range = product_prices[product]
        quantity = np.random.randint(1, 5)
        unit_price = np.random.uniform(price_range[0], price_range[1])
        amount = round(unit_price * quantity, 2)

        data.append({
            'sale_id': i + 1000,
            'date': dates[i].strftime('%Y-%m-%d'),
            'customer_id': np.random.randint(100, 999),
            'product': product,
            'quantity': quantity,
            'unit_price': round(unit_price, 2),
            'amount': amount,
            'region': np.random.choice(regions),
            'sales_person': np.random.choice(['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'])
        })

    # Create DataFrame and save to database
    df = pd.DataFrame(data)
    df.to_sql('sales', conn, if_exists='replace', index=False)

    # Calculate statistics for display
    total_sales = df['amount'].sum()

    # Store stats in session state for sidebar display
    st.session_state.db_stats = {
        "total_records": n_rows,
        "total_sales": total_sales,
        "date_range": f"{dates.min().strftime('%b %Y')} - {dates.max().strftime('%b %Y')}"
    }

    print(f"[DATABASE LOG] Created {n_rows} sales records")
    print(f"[DATABASE LOG] Total sales value: ${total_sales:,.2f}")

    return conn


# ============================================
# QUERY FUNCTIONS (SAFE TOOLS)
# ============================================
def execute_safe_query(query, params=None):
    """Tool 1: Execute a safe SQL query (SELECT only)"""
    if any(keyword in query.upper() for keyword in ['DELETE', 'DROP', 'INSERT', 'UPDATE', 'ALTER']):
        error_msg = "❌ Safety Violation: Only SELECT queries are allowed!"
        print(f"[SAFETY LOG] Blocked dangerous query: {query[:100]}...")
        return None, error_msg

    try:
        conn = sqlite3.connect('sales_data.db', check_same_thread=False)
        if params:
            df = pd.read_sql_query(query, conn, params=params)
        else:
            df = pd.read_sql_query(query, conn)
        conn.close()
        print(f"[QUERY LOG] Executed safe query: {query[:100]}...")
        return df, None
    except Exception as e:
        error_msg = f"Query error: {str(e)}"
        print(f"[QUERY LOG] Error: {error_msg}")
        return None, error_msg


def get_data_summary():
    """Tool 2: Get aggregated business insights"""
    print("[TOOL LOG] Generating data summary...")

    summary = {}

    # Total sales
    df, error = execute_safe_query("SELECT SUM(amount) as total_sales FROM sales")
    if df is not None:
        summary['total_sales'] = float(df['total_sales'].iloc[0])

    # Sales by product
    df, error = execute_safe_query("""
                                   SELECT product, COUNT(*) as count, SUM(amount) as revenue
                                   FROM sales
                                   GROUP BY product
                                   ORDER BY revenue DESC
                                   """)
    if df is not None:
        summary['top_product'] = df.iloc[0]['product']
        summary['top_product_revenue'] = float(df.iloc[0]['revenue'])

    # Sales by region
    df, error = execute_safe_query("""
                                   SELECT region, SUM(amount) as revenue
                                   FROM sales
                                   GROUP BY region
                                   ORDER BY revenue DESC
                                   """)
    if df is not None:
        summary['top_region'] = df.iloc[0]['region']

    # Monthly trend
    df, error = execute_safe_query("""
                                   SELECT strftime('%Y-%m', date) as month, SUM(amount) as revenue
                                   FROM sales
                                   GROUP BY month
                                   ORDER BY month
                                   """)
    if df is not None and len(df) > 1:
        summary['growth'] = ((df['revenue'].iloc[-1] - df['revenue'].iloc[0]) / df['revenue'].iloc[0]) * 100

    return summary


def suggest_support_ticket(context):
    """Tool 3: Suggest creating a support ticket"""
    suggestion = f"🤖 Agent Suggestion: Having trouble with '{context}'? Consider creating a support ticket for human assistance!"
    print(f"[TICKET LOG] Suggested support ticket for: {context}")
    return suggestion


# ============================================
# AGENT LOGIC
# ============================================
class DataInsightsAgent:
    """Simple agent that uses keyword matching and safe query tools"""

    def __init__(self):
        self.tools = {
            'execute_safe_query': execute_safe_query,
            'get_data_summary': get_data_summary,
            'suggest_support_ticket': suggest_support_ticket
        }
        print("[AGENT LOG] Agent initialized with 3 tools")

    def process_query(self, user_input):
        """Process user input and return appropriate response"""
        print(f"\n{'=' * 60}")
        print(f"[AGENT LOG] Processing: '{user_input}'")

        user_input_lower = user_input.lower()
        response = ""
        data = None

        # Check for greetings
        if any(word in user_input_lower for word in ['hello', 'hi', 'hey']):
            response = "Hello! I'm your Data Insights Assistant. Ask me about sales data!"

        # Check for total sales
        elif 'total' in user_input_lower and 'sales' in user_input_lower:
            print("[AGENT LOG] Using tool: execute_safe_query (total sales)")
            df, error = self.tools['execute_safe_query'](
                "SELECT SUM(amount) as total_sales, COUNT(*) as transactions FROM sales"
            )
            if df is not None:
                total = df['total_sales'].iloc[0]
                count = df['transactions'].iloc[0]
                response = f"**Total Sales Summary:**\n"
                response += f"- Total Revenue: **${total:,.2f}**\n"
                response += f"- Number of Transactions: **{count:,}**\n"
                response += f"- Average Transaction: **${total / count:,.2f}**"
                data = df
            else:
                response = f"❌ {error}"

        # Check for best product
        elif any(word in user_input_lower for word in ['best', 'top', 'popular']) and 'product' in user_input_lower:
            print("[AGENT LOG] Using tool: execute_safe_query (best product)")
            df, error = self.tools['execute_safe_query']("""
                                                         SELECT product, SUM(amount) as revenue, COUNT(*) as units_sold
                                                         FROM sales
                                                         GROUP BY product
                                                         ORDER BY revenue DESC LIMIT 3
                                                         """)
            if df is not None:
                response = "**Top 3 Products by Revenue:**\n\n"
                for idx, row in df.iterrows():
                    response += f"{idx + 1}. **{row['product']}**\n"
                    response += f"   - Revenue: ${row['revenue']:,.2f}\n"
                    response += f"   - Units Sold: {row['units_sold']:,}\n"
                data = df

        # Check for regional analysis
        elif any(word in user_input_lower for word in ['region', 'area', 'country']):
            print("[AGENT LOG] Using tool: execute_safe_query (regional)")
            df, error = self.tools['execute_safe_query']("""
                                                         SELECT region, SUM(amount) as revenue, COUNT(*) as transactions
                                                         FROM sales
                                                         GROUP BY region
                                                         ORDER BY revenue DESC
                                                         """)
            if df is not None:
                response = "**Sales by Region:**\n\n"
                for _, row in df.iterrows():
                    response += f"**{row['region']}**\n"
                    response += f"- Revenue: ${row['revenue']:,.2f}\n"
                    response += f"- Transactions: {row['transactions']:,}\n\n"
                data = df

        # Check for trend analysis
        elif any(word in user_input_lower for word in ['trend', 'month', 'growth', 'over time']):
            print("[AGENT LOG] Using tool: execute_safe_query (trend)")
            df, error = self.tools['execute_safe_query']("""
                                                         SELECT strftime('%Y-%m', date) as month, 
                       SUM(amount) as revenue,
                       COUNT(*) as transactions
                                                         FROM sales
                                                         GROUP BY month
                                                         ORDER BY month
                                                             LIMIT 6
                                                         """)
            if df is not None:
                response = "**Recent Monthly Trends (Last 6 months):**\n\n"
                for _, row in df.iterrows():
                    response += f"**{row['month']}**\n"
                    response += f"- Revenue: ${row['revenue']:,.2f}\n"
                    response += f"- Transactions: {row['transactions']:,}\n\n"
                data = df

        # Check for data summary
        elif any(word in user_input_lower for word in ['summary', 'overview', 'insight']):
            print("[AGENT LOG] Using tool: get_data_summary")
            summary = self.tools['get_data_summary']()
            response = "**Business Insights Summary:**\n\n"
            response += f"- Total Sales: **${summary.get('total_sales', 0):,.2f}**\n"
            response += f"- Top Product: **{summary.get('top_product', 'N/A')}** "
            response += f"(Revenue: ${summary.get('top_product_revenue', 0):,.2f})\n"
            response += f"- Top Region: **{summary.get('top_region', 'N/A')}**\n"
            if 'growth' in summary:
                response += f"- Growth Trend: **{summary['growth']:.1f}%**\n"

        # Check for help or support
        elif any(word in user_input_lower for word in ['help', 'support', 'ticket', 'issue', 'problem']):
            print("[AGENT LOG] Using tool: suggest_support_ticket")
            response = self.tools['suggest_support_ticket'](user_input)

        # Default response for unknown queries
        else:
            response = f"I can help you analyze sales data! Try asking about:\n"
            response += "- Total sales revenue\n"
            response += "- Best selling products\n"
            response += "- Regional performance\n"
            response += "- Sales trends over time\n\n"
            response += "Or use the sidebar to create a support ticket for complex queries."
            print("[AGENT LOG] No specific tool matched - providing general help")

        print(f"[AGENT LOG] Response prepared ({len(response)} chars)")
        print(f"{'=' * 60}")

        return response, data


# ============================================
# MAIN APPLICATION
# ============================================
def main():
    st.title("📊 Data Insights Chat Application")
    st.markdown("Chat with your sales data using natural language. *All queries are safe and read-only.*")

    # Initialize database
    conn = create_database()

    # Initialize agent
    if "agent" not in st.session_state:
        st.session_state.agent = DataInsightsAgent()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant",
             "content": "👋 Welcome! I'm your Data Insights Assistant. Ask me anything about the sales data!"}
        ]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Display data as table if present
            if "data" in message and message["data"] is not None:
                with st.expander("📋 View Data", expanded=False):
                    st.dataframe(message["data"], use_container_width=True)

    # Chat input
    if prompt := st.chat_input("Ask about your sales data..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyzing your query..."):
                response, data = st.session_state.agent.process_query(prompt)

                # Display response
                st.markdown(response)

                # Display data table if available
                if data is not None:
                    with st.expander("📊 View Detailed Data", expanded=False):
                        st.dataframe(data, use_container_width=True)

        # Store assistant response in history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "data": data
        })


# ============================================
# RUN THE APPLICATION
# ============================================