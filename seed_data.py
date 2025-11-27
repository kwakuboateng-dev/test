"""
Seed data script for Odoyewu premium features.
Run this after creating the database and running migrations.
"""

from database import SessionLocal
from models import (
    Badge, Theme, IcebreakerPrompt, CompatibilityQuiz,
    Event, RelationshipTip
)
from datetime import datetime, timedelta
import json

def seed_badges():
    """Create achievement badges"""
    db = SessionLocal()
    
    badges = [
        {"name": "First Match", "description": "Made your first match", "xp_requirement": 0, "icon_url": "🎯"},
        {"name": "Conversationalist", "description": "Sent 50 messages", "xp_requirement": 100, "icon_url": "💬"},
        {"name": "Social Butterfly", "description": "Matched with 10 people", "xp_requirement": 200, "icon_url": "🦋"},
        {"name": "Heart Revealer", "description": "Revealed your identity", "xp_requirement": 150, "icon_url": "💝"},
        {"name": "Event Goer", "description": "Attended 5 events", "xp_requirement": 250, "icon_url": "🎉"},
        {"name": "Quiz Master", "description": "Completed all quizzes", "xp_requirement": 300, "icon_url": "🧠"},
        {"name": "Mood Tracker", "description": "30-day mood streak", "xp_requirement": 500, "icon_url": "😊"},
    ]
    
    for badge_data in badges:
        badge = Badge(**badge_data)
        db.add(badge)
    
    db.commit()
    db.close()
    print(f"✅ Created {len(badges)} badges")

def seed_themes():
    """Create UI themes"""
    db = SessionLocal()
    
    themes = [
        {"name": "Default", "description": "Classic Odoyewu theme", "css_url": "/themes/default.css", "price": 0.0, "premium": False},
        {"name": "Dark Mode", "description": "Easy on the eyes", "css_url": "/themes/dark.css", "price": 0.0, "premium": False},
        {"name": "Sunset Romance", "description": "Warm orange and pink gradients", "css_url": "/themes/sunset.css", "price": 2.99, "premium": True},
        {"name": "Ocean Breeze", "description": "Cool blue and teal tones", "css_url": "/themes/ocean.css", "price": 2.99, "premium": True},
        {"name": "Forest Zen", "description": "Calming green nature theme", "css_url": "/themes/forest.css", "price": 2.99, "premium": True},
        {"name": "Midnight Galaxy", "description": "Deep purple and starry night", "css_url": "/themes/galaxy.css", "price": 4.99, "premium": True},
    ]
    
    for theme_data in themes:
        theme = Theme(**theme_data)
        db.add(theme)
    
    db.commit()
    db.close()
    print(f"✅ Created {len(themes)} themes")

def seed_icebreakers():
    """Create icebreaker prompts"""
    db = SessionLocal()
    
    icebreakers = [
        # Casual
        {"text": "If you could have dinner with anyone, dead or alive, who would it be?", "category": "casual", "premium": False},
        {"text": "What's the best trip you've ever taken?", "category": "casual", "premium": False},
        {"text": "What's your go-to karaoke song?", "category": "casual", "premium": False},
        {"text": "Coffee or tea? And how do you take it?", "category": "casual", "premium": False},
        
        # Deep
        {"text": "What's a belief you held strongly but changed your mind about?", "category": "deep", "premium": False},
        {"text": "What does a perfect day look like for you?", "category": "deep", "premium": False},
        {"text": "What's something you're working on improving about yourself?", "category": "deep", "premium": True},
        {"text": "What's your biggest fear and why?", "category": "deep", "premium": True},
        
        # Fun
        {"text": "If you were a superhero, what would your power be?", "category": "fun", "premium": False},
        {"text": "What's the weirdest food combination you enjoy?", "category": "fun", "premium": False},
        {"text": "If you could live in any fictional world, which would it be?", "category": "fun", "premium": False},
        {"text": "What's your most embarrassing moment?", "category": "fun", "premium": True},
        
        # Romantic
        {"text": "What's your love language?", "category": "romantic", "premium": False},
        {"text": "What does your ideal date night look like?", "category": "romantic", "premium": False},
        {"text": "What's the most romantic thing someone has done for you?", "category": "romantic", "premium": True},
        {"text": "How do you know when you're falling in love?", "category": "romantic", "premium": True},
    ]
    
    for icebreaker_data in icebreakers:
        icebreaker = IcebreakerPrompt(**icebreaker_data)
        db.add(icebreaker)
    
    db.commit()
    db.close()
    print(f"✅ Created {len(icebreakers)} icebreaker prompts")

