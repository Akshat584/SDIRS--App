from typing import List, Optional
from pydantic import BaseModel
from app.models.earthquake import EarthquakeFeature
from app.models.weather_alert import WeatherAlert
from app.models.social_media import Tweet

class VerificationResult(BaseModel):
    event_type: str
    confidence: float
    details: str

async def cross_check_data(
    earthquakes: Optional[List[EarthquakeFeature]] = None,
    weather_alerts: Optional[List[WeatherAlert]] = None,
    tweets: Optional[List[Tweet]] = None
) -> List[VerificationResult]:
    """
    Performs cross-checking logic on various data sources to verify potential disaster events.
    Returns a list of VerificationResult objects.
    """
    verification_results = []

    # Rule 1: High magnitude earthquake + related tweets
    if earthquakes:
        for eq in earthquakes:
            if eq.properties.mag >= 4.0: # Example threshold for significant earthquake
                related_tweets_count = 0
                if tweets:
                    for tweet in tweets:
                        if (eq.properties.place.lower() in tweet.content.lower() or 
                           eq.properties.title.lower() in tweet.content.lower()):
                            related_tweets_count += 1
                
                if related_tweets_count > 5: # Example threshold for related tweets
                    verification_results.append(
                        VerificationResult(
                            event_type="Earthquake",
                            confidence=0.9,
                            details=f"High magnitude earthquake ({eq.properties.mag}) in {eq.properties.place} confirmed by {related_tweets_count} related tweets."
                        )
                    )
                elif related_tweets_count > 0:
                    verification_results.append(
                        VerificationResult(
                            event_type="Earthquake",
                            confidence=0.7,
                            details=f"High magnitude earthquake ({eq.properties.mag}) in {eq.properties.place} with some social media mentions."
                        )
                    )
                else:
                    verification_results.append(
                        VerificationResult(
                            event_type="Earthquake",
                            confidence=0.6,
                            details=f"High magnitude earthquake ({eq.properties.mag}) in {eq.properties.place} detected by USGS."
                        )
                    )

    # Rule 2: Flood warning + related tweets
    if weather_alerts:
        for alert in weather_alerts:
            if "flood" in alert.event.lower() and "warning" in alert.event.lower():
                related_tweets_count = 0
                if tweets:
                    for tweet in tweets:
                        if (alert.event.lower() in tweet.content.lower() or 
                           alert.description.lower() in tweet.content.lower()):
                            related_tweets_count += 1
                
                if related_tweets_count > 5: # Example threshold for related tweets
                    verification_results.append(
                        VerificationResult(
                            event_type="Flood",
                            confidence=0.85,
                            details=f"Flood Warning ({alert.event}) confirmed by {related_tweets_count} related tweets."
                        )
                    )
                elif related_tweets_count > 0:
                    verification_results.append(
                        VerificationResult(
                            event_type="Flood",
                            confidence=0.7,
                            details=f"Flood Warning ({alert.event}) with some social media mentions."
                        )
                    )
                else:
                    verification_results.append(
                        VerificationResult(
                            event_type="Flood",
                            confidence=0.6,
                            details=f"Flood Warning ({alert.event}) detected by OpenWeatherMap."
                        )
                    )

    # Further rules can be added here
    return verification_results
