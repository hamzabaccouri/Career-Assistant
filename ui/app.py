import streamlit as st

class CareerAssistantApp:
    def __init__(self):
        pass  # No initialization needed for now

    def run(self):
        st.title("Career Application Assistant - Hello World")
        
        # Simple Sidebar
        with st.sidebar:
            st.header("Sidebar")
            st.write("This is a simple sidebar for testing.")
        
        # Main content area
        st.write("Welcome to the Career Application Assistant!")
        st.write("This is a minimal example to test if Streamlit is working.")
        
        # Button to show a message
        if st.button("Say Hello"):
            st.success("Hello, Streamlit is working!")

if __name__ == "__main__":
    app = CareerAssistantApp()
    app.run()
