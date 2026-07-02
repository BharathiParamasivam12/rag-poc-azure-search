import os
import json
from dotenv import load_dotenv
from google import genai
from queryIndex import hybrid_search

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))



def build_summary_prompt(query, results):
    reviews_text = "\n\n".join(
        f"[{r.get('name')} - {r.get('city')}, {r.get('province')} - Rating: {r.get('reviews_rating')}]\n"
        f"{r.get('reviews_title')}: {r.get('reviews_text')}"
        for r in results
    )

    prompt = f"""You are a helpful assistant that summarizes hotel guest reviews.

Below are review excerpts retrieved for the search query: "{query}"

Reviews:
{reviews_text}

Analyze the reviews and respond ONLY with valid JSON in this exact structure, no markdown formatting, no backticks, no extra text:

{{
  "overall_sentiment": "Positive | Negative | Mixed",
  "summary": "2-3 sentence overview",
  "common_themes": [
    {{"theme": "string", "description": "string"}}
  ],
  "standout_praise": "string or null",
  "standout_complaints": "string or null",
  "recommendation": "1 sentence recommendation and ideal traveler type"
}}

Rules:
- Only use information present in the reviews above. Do not invent details.
- If reviews conflict on a point, mention both sides within the relevant field.
- Include only themes that are clearly supported by at least 2 reviews."""

    return prompt


def summarize_results(query, results):
    prompt = build_summary_prompt(query, results)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    raw_text = response.text.strip()

    # Strip accidental markdown code fences if the model adds them anyway
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        print("Warning: model did not return valid JSON. Raw output:")
        print(raw_text)
        return None


if __name__ == "__main__":
    query = "clean rooms and friendly staff"
    results = hybrid_search(query)

    summary = summarize_results(query, results)
    if summary:
        print(json.dumps(summary, indent=2))