
from llm.rag_query import (
    rag_query
)

def main():
    queries = [
        "what is the entertainment budget plans for employee",
        "are interns allowed for wifi reimbursment"
    ]

    for q in queries:
        rag_query(q, verbose=True)
        print()
   

if __name__ =="__main__":
    main()
