import csv, requests

access_token = 'seu_access_token'

def run_query(query):
    url = 'https://api.github.com/graphql'
    headers = {'Authorization': f'Bearer {access_token}'}

    response = requests.post(url, json={'query': query}, headers=headers)

    if response.status_code != 200:
        raise RuntimeError(
            f"Falha na execução da query GraphQL.\n"
            f"Status HTTP: {response.status_code}\n"
            f"Resposta: {response.text}\n"
            f"Query: {query}"
        )
    
    data = response.json()
    if 'errors' in data:
        raise RuntimeError(
            f"Erros retornados pela API GraphQL:\n"
            f"{data['errors']}\n"
            f"Query: {query}"
        )
    
    return data

def query_composer(cursor=None):
    cursor_part = f', after: "{cursor}"' if cursor else ""
    query = f"""
               query {{
                  search(query: "chat.openai.com/share is:pr is:merged in:title,body",
                    type: ISSUE,
                    first: 100{cursor_part}) {{
                        pageInfo {{
                            endCursor
                            hasNextPage
                        }}
                        issueCount
                        edges {{
                            node {{
                                ... on PullRequest {{
                                    url
                                    title
                                    createdAt
                                    mergedAt
                                    repository {{
                                        stargazerCount
                                        isFork
                                        primaryLanguage {{
                                            name
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
                """
    return query

def write_samples(prs):
    filename = 'Candidate samples.csv'

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['PR URL', 'PR Title', 'PR createdAt', 'PR mergedAt', 'stars', 'fork', 'language'])
        writer.writerows(prs)      

def get_samples(): 
    cursor = None
    has_next_page = True    
    prs = []
                          
    while has_next_page:

        result = run_query(query_composer(cursor))
        end_cursor = result["data"]["search"]["pageInfo"]["endCursor"]
        has_next_page = result["data"]["search"]["pageInfo"]["hasNextPage"]

        issue_count = result["data"]["search"]["issueCount"]
    
        print(f"Occurrences: {issue_count}")

        for pr in result["data"]["search"]["edges"]:   
            pr_url = pr["node"]["url"]
            pr_title = pr["node"]["title"]
            pr_created_at = pr["node"]["createdAt"]
            pr_merged_at = pr["node"]["mergedAt"]
            stars = pr["node"]["repository"]["stargazerCount"]
            fork = pr["node"]["repository"]["isFork"]
            language = ""
            if pr["node"]["repository"]["primaryLanguage"] != None:
                language = pr["node"]["repository"]["primaryLanguage"]["name"]

            prs.append((pr_url, pr_title, pr_created_at, pr_merged_at, stars, fork, language))                            

        cursor = end_cursor
    return prs

prs = get_samples()
write_samples(prs)



                