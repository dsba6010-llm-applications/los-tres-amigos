# verify_tracing.py

from dotenv import load_dotenv
import time
import logging
from tracing import SimpleTracer  # Import the SimpleTracer class

# Load environment variables first
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tracer instance BEFORE using it in decorators
tracer = SimpleTracer()

# Test 1: Basic function tracing
@tracer.trace_function("test_basic_function")
def test_basic():
    logger.info("Running basic tracing test")
    time.sleep(1)  # Simulate some work
    return "Basic test complete"

# Test 2: Function with parameters
@tracer.trace_function("test_with_params")
def test_parameters(param1: str, param2: int):
    logger.info(f"Testing with parameters: {param1}, {param2}")
    time.sleep(1)  # Simulate some work
    return f"Parameter test complete: {param1}, {param2}"

# Test 3: Error handling
@tracer.trace_function("test_error_handling")
def test_error():
    logger.info("Testing error handling")
    raise ValueError("Test error")

def run_verification():
    print("\n=== Starting Tracing Verification ===\n")
    
    # Test 1: Basic Tracing
    try:
        print("1. Testing basic tracing...")
        result = test_basic()
        print(f"   Result: {result}")
        print("   ✅ Basic tracing test passed")
    except Exception as e:
        print(f"   ❌ Basic tracing test failed: {str(e)}")

    # Test 2: Parameter Tracing
    try:
        print("\n2. Testing tracing with parameters...")
        result = test_parameters("test_string", 42)
        print(f"   Result: {result}")
        print("   ✅ Parameter tracing test passed")
    except Exception as e:
        print(f"   ❌ Parameter tracing test failed: {str(e)}")

    # Test 3: Error Handling
    try:
        print("\n3. Testing error handling...")
        test_error()
    except ValueError:
        print("   ✅ Error handling test passed (expected error caught)")
    except Exception as e:
        print(f"   ❌ Error handling test failed: {str(e)}")

    print("\n=== Verification Complete ===")
    print("\nNext Steps:")
    print("1. Check your Langfuse dashboard for traces")
    print("2. Verify that you see three traces:")
    print("   - test_basic_function")
    print("   - test_with_params")
    print("   - test_error_handling")
    print("3. Verify that the error trace shows the test error")
    print("4. Check that parameters are properly logged")

if __name__ == "__main__":
    run_verification()