from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

openai.api_key = OPENAI_API_KEY

app = FastAPI()

# Request model
class ProjectRequest(BaseModel):
    languages: list
    difficulty: str

@app.post("/generate-project")
async def generate_project(request: ProjectRequest):
    prompt = f"Suggest a {request.difficulty} project idea using {', '.join(request.languages)}."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  
            messages=[{
                "role": "system", "content": "You are a helpful assistant that generates project ideas."
            },
            {
                "role": "user", "content": prompt
            }]
        )
        return {"idea": response['choices'][0]['message']['content']}

    except openai.OpenAIError as e:
        return {"error": f"Error generating project idea: {str(e)}"}
