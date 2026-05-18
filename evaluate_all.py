import csv
import asyncio
from sql_agent import run_agent  

async def run_benchmark():
    input_csv = "sql_questions.csv"
    output_csv = "evaluation_report.csv"
    
    evaluation_records = []
    
    # 1. Open and extract benchmark questions
    with open(input_csv, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        # Ensure our CSV column header matches "question" exactly
        questions = [row["question"] for row in reader if row.get("question")]
        
    print(f"Loaded {len(questions)} target benchmark questions. Beginning execution loop...")

    # 2. Iterate automatically through every question
    for idx, question in enumerate(questions, 1):
        print(f"\nProcessing System Query {idx}/{len(questions)}...")
        
        # Call the updated agent function directly passing the loop's question string
        res = await run_agent(question)
        evaluation_records.append(res)
        
        # Tiny rest window to allow connection pool / API stability
        await asyncio.sleep(0.2)

    # 3. Compile the structured metric report table
    with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
        fieldnames = ["question", "sql", "executed_successfully", "correct_result", "retry_needed", "final_status"]
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction='ignore')
        
        writer.writeheader()
        for record in evaluation_records:
            # Leave correct_result blank so we can do our manual benchmark accuracy check
            record["correct_result"] = "" 
            writer.writerow(record)
            
    print(f"\n[Done] Benchmark matrix exported cleanly to: {output_csv}")

if __name__ == "__main__":
    asyncio.run(run_benchmark())