import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def print_agent_response(title, response):
    if title == "FINAL BUSINESS STRATEGY":
        print(f"\n{'=' * 50}")
        print(f"📌 {title}")
        print(f"{'=' * 50}")
        print(response)
        print(f"{'=' * 50}\n")

def get_clarity(user_input):
    print("\n🤔 Clarity Agent is analyzing your idea...")
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a clarity expert. Help entrepreneurs understand how they can monetize their skills with AI."},
            {"role": "user", "content": user_input}
        ]
    )
    result = response.choices[0].message.content
    print_agent_response("CLARITY ANALYSIS", result)
    return result

def get_niche(clarity_response):
    print("\n🎯 Niche Agent is identifying your target market...")
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a niche expert. Help identify specific target market and ideal customer avatar."},
            {"role": "user", "content": f"Based on this information, help identify the perfect niche and target avatar: {clarity_response}"}
        ]
    )
    result = response.choices[0].message.content
    print_agent_response("NICHE ANALYSIS", result)
    return result

def get_action_plan(niche_response):
    print("\n📝 Action Agent is creating your step-by-step plan...")
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an action expert. Provide specific, actionable steps for business growth."},
            {"role": "user", "content": f"Create an action plan based on this information: {niche_response}"}
        ]
    )
    result = response.choices[0].message.content
    print_agent_response("ACTION PLAN", result)
    return result

def get_final_strategy(user_input, clarity_response, niche_response, action_response):
    print("\n🎓 Business Strategist is finalizing your complete strategy...")
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert business strategist. Present a comprehensive business strategy with clear, actionable steps. Your response should: 1) Summarize the core business concept and target market, 2) List specific, prioritized action steps with timelines, 3) Address potential challenges and provide solutions, 4) Include risk mitigation strategies, and 5) Highlight key success metrics. Be direct, practical, and thorough while anticipating and addressing common concerns or objections the entrepreneur might have."},
            {"role": "user", "content": f"""Based on the user's original input: "{user_input}"

Summarize this business strategy:
            Clarity Analysis: {clarity_response}
            Niche Analysis: {niche_response}
            Action Plan: {action_response}"""}
        ]
    )
    result = response.choices[0].message.content
    print_agent_response("FINAL BUSINESS STRATEGY", result)
    return result

def main():
    print("\n🚀 Welcome to AI Business Advisor!")
    user_input = input("\n💭 Tell me about your business idea or skills: ")
    
    # Process through each agent silently
    clarity_response = get_clarity(user_input)
    niche_response = get_niche(clarity_response)
    action_response = get_action_plan(niche_response)
    final_strategy = get_final_strategy(user_input, clarity_response, niche_response, action_response)
    
    # Ask for follow-up questions
    while True:
        follow_up = input("\n❓ Do you have any questions about the strategy? (Type 'exit' to end): ")
        if follow_up.lower() == 'exit':
            print("\n👋 Thank you for using AI Business Advisor! Good luck with your business journey!")
            break
        elif follow_up.strip():
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful business advisor. Answer questions about the previously provided business strategy."},
                    {"role": "user", "content": f"Previous strategy: {final_strategy}\n\nUser question: {follow_up}"}
                ]
            )
            print("\n🤝 Answer:")
            print(response.choices[0].message.content)

if __name__ == "__main__":
    main()

