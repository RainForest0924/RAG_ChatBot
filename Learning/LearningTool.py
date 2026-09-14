from langchain_core.tools import tool

@tool("calculator")
def calculator(expression: str) -> str:
    """Calculate a mathematical expression."""
    return f"計算結果是:{eval(expression)}"

@tool("Wikipedia")
def search_wikipedia(query: str) -> str:
    """Search Wikipedia for a query."""
    return f"在維基百科搜尋結果是: {query} 的相關資訊"