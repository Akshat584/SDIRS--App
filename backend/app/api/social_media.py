from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.services import social_media_service
from app.models.social_media import Tweet

router = APIRouter()

@router.get("/tweets", response_model=List[Tweet])
def get_tweets(
    query: str = Query(..., description="The search query for tweets."),
    max_tweets: int = Query(10, description="The maximum number of tweets to return.")
):
    """
    Get the latest tweets from Twitter based on a search query.
    """
    tweets = social_media_service.scrape_tweets(query, max_tweets)
    if not tweets:
        raise HTTPException(status_code=404, detail="No tweets found for the given query.")
    return tweets
