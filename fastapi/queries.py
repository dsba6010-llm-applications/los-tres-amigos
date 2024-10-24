#example queries

class Syllabi:
    def __init__(self) -> None:
                pass
        self.courses = self.load_courses()


    def handle_query(self, query: str) -> str:
        """
        Main method to handle incoming queries.
        Detects ambiguous queries and prompts users for clarification.
        """
        # Check if query is ambiguous
        if self.is_ambiguous(query):
            return self.prompt_for_clarification(query)
        else:
            return self.process_query(query)

    def is_ambiguous(self, query: str) -> bool:
        """
        Detect if a query is ambiguous
        Returns True if ambiguous, False otherwise.
        """
        # Example: Detect if the query doesn't mention a course or is too vague
        ambiguous_keywords = ['assignment', 'due date', 'exam', 'syllabus']
        if any(keyword in query.lower() for keyword in ambiguous_keywords) and not self.contains_course_name(query):
            return True
        return False
    
    def contains_course_name(self, query: str) -> bool:
        """
        Check if the query contains a valid course name.
        """
        for course in self.courses:
            if course.lower() in query.lower():
                return True
        return False

    def prompt_for_clarification(self, query: str) -> str:
        """
        Prompt the user for clarification when the query is ambiguous.
        """
        # Example clarification prompts
        if 'assignment' in query.lower():
            return "Which course are you asking about for the assignment due date?"
        if 'exam' in query.lower():
            return "Which course are you referring to for the exam schedule?"
        return "Can you clarify which course or more specific detail you're asking about?"

    def process_query(self, query: str) -> str:
        """
        Process the query after ambiguity is resolved or if it's clear.
        """
        # Placeholder logic
        return f"Here is the information for your query: '{query}'"

    def load_courses(self) -> list:
        """
        Load available courses (mockup for demo purposes).
        """
        return ['DSBA 6010', 'DSBA 6165', 'DSBA 6120']  # Example course list
