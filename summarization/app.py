from fastapi import FastAPI
from pydantic import BaseModel
from summarizer import summarize_text  # import the summarization function

app = FastAPI(title="Learning Content Summarizer API", version="1.0")

# Request model
class SummarizationRequest(BaseModel):
    page_content: str
    title: str
    max_length: int = 150
    min_length: int = 50

@app.post("/summarize/")
def summarize_endpoint(request: SummarizationRequest):
    """
    Summarize technical content from a learning resource.
    """
    result = summarize_text(
        page_content=request.page_content,
        title=request.title,
        max_length=request.max_length,
        min_length=request.min_length
    )
    return {"summary": result}
