from django.shortcuts import render
from .news_service import fetch_fitness_news, _get_mock_news

def community_hub(request):
    """
    View for the community hub page
    """
    # Use mock data directly to ensure we have content
    trending_news = _get_mock_news(count=4)
    print(f"Trending news count: {len(trending_news)}")
    
    # Context data for the template
    context = {
        'featured_discussions': [
            {
                'title': 'HIIT/LISS workout: expectations vs reality',
                'description': 'Let\'s talk about what really happens during intense workouts...',
                'comments': 123,
                'likes': 45,
                'views': 1200,
                'tag': 'Featured'
            },
            {
                'title': 'Nutrition tips for muscle gain',
                'description': 'Share your best nutrition strategies for gaining lean muscle...',
                'comments': 87,
                'likes': 32,
                'views': 956,
                'tag': 'Popular'
            },
            {
                'title': 'Overcoming fitness plateaus',
                'description': 'How to break through when you feel stuck in your progress...',
                'comments': 65,
                'likes': 28,
                'views': 742,
                'tag': None
            },
            {
                'title': 'Recovery: 10 things I wish I knew',
                'description': 'Important recovery techniques that changed my fitness journey...',
                'comments': 92,
                'likes': 51,
                'views': 1500,
                'tag': 'Trending'
            }
        ],
        'trending_topics': trending_news,  # Use mock news data
        'community_members': [
            {
                'name': 'Sarah J.',
                'level': 'Community Leader',
                'joined': '10 months ago',
                'posts': 78,
                'likes': 523
            },
            {
                'name': 'Michael D.',
                'level': 'Fitness Coach',
                'joined': '1 year ago',
                'posts': 124,
                'likes': 892
            },
            {
                'name': 'Jessica L.',
                'level': 'Nutrition Expert',
                'joined': '8 months ago',
                'posts': 67,
                'likes': 412
            }
        ],
        'community_challenges': [
            {
                'name': '10,000 Steps Daily',
                'icon': 'fa-running',
                'progress': 75
            },
            {
                'name': 'Strength Training (3x/week)',
                'icon': 'fa-dumbbell',
                'progress': 60
            },
            {
                'name': '5 Fruits/Veggies Daily',
                'icon': 'fa-apple-alt',
                'progress': 85
            }
        ]
    }
    
    return render(request, 'community/cmain.html', context)

