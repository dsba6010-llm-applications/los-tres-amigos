import streamlit as st
import requests
import json
import urllib3

# Disable SSL verification warnings 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
API_URL = "https://syllabi.communitystar.com/infer/{phrase}"  

def main():
    st.title("UNC Charlotte DSBA Course Assistant")
    st.markdown("### Ask questions about DSBA courses and syllabi")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_question = st.text_input("Ask a question about DSBA courses:", key="user_input")

    if st.button("Submit"):
        if user_question:
            try:
# Make API call with SSL verification disabled
                response = requests.get(
                    API_URL.format(phrase=user_question),
                    verify=False  # Disable SSL verification
                )
                
                if response.status_code == 200:
                    answer = response.json()["answer"]
                    st.session_state.chat_history.append({"question": user_question, "answer": answer})
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

if __name__ == "__main__":
    main()