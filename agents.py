from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from google import genai
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from Tools import webSearch, scrape
import os,requests, re
from dotenv import load_dotenv
load_dotenv()

MAX_REVISIONS = 2

# client = genai.Client()
# llm = client.interactions(
#     model="gemini-3.7-flash"
# )

# llm = ChatGoogleGenerativeAI(model="gemini-3.7-flash")
# print(llm.invoke("Hello").content)
llm = ChatMistralAI(model = "mistral-small-2506",temperature=0)


# Search agent
def searchAgent():
    return create_agent(
        model = llm,
        tools = [webSearch]
    )

#reader agent
def readerAgent():
    return create_agent(
        model = llm,
        tools = [scrape]
    )


# writer chain
writer_prompt= ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    
    ("human", """Write a detailed research report on the topic below.

    Topic: {topic}

    Research Gathered:
    {research}

    Structure the report as:
    - Introduction
    - Key Findings (minimum 3 well-explained points)
    - Conclusion
    - Sources (list all URLs found in the research."""),

])

writerChain = writer_prompt | llm | StrOutputParser()

# Critic Chain 
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

        Report:
        {report}

        Respond in this exact format:

        Score: X/10

        Strengths:
        - ...
        - ...

        Areas to Improve:
        - ...
        - ...

        One line verdict:
        ..."""),
])

criticChain = critic_prompt | llm | StrOutputParser()

# Revision chain - writer revises based on critic feedback
revision_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer revising a report based on critic feedback."),
 
    ("human", """Revise the report below based on the critic's feedback.
 
    Original Report:
    {report}
 
    Critic Feedback:
    {feedback}
 
    Produce an improved, complete revised report following the same structure:
    - Introduction
    - Key Findings (minimum 3 well-explained points)
    - Conclusion
    - Sources (list all URLs found in the research)."""),
])
 
revisionChain = revision_prompt | llm | StrOutputParser()
 
 
def extract_score(feedback: str) -> int:
    """Pull the numeric score out of the critic's 'Score: X/10' line."""
    match = re.search(r"score[:\-]?\s*\*{0,2}\s*(\d+)\s*(?:/\s*10)?", feedback, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 0
 

 #critic revision
 
def revise_until_good(report: str) -> dict:
    """Critic -> Writer revision loop with a max revision cap."""
    state = {}
 
    
 
    state['report'] = report
    state['feedback'] = criticChain.invoke({"report": state['report']})
    state['score'] = extract_score(state['feedback'])
 
    
 
    revisions = 0
 
    while state['score'] < 8 and revisions < MAX_REVISIONS:
        revisions += 1
 
        print("\n" + "=" * 20)
        print(f"Step 5 - Revision Attempt {revisions} (score {state['score']}/10)")
        print("\n" + "=" * 20)
 
        state['report'] = revisionChain.invoke({
            "report": state['report'],
            "feedback": state['feedback']
        })
 
        print("\n Revised report\n", state['report'])
 
        state['feedback'] = criticChain.invoke({"report": state['report']})
        state['score'] = extract_score(state['feedback'])
 
        print("\n Critic feedback\n", state['feedback'])
        print("\n Parsed score:", state['score'])
 
    return {
        "final_report": state['report'],
        "final_score": state['score'],
        "final_feedback": state['feedback'],
        "revisions_performed": revisions
    }