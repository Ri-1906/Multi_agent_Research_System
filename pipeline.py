from agents import searchAgent, readerAgent, writerChain, criticChain, revise_until_good

def run(topic: str) -> dict:
    state ={}

    # search working
    print("\n"+"="*20)
    print("Step 1 - Search Agent")
    print("\n"+"="*20)

    search = searchAgent()
    searchResult = search.invoke({
        "messages" : [("user", f"Find recent, reliable and detailed information about : {topic}")]
    })

    state['search_result'] = searchResult['messages'][-1].content

    print("\n search result ",state['search_result'])


    # reader working
    print("\n"+"="*20)
    print("Step 2 - Reader Agent scraping resources...")
    print("\n"+"="*20)

    reader = readerAgent()
    readerResult = reader.invoke({
        "messages" : [("user",
            f"BAsed on following search results about '{topic}, "
            f"pick the most releveant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_result'][:800]}"
            )]
    })

    state['scraped_content'] = readerResult['messages'][-1].content

    print("\nScraped content\n", state["scraped_content"])


    # writer chain
    print("\n"+"="*20)
    print("Step 3 - Writer Agent")
    print("\n"+"="*20)

    combined_research =(
        f"Search RESULTS : \n {state['search_result']} \n\n"
        f"DETAILED SCRAPED CONTENT: \n{state['scraped_content']}\n\n"
    )

    state['report'] = writerChain.invoke({
        "topic" : topic,
        "research" : combined_research
    })

    print("\n Final Report\n", state['report'])


    #critic
    print("\n"+"="*20)
    print("Step 4 - Critic Agent")
    print("\n"+"="*20)

    state['feedback'] = criticChain.invoke({
        "report" : state['report']
    })


    print("\n Critic report\n", state['feedback'])

    # critic -> writer revision loop
    revision_result = revise_until_good(state['report'])
 
    state['report'] = revision_result['final_report']
    state['feedback'] = revision_result['final_feedback']
    state['score'] = revision_result['final_score']
    state['revisions_performed'] = revision_result['revisions_performed']
 
    print("\n" + "=" * 20)
    print("FINAL RESULT")
    print("\n" + "=" * 20)
    print("\n Final Report\n", state['report'])
    print("\n Final Score:", state['score'])
    print("\n Revisions Performed:", state['revisions_performed'])
 
   



if __name__ == "__main__":
    topic = input("Enter a research topic: ")
    run(topic)