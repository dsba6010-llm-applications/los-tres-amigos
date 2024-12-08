import streamlit as st
import requests
import json
import urllib3

# Disable SSL verification warnings 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
API_URL = "https://syllabi.communitystar.com/infer/{phrase}"  

def main():
    st.title("NinerKnows Course Assistant")
    st.markdown("### I am a simple Q&A bot, I do not know how to remember what I told you in previous questions")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_question = st.text_input("Ask a question about DSBA courses:", key="user_input")

    if st.button("Submit"):
        if user_question:
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

        st.markdown(
        """
        Course Syllabi List - [https://dsba.charlotte.edu/syllabi/](https://dsba.charlotte.edu/syllabi/)  <br> <br>
        Available Courses - Consult DSBA website (https://dsba.charlotte.edu/curriculum/course-catalog/) for full list of active courses for current semester
        """,
        unsafe_allow_html=True,
        )
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

if __name__ == "__main__":
    main()