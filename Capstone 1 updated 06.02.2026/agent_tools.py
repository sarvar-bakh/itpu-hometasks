import json
import requests
from datetime import datetime


class AgentTools:
    def __init__(self, db_manager):
        self.db = db_manager
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "query_database",
                    "description": "Execute safe SQL queries to get data from the database. Use for data analysis, filtering, and aggregation.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The SQL SELECT query to execute (READ-ONLY operations only)"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_database_stats",
                    "description": "Get aggregated statistics and insights about the database contents.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_support_ticket",
                    "description": "Create a support ticket for human assistance. Use when user requests help or when unable to answer a question.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title of the support ticket"
                            },
                            "description": {
                                "type": "string",
                                "description": "Detailed description of the issue"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["Low", "Medium", "High", "Critical"],
                                "description": "Priority level of the ticket"
                            }
                        },
                        "required": ["title", "description"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_schema_info",
                    "description": "Get information about database tables and their columns.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]

    def query_database(self, query):
        """Execute a safe database query"""
        try:
            print(f"LOG | Executing query: {query}")
            result = self.db.execute_safe_query(query)
            return json.dumps({"success": True, "data": result, "row_count": len(result)})
        except PermissionError as e:
            print(f"LOG | Blocked dangerous query: {query}")
            return json.dumps({"success": False, "error": str(e)})
        except Exception as e:
            print(f"LOG | Query error: {str(e)}")
            return json.dumps({"success": False, "error": str(e)})

    def get_database_stats(self):
        """Get database statistics"""
        try:
            stats = self.db.get_database_stats()
            print(f"LOG | Retrieved database stats: {stats}")
            return json.dumps({"success": True, "stats": stats})
        except Exception as e:
            print(f"LOG | Error getting stats: {str(e)}")
            return json.dumps({"success": False, "error": str(e)})

    def create_support_ticket(self, title, description, priority="Medium"):
        """Create a support ticket"""
        try:
            ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d')}-{hash(title + description) % 10000:04d}"

            self.db.cursor.execute('''
                                   INSERT INTO support_tickets (ticket_id, title, description, status, priority, created_date)
                                   VALUES (?, ?, ?, ?, ?, ?)
                                   ''', (ticket_id, title, description, "Open", priority, datetime.now()))

            self.db.connection.commit()

            # In a real implementation, this would connect to Jira/GitHub/etc.
            # For now, we'll just log it
            print(f"LOG | Created support ticket: {ticket_id}")
            print(f"LOG | Title: {title}")
            print(f"LOG | Priority: {priority}")

            return json.dumps({
                "success": True,
                "ticket_id": ticket_id,
                "message": f"Support ticket '{ticket_id}' has been created with priority '{priority}'. A human agent will contact you shortly."
            })
        except Exception as e:
            print(f"LOG | Error creating ticket: {str(e)}")
            return json.dumps({"success": False, "error": str(e)})

    def get_schema_info(self):
        """Get database schema information"""
        try:
            schema = self.db.get_schema_info()
            print(f"LOG | Retrieved schema info")
            return json.dumps({"success": True, "schema": schema})
        except Exception as e:
            print(f"LOG | Error getting schema: {str(e)}")
            return json.dumps({"success": False, "error": str(e)})

    def execute_tool(self, tool_name, arguments):
        """Execute a tool by name with arguments"""
        if tool_name == "query_database":
            return self.query_database(**arguments)
        elif tool_name == "get_database_stats":
            return self.get_database_stats()
        elif tool_name == "create_support_ticket":
            return self.create_support_ticket(**arguments)
        elif tool_name == "get_schema_info":
            return self.get_schema_info()
        else:
            return json.dumps({"success": False, "error": f"Unknown tool: {tool_name}"})