def seed_quizzes():
    """Create compatibility quizzes"""
    db = SessionLocal()
    
    quizzes = [
        {
            "title": "Love Language Quiz",
            "description": "Discover how you give and receive love",
            "premium": False,
            "questions": json.dumps([
                {
                    "text": "How do you prefer to show affection?",
                    "options": ["Physical touch", "Words of affirmation", "Acts of service", "Quality time", "Gifts"]
                },
                {
                    "text": "What makes you feel most loved?",
                    "options": ["Hugs and kisses", "Compliments", "Help with tasks", "Undivided attention", "Thoughtful presents"]
                },
                {
                    "text": "In a relationship, what's most important?",
                    "options": ["Physical intimacy", "Communication", "Support", "Shared experiences", "Generosity"]
                }
            ])
        },
        {
            "title": "Attachment Style Assessment",
            "description": "Understand your relationship patterns",
            "premium": True,
            "questions": json.dumps([
                {
                    "text": "How do you feel about emotional closeness?",
                    "options": ["I crave it", "I'm comfortable with it", "I need space", "It makes me anxious"]
                },
                {
                    "text": "When conflict arises, you tend to:",
                    "options": ["Seek resolution immediately", "Need time to process", "Avoid it", "Get overwhelmed"]
                },
                {
                    "text": "How do you feel about independence in relationships?",
                    "options": ["We should do everything together", "Balance is key", "I need lots of alone time", "It depends on my mood"]
                }
            ])
        },
        {
            "title": "Relationship Values Quiz",
            "description": "What matters most to you in love?",
            "premium": False,
            "questions": json.dumps([
                {
                    "text": "What's your top priority in a partner?",
                    "options": ["Honesty", "Humor", "Ambition", "Kindness", "Intelligence"]
                },
                {
                    "text": "How important is shared interests?",
                    "options": ["Very important", "Somewhat important", "Not very important", "Doesn't matter"]
                },
                {
                    "text": "What's your ideal relationship pace?",
                    "options": ["Fast - I know what I want", "Moderate - let's see where it goes", "Slow - I need time", "No rush at all"]
                }
            ])
        }
    ]
    
    for quiz_data in quizzes:
        quiz = CompatibilityQuiz(**quiz_data)
        db.add(quiz)
    
    db.commit()
    db.close()
    print(f"✅ Created {len(quizzes)} compatibility quizzes")

def seed_events():
    """Create virtual events"""
    db = SessionLocal()
    
    now = datetime.utcnow()
    
    events = [
        {
            "title": "Speed Dating Night",
            "description": "Meet 10 people in 10 minutes each! Fast-paced fun for making connections.",
            "start_time": now + timedelta(days=2, hours=19),
            "end_time": now + timedelta(days=2, hours=21),
            "premium": False,
            "max_participants": 20
        },
        {
            "title": "Relationship Workshop: Communication",
            "description": "Learn effective communication techniques with relationship expert Dr. Sarah Johnson.",
            "start_time": now + timedelta(days=5, hours=18),
            "end_time": now + timedelta(days=5, hours=20),
            "premium": True,
            "max_participants": 50
        },
        {
            "title": "Singles Mixer: Coffee & Conversation",
            "description": "Casual virtual coffee meetup for singles. Bring your favorite beverage!",
            "start_time": now + timedelta(days=7, hours=10),
            "end_time": now + timedelta(days=7, hours=11, minutes=30),
            "premium": False,
            "max_participants": 30
        },
        {
            "title": "Mindful Dating Meditation",
            "description": "Guided meditation session focused on opening your heart and attracting healthy love.",
            "start_time": now + timedelta(days=10, hours=20),
            "end_time": now + timedelta(days=10, hours=21),
            "premium": True,
            "max_participants": 100
        },
        {
            "title": "Game Night: Icebreaker Edition",
            "description": "Play fun games designed to help you get to know other singles!",
            "start_time": now + timedelta(days=14, hours=19),
            "end_time": now + timedelta(days=14, hours=21),
            "premium": False,
            "max_participants": 40
        }
    ]
    
    for event_data in events:
        event = Event(**event_data)
        db.add(event)
    
    db.commit()
    db.close()
    print(f"✅ Created {len(events)} events")

