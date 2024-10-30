from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage

class NoteState(BaseModel):
    messages: List[BaseMessage] = Field(default_factory=list)
    hypothesis: Optional[str] = None
    process: Optional[str] = None
    process_decision: Optional[str] = None
    visualization_state: Optional[str] = None
    searcher_state: Optional[str] = None
    code_state: Optional[str] = None
    report_section: Optional[str] = None
    quality_review: Optional[str] = None
    needs_revision: bool = False
    sender: Optional[str] = None

# 如果需要，可以在这里定义其他相关的类或函数
