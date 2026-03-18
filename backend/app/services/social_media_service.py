from typing import List
from app.models.social_media import Tweet
from datetime import datetime
from app.services.nlp_service import nlp_service

def scrape_tweets(query: str, max_tweets: int) -> List[Tweet]:
    """
    SDIRS Social Media Intelligence Pipeline (Module 3)
    Simulates real-time API ingestion from X/Reddit + BERT NLP classification.
    """
    print(f"SDIRS AI: Processing real-time NLP stream for '{query}'...")
    
    raw_posts = [
        {
            "url": "https://twitter.com/user/status/1",
            "content": f"URGENT: Major {query} near the power station! People are trapped. SOS!",
            "username": "citizen_reporter"
        },
        {
            "url": "https://twitter.com/user/status/2",
            "content": f"Official Alert: Evacuation orders issued for the river district due to {query}.",
            "username": "emergency_ops"
        },
        {
            "url": "https://twitter.com/user/status/3",
            "content": f"Just saw some {query} on the news. Hope everyone is okay.",
            "username": "random_user"
        }
    ]

    tweets = []
    for post in raw_posts:
        # Perform BERT-based NLP Analysis
        nlp_result = nlp_service.analyze_text(post["content"])
        
        tweets.append(Tweet(
            url=post["url"],
            date=datetime.now(),
            content=post["content"],
            username=post["username"],
            sentiment=nlp_result["sentiment"],
            classification=nlp_result["classification"]
        ))
    
    return tweets
