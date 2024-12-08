import streamlit as st
import requests
import json
import urllib3
import webbrowser

# Disable SSL verification warnings 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
API_URL = "https://syllabi.communitystar.com/infer/{phrase}"  

def main():
    st.title("UNC Charlotte DSBA Course Assistant")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_question = st.text_input("Ask a question about DSBA courses and syllabi:", key="user_input")
    st.info("Hi! I’m a Q&A bot. I can help with your questions, but I don’t remember what we’ve talked about before.")
    if st.button("Submit"):
        with st.spinner("Processing..."):
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
    for chat in reversed(st.session_state.chat_history):
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
        
        if st.button("Feedback Form"):
            webbrowser.open_new_tab("https://forms.gle/Uz7M3xpVsdKe2NPz6")


if __name__ == "__main__":
    main()