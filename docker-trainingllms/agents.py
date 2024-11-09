import os
import anthropic
import csv
from prompts import *

def get_api_key():
    print("\n🔑 API Key Setup")
    api_key = input("Please enter your Anthropic API key: ")
    return api_key

def read_csv_file(file_path):
    print(f"\n📂 Reading CSV file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader)
            data = list(csv_reader)
            print(f"✅ Successfully read {len(data)} rows of data")
            return header, data
    except FileNotFoundError:
        print(f"❌ Error: File '{file_path}' not found.")
        return None, None
    except Exception as e:
        print(f"❌ Error reading CSV file: {str(e)}")
        return None, None

def append_to_csv(file_path, new_rows):
    print(f"\n💾 Saving new data to: {file_path}")
    try:
        with open(file_path, 'a', newline='', encoding='utf-8') as file:
            csv_writer = csv.writer(file)
            for row in new_rows:
                csv_writer.writerow(row)
        print(f"✅ Successfully appended {len(new_rows)} new rows to the file")
    except Exception as e:
        print(f"❌ Error appending to CSV file: {str(e)}")

def analyze_data(client, file_path):
    header, data = read_csv_file(file_path)
    if header is None or data is None:
        return None
    
    print("\n🔍 Analyzing data patterns and structure...")
    csv_summary = f"Header: {header}\nFirst few rows: {data[:3]}"
    
    analysis = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1000,
        temperature=0.1,
        system=ANALYZER_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": ANALYZER_USER_PROMPT.format(csv_summary=csv_summary)
        }]
    )
    
    print("✅ Analysis complete!")
    return analysis.content[0].text

def generate_data(client, file_path, num_rows, analysis_summary):
    header, data = read_csv_file(file_path)
    if header is None or data is None:
        return None
    
    print(f"\n🔄 Generating {num_rows} new rows based on the analysis...")
    csv_summary = f"Header: {header}\nFirst few rows: {data[:3]}"
    
    # Keep generating until we have enough rows
    generated_rows = []
    max_attempts = 5
    attempts = 0
    
    while len(generated_rows) < num_rows and attempts < max_attempts:
        attempts += 1
        remaining_rows = num_rows - len(generated_rows)
        print(f"Attempt {attempts}: Generating {remaining_rows} more rows...")
        
        generation = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1500,
            temperature=1,
            system=GENERATOR_SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": GENERATOR_USER_PROMPT.format(
                    csv_summary=csv_summary,
                    num_rows=remaining_rows,
                    analysis_summary=analysis_summary
                )
            }]
        )
        
        # Use CSV reader to properly handle quoted fields
        import io
        csv_data = io.StringIO(generation.content[0].text)
        csv_reader = csv.reader(csv_data)
        new_rows = [row for row in csv_reader if row and not any(cell.startswith('#') for cell in row)]
        
        generated_rows.extend(new_rows)
        
        # If we got too many rows, trim the excess
        if len(generated_rows) > num_rows:
            generated_rows = generated_rows[:num_rows]
            break
        
        if len(generated_rows) < num_rows:
            print(f"Still need {num_rows - len(generated_rows)} more rows...")
    
    if len(generated_rows) < num_rows:
        print(f"⚠️ Warning: Could only generate {len(generated_rows)} out of {num_rows} requested rows")
    else:
        print(f"✅ Successfully generated all {num_rows} requested rows")
    
    return generated_rows

def get_summary(client, analysis):
    print("\n📝 Creating summary of analysis...")
    summary = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=300,
        temperature=0.1,
        system="You are an AI assistant that creates clear, concise summaries.",
        messages=[{
            "role": "user",
            "content": f"Summarize the following analysis in one clear paragraph:\n{analysis}"
        }]
    )
    return summary.content[0].text

def copy_file_from_container(source_path, destination_path="./output.csv"):
    print(f"\n📋 Copying generated data to local file: {destination_path}")
    try:
        # Read the original file with all data (including new rows)
        with open(source_path, 'r', encoding='utf-8') as source:
            csv_reader = csv.reader(source)
            header = next(csv_reader)  # Get header
            data = list(csv_reader)    # Get all rows
        
        print(f"Found {len(data)} total rows")
        
        # Write all data to the output file
        with open(destination_path, 'w', newline='', encoding='utf-8') as dest:
            csv_writer = csv.writer(dest)
            csv_writer.writerow(header)  # Write header first
            csv_writer.writerows(data)   # Write all rows
            
        print(f"✅ Successfully copied {len(data)} rows to {destination_path}")
    except Exception as e:
        print(f"❌ Error copying file: {str(e)}")

def main():
    print("\n🤖 Starting CSV Data Generator...")
    
    # Get API key from user
    api_key = get_api_key()
    client = anthropic.Client(api_key=api_key)
    
    # Get user input
    file_path = input("\n📁 Please enter the path to your CSV file: ")
    num_rows_to_generate = int(input("🔢 How many new rows would you like to generate? "))
    
    # Analyze the data
    analysis = analyze_data(client, file_path)
    if not analysis:
        print("❌ Analysis failed. Exiting...")
        return
    
    # Get and print summary
    summary = get_summary(client, analysis)
    print("\n📊 Analysis Summary:")
    print(summary)
    
    # Generate new data
    new_rows = generate_data(client, file_path, num_rows_to_generate, analysis)
    
    # Save the generated data
    if new_rows:
        append_to_csv(file_path, new_rows)
        print("\n👀 Preview of generated data (first 3 rows):")
        for row in new_rows[:3]:
            print(row)
        
        # Automatically copy the file to local machine
        copy_file_from_container(file_path)
        
    print("\n✨ Process completed successfully!")

if __name__ == "__main__":
    main()