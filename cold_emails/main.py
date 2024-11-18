import os
from dotenv import load_dotenv
from groq import Groq
from together import Together
from openai import OpenAI

def initialize_clients():
    """Initialize API clients for different LLM providers."""
    load_dotenv()
    
    perplexity_client = OpenAI(
        api_key=os.environ.get("PERPLEXITY_API_KEY"),
        base_url="https://api.perplexity.ai"
    )
    
    openai_client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    
    return perplexity_client, openai_client


def generate_search_queries(client, user_input, model="gpt-4o"):
    """Generate search queries for potential clients."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert in market research and lead generation. YOU MUST ONLY PROVIDE THE SEARCH QUERIES, NOTHING ELSE. ONLY THE LIST OF 5 SEARCH QUERIES."},
            {"role": "user", "content": f"Generate a list of 5 search queries to recognize potential clients interests, needs, pain points, and challenges this industry: #### {user_input} ####"},
        ]
    )
    
    queries = response.choices[0].message.content
    return [query.strip() for query in queries.split('\n') if query.strip()]

def perform_web_search(client, queries):
    """Perform web searches for each query and return relevant results."""
    search_results = []
    for query in queries:
        print("performing search for: ", query)
        response = client.chat.completions.create(
            model="llama-3.1-sonar-large-128k-online",
            messages=[
                {"role": "system", "content": "You are a research assistant. Search the web and provide detailed, factual results about market situations, trends, and opportunities."},
                {"role": "user", "content": f"Search the web for: {query}\nProvide specific companies' problems, needs, and challenges. Format the response as a structured list."}
            ],
        )
        search_results.append({
            'query': query,
            'search_results': response.choices[0].message.content
        })
    return search_results

def process_search_queries(client, search_results):
    """Process search results and generate personalized outreach messages."""
    results = []
    for result in search_results:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a marketing assistant helping with cold outreach based on the market situation, trends, and opportunities."},
                {"role": "user", "content": f"Based on these search results about '{result['query']}':\n\n{result['search_results']}\n\nDraft personalized outreach messages for companies, highlighting specific details about common problems, needs, and challenges in their industry."}
            ],
        )
        results.append({
            'query': result['query'],
            'search_results': result['search_results'],
            'outreach_messages': response.choices[0].message.content
        })
    return results

def main():
    # Initialize clients
    perplexity_client, openai_client = initialize_clients()
    user_input = input("Enter the industry you want to target: ")
    # Generate search queries
    search_queries = generate_search_queries(openai_client, user_input)
    print("Generated Search Queries:")
    print("\n".join(search_queries))
    print("\n" + "-"*50)
    
    # Perform web searches
    print("\nPerforming web searches...")
    search_results = perform_web_search(perplexity_client, search_queries)
    
    # Process results and generate outreach messages
    results = process_search_queries(openai_client, search_results)
    
    # Print final results
    for result in results:
        print(f"\nQuery: '{result['query']}'")
        print("\nSearch Results:")
        print(result['search_results'])
        print("\nGenerated Outreach Messages:")
        print(result['outreach_messages'])
        print("\n" + "-"*50)

if __name__ == "__main__":
    main()
