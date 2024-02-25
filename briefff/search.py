
from html.parser import HTMLParser
from metaphor_python import Metaphor
from datetime import datetime, timedelta
from gcloud_helper import *
import io
from llm_functions import gpt3GenerateText, mixtralGenerateText

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = io.StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def search(query, user_id = None):
    client = Metaphor(api_key="e4e2b91e-385a-4425-9204-321372d76b7e")
    start_published_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    context = []
    url_list = []
    articles_per_topic = 8
    # yesterdays_urls = set(get_yesterdays_urls(user_id))

    search_results = client.search(
        query,
        num_results=8,
        use_autoprompt=True,
        # TODO: research if we actually need this and what it does
        start_published_date=start_published_date,
    )
    # one search and one get contents
    metaphor_content = search_results.get_contents()
    repeated_urls = []
    usefulSources = 0
    if user_id:
        yesterdays_urls = set(get_yesterdays_urls(user_id))
    else:
        yesterdays_urls =None

    i = 0
    for i in range(articles_per_topic):
        # for result in search_results.results:
        if i < len(metaphor_content.contents):
            #print("in bounds")
            result = metaphor_content.contents[i]
            url = result.url
            if yesterdays_urls and url in yesterdays_urls:
                print(f"Skipping {url} since it was used for {user_id}")
                continue

            metaphor_extract = metaphor_content.contents[i].extract
            metaphor_extract = strip_tags(metaphor_extract)
            ctx = f"SOURCE {result.title}" +"INFORMATION: " + metaphor_extract
            # print(f"Evaluating research for {user_id} for topic {query} with information {ctx}")

            if validate_source(query, ctx):
                url_list.append(url)
                if metaphor_extract:
                    context.append(f"SOURCE {result.title}" +"INFORMATION: " + metaphor_extract)
                usefulSources+=1
                if usefulSources>=5:
                    break
        else:
            break
        i+=1
    if usefulSources >= 5:
        print(f"Searched for {query} and got >= 5 useful Sources out of {articles_per_topic} Sources")
    else:
        print(f"Searched for {query} and got {usefulSources} useful Sources out of {articles_per_topic} Sources")
    return [url_list, context]

def validate_source(query, context):
    isValid = mixtralGenerateText(f"""
Evaluate the following article to determine its relevance for a podcast segment on the topic: '{query}'. Consider the article's alignment with the topic, the recency and depth of the information provided, and its focus on factual content over opinion. Based on these criteria:

- Is the article directly related to the topic '{query}'?
- Does the article provide detailed, factual information that is current and informative for listeners?
- Is the content of a depth that supports a meaningful discussion on the podcast?
- Is the content considered news or is it simply an information piece?
Answer with 'YES' if the article meets these criteria and is deemed relevant for inclusion in the podcast. Answer with 'NO' if it does not meet these criteria. Provide a single-word response without any explanation. Here is the Source: {context}
""", 10000).strip()
    
    if isValid[:2].lower() == "no":
        print("BAD SOURCE")
        return False
    elif isValid[:3].lower() == "yes":
        print("GOOD SOURCE")
        return True
    else:
        print(isValid)
        print("BAD VALIDATE OUTPUT")
        return True
def create_queries(topic):
    prompt = f"""Provide three brief queries that I can give to a neural search engine about {topic} in a numbered list format without any additional labels or formatting. Keep the queries very general, relevant, and short. DO NOT INCLUDE ANYTHING DATE SPECIFIC"""
    output = gpt3GenerateText(prompt)
    # print(output)
    try:
        out_list = extract_questions(output)
        # print(out_list)
        add_pref_queries(topic, out_list)
    # print(type(out_list))
    except:
        print(f"get_queries didnt work for {topic}")

#search("US Politics")