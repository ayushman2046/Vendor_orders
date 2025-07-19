from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi import Depends
import os
from app.dependencies.db_session import get_db
from app.dependencies.token_auth import verify_token
from app.langchain.invoke_langchain import create_prompt_template, invoke_langchain

query_router = APIRouter()
api_key = os.getenv('OPENAI_API_KEY')

class QueryRequest(BaseModel):
    question: str

@query_router.post("/query")
def query_with_custom_prompt(request: QueryRequest, db: Session = Depends(get_db), auth=Depends(verify_token)):
    try:
        # System & user prompt
        system_prompt = """
                    You are a PostgreSQL expert. Convert the following natural language question into a valid SQL query.

                    You are working with this table:
                    Table: order_events
                    Columns:
                    - id (UUID)
                    - vendor_id (TEXT)
                    - items (JSONB)
                    - total_amount (FLOAT)
                    - timestamp (TIMESTAMP)

                    Rules:
                    - Only write SELECT queries.
                    - The SQL should be syntactically correct and end with a semicolon.
                    - DO NOT write explanations. Only return SQL.
                """

        human_template = "please generate a sql query without any extra stuff User question: {user_question}"

        # Step 1: Create the prompt template
        prompt_template = create_prompt_template(
            template_string=human_template,
            sys_prompt=system_prompt,
        )

        # Step 2: Prepare input variables
        input_vars = {
            "user_question": request.question,
            "llm": "openai",
            "llm_model": "gpt-3.5-turbo",  # or "gpt-4o-mini"
            "temperature": 0,
        }

        # Step 3: Get response from LLM
        response = invoke_langchain(prompt_template, input_vars)
        if not response:
            raise HTTPException(status_code=400, detail="Prompt validation failed.")
        
        query = response.content.strip()
        print("Final SQL:", query)

        # Optional: block unsafe SQL
        if not query.lower().strip().startswith("select"):
            raise HTTPException(status_code=400, detail="Only SELECT queries are allowed.")

        # Step 4: Run the query
        result = db.execute(text(query)).fetchall()
        
        rows = [dict(row._mapping) for row in result]
        for row in rows:
            for k, v in row.items():
                if v is None:
                    row[k] = 0

        return {"query": query, "result": rows}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))