def seed_relationship_tips():
    """Create relationship tips"""
    db = SessionLocal()
    
    tips = [
        # Communication
        {
            "title": "Active Listening",
            "content": "When your partner speaks, put away distractions and truly listen. Reflect back what you heard to ensure understanding. This simple act shows you value their thoughts and feelings.",
            "category": "communication",
            "premium": False
        },
        {
            "title": "Use 'I' Statements",
            "content": "Instead of 'You always...', try 'I feel... when...'. This reduces defensiveness and opens dialogue. For example: 'I feel hurt when plans change last minute' vs 'You always cancel on me.'",
            "category": "communication",
            "premium": False
        },
        {
            "title": "The 5:1 Ratio",
            "content": "Research shows healthy relationships have 5 positive interactions for every 1 negative. Make deposits in your relationship bank through compliments, appreciation, and affection.",
            "category": "communication",
            "premium": True
        },
        
        # Trust
        {
            "title": "Consistency Builds Trust",
            "content": "Trust isn't built through grand gestures, but through consistent small actions. Follow through on promises, be reliable, and show up when you say you will.",
            "category": "trust",
            "premium": False
        },
        {
            "title": "Vulnerability Creates Connection",
            "content": "Sharing your fears, dreams, and insecurities (appropriately) deepens intimacy. Start small and build as trust grows. Vulnerability is strength, not weakness.",
            "category": "trust",
            "premium": False
        },
        {
            "title": "Repair After Conflict",
            "content": "How you handle conflict matters more than avoiding it. Apologize sincerely, take responsibility, and discuss how to prevent similar issues. This builds trust over time.",
            "category": "trust",
            "premium": True
        },
        
        # Intimacy
        {
            "title": "Emotional Intimacy First",
            "content": "Physical intimacy deepens when emotional connection is strong. Share your day, your thoughts, your feelings. Create space for your partner to do the same.",
            "category": "intimacy",
            "premium": False
        },
        {
            "title": "Quality Over Quantity",
            "content": "It's not about how much time you spend together, but how present you are. 20 minutes of undivided attention beats 2 hours of distracted coexistence.",
            "category": "intimacy",
            "premium": False
        },
        {
            "title": "Keep Dating Each Other",
            "content": "Don't stop courting just because you're together. Plan dates, try new experiences, surprise each other. Novelty and effort keep the spark alive.",
            "category": "intimacy",
            "premium": True
        },
        
        # Conflict
        {
            "title": "Take a Timeout",
            "content": "When emotions run high, it's okay to pause. Say 'I need 20 minutes to cool down' and return when calm. Never make it a punishment—always come back to resolve.",
            "category": "conflict",
            "premium": False
        },
        {
            "title": "Fight Fair",
            "content": "No name-calling, no bringing up past issues, no threats. Stick to the current issue, use respectful language, and remember you're on the same team.",
            "category": "conflict",
            "premium": False
        },
        {
            "title": "Understand vs. Win",
            "content": "The goal isn't to win the argument, but to understand each other. Ask 'Help me understand your perspective' instead of proving you're right. Compromise when possible.",
            "category": "conflict",
            "premium": True
        }
    ]
    
    for tip_data in tips:
        tip = RelationshipTip(**tip_data)
        db.add(tip)
    
    db.commit()
    db.close()
    print(f"✅ Created {len(tips)} relationship tips")

def seed_all():
    """Run all seed functions"""
    print("🌱 Starting database seeding...\n")
    
    try:
        seed_badges()
        seed_themes()
        seed_icebreakers()
        seed_quizzes()
        seed_events()
        seed_relationship_tips()
        
        print("\n✅ Database seeding complete!")
        print("\n📊 Summary:")
        print("  - 7 Badges")
        print("  - 6 Themes (2 free, 4 premium)")
        print("  - 16 Icebreaker Prompts")
        print("  - 3 Compatibility Quizzes")
        print("  - 5 Virtual Events")
        print("  - 12 Relationship Tips")
        print("\n🎉 Your app is ready to test!")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        raise

if __name__ == "__main__":
    seed_all()
