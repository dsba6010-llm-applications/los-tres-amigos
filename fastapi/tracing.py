# tracing.py

from langfuse import Langfuse
import os
from dotenv import load_dotenv
import time
import logging
from functools import wraps

# Load environment variables
load_dotenv()

class SimpleTracer:
    def __init__(self):
        """Initialize the tracer with Langfuse credentials from environment variables."""
        # Get credentials from environment variables
        secret_key = os.getenv('LANGFUSE_SECRET_KEY')
        public_key = os.getenv('LANGFUSE_PUBLIC_KEY')
        
        if not secret_key or not public_key:
            raise ValueError("Missing required environment variables: LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY")
        
        self.langfuse = Langfuse(
            secret_key=secret_key,
            public_key=public_key,
            host="https://us.cloud.langfuse.com"
        )
        self.logger = logging.getLogger(__name__)
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def trace_function(self, function_name):
        """Basic function tracing decorator."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Create a unique trace ID
                trace_id = f"{function_name}_{int(time.time())}"
                
                # Start trace
                trace = self.langfuse.trace(
                    id=trace_id,
                    name=function_name,
                    metadata={
                        "function": function_name,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                )
                
                try:
                    # Log the start of function execution
                    self.logger.info(f"Starting {function_name}")
                    
                    # Execute the function and measure time
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # Update trace with success information
                    trace.update(
                        metadata={
                            "status": "success",
                            "execution_time": execution_time,
                            "args": str(args),
                            "kwargs": str(kwargs)
                        }
                    )
                    
                    self.logger.info(f"Completed {function_name} in {execution_time:.2f} seconds")
                    return result
                
                except Exception as e:
                    # Log error if execution fails
                    error_message = str(e)
                    self.logger.error(f"Error in {function_name}: {error_message}")
                    
                    # Update trace with error information
                    trace.update(
                        metadata={
                            "status": "error",
                            "error_message": error_message
                        }
                    )
                    raise
            
            return wrapper
        return decorator