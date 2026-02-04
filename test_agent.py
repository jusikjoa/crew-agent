"""
Quick test script for the AI Agent
"""
import sys
sys.path.insert(0, 'src')

from agent import create_agent

# Create agent
print("Creating AI Agent...")
agent = create_agent(
    model_name="gpt-4",
    temperature=0.7,
    verbose=False
)

# Test simple query
print("\n=== Test 1: Simple Question ===")
response = agent.run("Hello! What can you help me with?")
print(f"Agent: {response}")

print("\n=== Agent is ready! ===")
print("You can now:")
print("1. Run: cd src && python main.py (for interactive mode)")
print("2. Or use the agent in your Python code")
