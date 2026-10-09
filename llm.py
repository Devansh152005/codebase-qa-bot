import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def build_prompt(question: str, chunks: list[dict]) -> str:
    """
    Builds the prompt by injecting retrieved chunks as context.
    This is the core of RAG — augmenting the question with real context.
    """
    context_parts = []

    for i, chunk in enumerate(chunks):
        context_parts.append(
            f"--- Code Chunk {i+1} ---\n"
            f"File: {chunk['file_path']}\n"
            f"Code:\n{chunk['content']}\n"
        )

    context = "\n".join(context_parts)

    prompt = f"""You are an expert code assistant. 
A developer is asking a question about a codebase.
Use ONLY the code chunks provided below to answer.
If the answer is not in the chunks, say "I could not find that in the provided context."

--- CODE CONTEXT ---
{context}
--- END CONTEXT ---

Developer's Question: {question}

Answer clearly and concisely, referencing specific file names where relevant:"""

    return prompt


def generate_answer(question: str, chunks: list[dict]) -> str:
    """
    Takes a question and retrieved chunks,
    builds a prompt, sends to LLM, returns the answer.
    """
    if not chunks:
        return "No relevant code chunks found for your question."

    prompt = build_prompt(question, chunks)

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,  # low temp = more factual, less creative
        max_tokens=500
    )

    return response.choices[0].message.content