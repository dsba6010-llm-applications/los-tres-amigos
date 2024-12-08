import streamlit as st
import requests
import json
import urllib3
import webbrowser


st.set_page_config(
    page_title="NinerKnows Course Assistant",  # Title of the browser tab
    page_icon="favicon.ico",               # Favicon (can be an emoji, URL, or local file path)
    layout="centered",            # Layout options: "centered" or "wide"
    initial_sidebar_state="expanded", # Sidebar state: "auto", "expanded", "collapsed"
)

# Disable SSL verification warnings 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
API_URL = "https://syllabi.communitystar.com/infer/{phrase}"  

# Initialize session state for the disclaimer
if "disclaimer_accepted" not in st.session_state:
    st.session_state.disclaimer_accepted = False

# Show the disclaimer only if it has not been accepted
if not st.session_state.disclaimer_accepted:
    # Simulated pop-up disclaimer
    st.markdown("### Disclaimer")
    st.markdown(
        """
        This application is not affiliated with, endorsed by, or officially connected to the University of North Carolina at Charlotte (UNCC). 
        All information and content provided here are for informational purposes only.
        """
    )
    if st.button("I Acknowledge"):
        st.session_state.disclaimer_accepted = True
        st.query_params = {"acknowledged": "true"}  # Set query parameters
        st.stop()  # Prevent further execution until acknowledgment
else:
    # Main application function
    def main():

        # Main content
        st.image("image.png")  # Add logo with controlled width
        st.title("NinerKnows Course Assistant")
        st.info(
            "Hi! I’m a Q&A bot. I can help with your questions, but I don’t remember what we’ve talked about before."
        )

        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        user_question = st.text_input("Ask a question about DSBA courses and syllabi:")
        acknowledged = st.checkbox(
            "I understand that this chatbot is for general use, and I should not input any sensitive or personally identifiable information (PII)."
        )
        submit = st.button("Ask")

        # Conditional behavior based on acknowledgment
        if not acknowledged:
            st.warning("You must acknowledge the notice before proceeding.")

        if acknowledged and user_question:
            if submit:
                with st.spinner("Processing..."):
                    try:
                        response = requests.get(
                            API_URL.format(phrase=user_question),
                            verify=False
                        )
                        
                        if response.status_code == 200:
                            answer = response.json()["answer"]
                            # Insert new chat at the beginning of the list
                            st.session_state.chat_history.insert(0, {"question": user_question, "answer": answer})
                        else:
                            st.error(f"Error: {response.status_code}")

                    except Exception as e:
                        st.error(f"Error connecting to the server: {str(e)}")


            # Display chat history
            st.markdown("### Conversation History")
            for chat in st.session_state.chat_history:
                st.markdown(f"**Question:** {chat['question']}")
                st.markdown(f"**Answer:** {chat['answer']}")
                st.markdown("---")


        # Add sidebar with additional features
        with st.sidebar:
            st.header("About")
            st.markdown("""
            This chatbot helps answer questions about DSBA courses at UNC Charlotte.
            It uses RAG (Retrieval Augmented Generation) to provide accurate information
            from course syllabi.
            """)
            
            # Add course list from syllabi
            st.header("Available Courses")
            try:
                response = requests.get(f"{API_URL}/c_store")
                if response.status_code == 200:
                    courses = response.json()
                    for doc_id in courses:
                        course_info = courses[doc_id]["chunks"][f"{doc_id}.full"]["metadata"]
                        st.markdown(f"- {course_info['course_number']}: {course_info['course_title']}")
            except:
                st.warning("Unable to load course list")

            # Feedback button
            if st.button("Feedback Form"):
                webbrowser.open_new_tab("https://forms.gle/Uz7M3xpVsdKe2NPz6")

        # Run the main application
    main()
