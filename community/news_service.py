# news_service.py - Create this file in your project

import requests
from django.conf import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def fetch_fitness_news(count=6):
    """
    Fetch fitness and health related news articles
    
    Args:
        count: Number of articles to fetch (default: 6)
    
    Returns:
        list: List of news articles or fallback to mock data if API fails
    """
    api_key = settings.NEWS_API_KEY
    
    # Define the news API endpoint
    url = 'https://newsapi.org/v2/everything'
    
    # Define parameters for the request
    params = {
        'q': 'fitness OR health OR workout OR nutrition',
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': count,
        'apiKey': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        data = response.json()
        articles = data.get('articles', [])
        
        # Process and format the articles
        formatted_articles = []
        for article in articles:
            formatted_article = {
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'image_url': article.get('urlToImage', ''),
                'published_at': article.get('publishedAt', ''),
                'source': article.get('source', {}).get('name', ''),
                'description': article.get('description', '')[:120] + '...' if article.get('description') else ''
            }
            formatted_articles.append(formatted_article)
        
        if not formatted_articles:  # If API returned no articles, use mock data
            return _get_mock_news(count)
            
        return formatted_articles
        
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        # Return mock data if API fails
        return _get_mock_news(count)

def _get_mock_news(count=4):
    """
    Generate mock news data when API fails
    """
    today = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    mock_news = [
        {
            'title': 'The Benefits of High-Intensity Interval Training for Weight Loss',
            'url': 'https://www.healthline.com/nutrition/benefits-of-hiit',
            'image_url': 'https://i0.wp.com/images-prod.healthline.com/hlcmsresource/images/topic_centers/Fitness-Exercise/400x400_Benefits_of_Working_Out_in_the_Morning.jpg?w=1155&h=1528',
            'published_at': today,
            'source': 'Healthline',
            'category': 'Workout',
            'description': 'HIIT workouts can burn more calories in less time and continue to burn calories post-workout. Learn how to incorporate them into your fitness routine.'
        },
        {
            'title': 'Nutrition Strategies to Support Muscle Recovery After Exercise',
            'url': 'https://www.verywellfit.com/nutrition-for-muscle-recovery-5114133',
            'image_url': 'https://www.verywellfit.com/thmb/7NxeaKZP-l2h_dCnL95fSVnwOcQ=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/GettyImages-1073271468-5c3d8a9446e0fb000112d72d.jpg',
            'published_at': today,
            'source': 'Very Well Fit',
            'category': 'Nutrition',
            'description': 'What you eat after a workout can significantly impact your recovery. Learn which nutrients and foods promote optimal muscle repair.'
        },
        {
            'title': 'How Sleep Quality Affects Your Athletic Performance',
            'url': 'https://www.sleepfoundation.org/physical-activity/athletic-performance-and-sleep',
            'image_url': 'https://www.sleepfoundation.org/wp-content/uploads/2018/10/SleepAthletics.jpg?x21653',
            'published_at': today,
            'source': 'Sleep Foundation',
            'category': 'Recovery',
            'description': 'Research shows that quality sleep improves reaction time, accuracy, and endurance. Learn how to optimize your sleep for better athletic performance.'
        },
        {
            'title': 'The Connection Between Gut Health and Fitness Performance',
            'url': 'https://www.runnersworld.com/health-injuries/a36432850/gut-health-for-runners/',
            'image_url': 'https://hips.hearstapps.com/hmg-prod/images/gut-health-for-runners-royalty-free-image-1620845196.jpg?crop=0.668xw:1.00xh;0.168xw,0&resize=980:*',
            'published_at': today,
            'source': 'Runner\'s World',
            'category': 'Health',
            'description': 'Your gut microbiome affects more than just digestion. Learn how gut health impacts athletic performance and recovery.'
        },
        {
            'title': 'Plant-Based Protein Sources for Vegetarian Athletes',
            'url': 'https://www.medicalnewstoday.com/articles/321474',
            'image_url': 'https://cdn-prod.medicalnewstoday.com/content/images/articles/321/321474/legumes-including-black-beans-chickpeas-red-kidney-beans-and-lentils.jpg',
            'published_at': today,
            'source': 'Medical News Today',
            'category': 'Nutrition',
            'description': 'Discover how vegetarian and vegan athletes can meet their protein needs with plant-based foods. These sources provide all essential amino acids.'
        },
        {
            'title': 'How to Prevent Common Running Injuries',
            'url': 'https://www.mayoclinic.org/healthy-lifestyle/fitness/in-depth/running/art-20046001',
            'image_url': 'https://www.mayoclinic.org/-/media/kcms/gbs/patient-consumer/images/2013/08/26/10/51/ds00439_im03153_sn7_runningthu_jpg.jpg',
            'published_at': today,
            'source': 'Mayo Clinic',
            'category': 'Health',
            'description': 'Proper form, appropriate footwear, and smart training can help prevent common running injuries. Learn expert tips for staying injury-free.'
        }
    ]
    
    # Return only the requested number of items
    return mock_news[:count]