# Install ERAlchemy first: pip install eralchemy
from eralchemy import render_er
# Generate ER Diagram
render_er('postgresql+psycopg2://dhms_user:dhms_05@localhost/dhms_db', 'er_diagram.png')
#from graphviz import Digraph

#dfd = Digraph('DFD', filename='dfd_diagram', format='png')
#dfd.attr(rankdir='LR')
# Add nodes
#dfd.node('User', 'User')
#dfd.node('Frontend', 'Frontend Interface')
#dfd.node('Backend', 'Backend (Flask)')
#dfd.node('Database', 'Database (PostgreSQL)')
# Add edges
#dfd.edge('User', 'Frontend', 'Inputs Data')
#dfd.edge('Frontend', 'Backend', 'Sends Requests')
#dfd.edge('Backend', 'Database', 'Fetch/Update Data')
#dfd.edge('Database', 'Backend', 'Returns Data')
#dfd.edge('Backend', 'Frontend', 'Responds with Data')
#dfd.edge('Frontend', 'User', 'Displays Outputs')
# Save and render the diagram
#dfd.render()

# from diagrams import Diagram
# from diagrams.generic.device import Mobile
# from diagrams.programming.language import Python
# from diagrams.onprem.database import PostgreSQL
# from diagrams.generic.network import Internet

# with Diagram("Workflow Diagram", show=False, direction="LR"):
#     user = Mobile("User")
#     frontend = Python("Frontend (HTML/CSS/JS)")
#     backend = Python("Backend (Flask)")
#     database = PostgreSQL("Database")
#     otp = Internet("OTP Service")

#     user >> frontend >> backend >> database
#     backend >> otp
