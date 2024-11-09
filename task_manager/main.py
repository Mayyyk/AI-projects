from anthropic import Anthropic
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
api_key = os.getenv('ANTHROPIC_API_KEY')

# Initialize Anthropic client
client = Anthropic(api_key=api_key)

tasks = []

while True:
    # Get task from user
    task_name = input("\nEnter task name (or 'quit' to exit): ")
    if task_name.lower() == 'quit':
        break
    
    # Prepare the prompt with existing tasks
    tasks_description = "\n".join([f"- {t['name']} (Priority: {t['priority']})" for t in tasks])
    prompt = f"""Given these existing tasks with priorities:

{tasks_description}

Analyze this new task: "{task_name}"
Analyze the existing tasks and this new task. Your response should follow this format:
1. List the existing tasks in priority order (from highest to lowest)
2. Explain your reasoning for where the new task fits
3. State where the new task belongs in the priority order

Respond ONLY with these 3 sections, no other text."""

    # Make API call
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        temperature=0.1,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )
    
    # Get priority from Claude's response
    priority = message.content.strip()
    
    # Add new task to list
    tasks.append({
        "name": task_name,
        "priority": priority
    })
    
    # Show all tasks
    print("\nCurrent tasks:")
    for task in tasks:
        print(f"• {task['name']} - Priority: {task['priority']}")