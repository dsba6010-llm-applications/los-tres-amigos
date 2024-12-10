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
            if st.button("Feedback Form"):
                webbrowser.open_new_tab("https://forms.gle/Uz7M3xpVsdKe2NPz6")
            # Add course list from syllabi
            emoji_link = """
            <div style="text-align: center;">
                <a href="https://dsba.charlotte.edu/syllabi/" target="_blank" style="text-decoration: none;", title="Go to List of DSBA Syllabi">
            📃
                </a>
                <a href="https://dsba.charlotte.edu/curriculum/course-catalog/" target="_blank" style="text-decoration: none; margin: 0 10px;", title="Go to Course Catalog">
                🏫
                </a>
            </div>
            """

# Add the clickable emoji to the sidebar
            st.sidebar.markdown(emoji_link, unsafe_allow_html=True)
            st.markdown("**Required Courses**")
            st.markdown("""
            - DSBA 5122 - Visual Analytics and Storytelling 
            - DSBA 6156 - Applied Machine Learning
            - DSBA 6160 - Database Systems for Data Scientists
            - DSBA 6201 - Business Intelligence and Analytics
            - DSBA 6211 - Advanced Business Analytics
            - DSBA 6276 - Strategic Business Analytics
            """)

            st.markdown("**Data Science Elective Courses**")
            st.markdown("""
            - DSBA 6155 - Knowledge-Based Systems
            - DSBA 6162 - Data Mining
            - DSBA 6165 - Artificial Intelligence and Deep Learning
            - DSBA 6188 - Text Mining and Information Retrieval
            - DSBA 6190 - Cloud Computing for Data Analysis
            - DSBA 6345 - Modern Data Science Systems
            - DSBA 6322 - Complex Adaptive Systems
            - DSBA 6326 - Network Science
            """)

            st.markdown("**Business Analytics Elective Courses**")
            st.markdown("""
            - DSBA 6100 - Big Data Analytics for Competitive Advantage
            - DSBA 6112 - Graduate Econometrics
            - DSBA 6122 - Decision Modeling and Analysis
            - DSBA 6207 - Business Project Management
            - DSBA 6208 - Supply Chain Management
            - DSBA 6213 - Applied Healthcare Business Analytics
            - DSBA 6277 - Social Media Marketing and Analytics
            - DSBA 6284 - Digital Marketing Analytics
            """)

            st.markdown("**Other Elective Courses**")
            st.markdown("""
            - DSBA 6010 - Special Topics in Data Science and Business Analytics
            - DSBA 6115 - Statistical Learning with Big Data 
            - DSBA 6170 - Ethics, Privacy, Security and Governance of Big Data 
            """)



        # Run the main application
    main()
