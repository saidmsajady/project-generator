from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import json
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

openai.api_key = OPENAI_API_KEY

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://project-generator-site.web.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model for project generation
class ProjectRequest(BaseModel):
    languages: list
    difficulty: str
    project_type: str

# Function to extract project ideas from OpenAI response
def parse_openai_response(response_text: str):
    projects = []
    project_blocks = response_text.split("\n\n")  # Split into individual project descriptions

    for block in project_blocks:
        title_match = re.search(r"Title:\s*(.*)", block)
        short_desc_match = re.search(r"Short Description:\s*(.*)", block)
        long_desc_match = re.search(r"Long Description:\s*(.*)", block, re.DOTALL)
        tech_stack_match = re.search(r"Tech Stack:\s*(.*)", block)
        instructions_match = re.search(r"Implementation Instructions:\s*(.*)", block, re.DOTALL)

        if title_match and short_desc_match and long_desc_match and tech_stack_match and instructions_match:
            projects.append({
                "title": title_match.group(1).strip(),
                "short_description": short_desc_match.group(1).strip(),
                "long_description": long_desc_match.group(1).strip(),
                "tech_stack": [tech.strip() for tech in tech_stack_match.group(1).split(",")],
                "implementation_instructions": instructions_match.group(1).strip(),
            })

    return projects

# Endpoint to generate project ideas
@app.post("/generate-project")
async def generate_project(request: ProjectRequest):
    prompt = (
        f"Generate two {request.difficulty} {request.project_type} project ideas using {', '.join(request.languages)}. "
        "Include the following details in the JSON response:\n"
        "{\n"
        '  "project_ideas": [\n'
        '    { "title": "Project Title", "short_description": "A short summary", '
        '      "long_description": "A detailed description", "tech_stack": ["Tech1", "Tech2"], '
        '      "implementation_instructions": "Step-by-step implementation" },\n'
        '    { "title": "Project Title", "short_description": "A short summary", '
        '      "long_description": "A detailed description", "tech_stack": ["Tech1", "Tech2"], '
        '      "implementation_instructions": "Step-by-step implementation" }\n'
        '  ]\n'
        "}\n"
        "DO NOT include any explanations, only return valid JSON."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates detailed project ideas."},
                {"role": "user", "content": prompt}
            ]
        )

        openai_text = response['choices'][0]['message']['content']
        
        # Log the response to see what OpenAI actually returns
        print("OpenAI Response:", openai_text)

        # Convert OpenAI response directly to JSON
        project_ideas = json.loads(openai_text).get("project_ideas", [])

        return {"project_ideas": project_ideas}

    except (openai.OpenAIError, json.JSONDecodeError) as e:
        return {"error": f"Error generating project idea: {str(e)}"}
