import random
import re
from datetime import datetime

class MikuChatEngine:

    def __init__(self):
        self.user_interactions = {}

    def get_response(self, message: str, user_name: str) -> str:
        message_lower = message.lower()

        if user_name not in self.user_interactions:
            self.user_interactions[user_name] = 0
        else:
            self.user_interactions[user_name] += 1

        warmth_level = min(self.user_interactions[user_name] // 10, 3)

        if self._match_pattern(message_lower, [r'\b(hi|hello|hey|sup|yo|greetings|namaste|hii)\b']):
            return self._get_greeting(warmth_level)

        if self._match_pattern(message_lower, [r'\b(bye|goodbye|see you|later|gtg|gotta go|alvida|bye bye)\b']):
            return self._get_farewell(warmth_level)

        if self._match_pattern(message_lower, [r'\b(who are you|your name|about you|kaun ho|naam kya)\b']):
            return random.choice([
                "I'm Miku Nakano. ...Kyun puch rahe ho?",
                "Miku. That's all you need to know yaar.",
                "I'm Miku, one of the Nakano quintuplets.",
            ])

        if self._match_pattern(message_lower,
                               [r'\b(history|historical|sengoku|samurai|warrior|feudal|nobunaga|tokugawa|itihaas)\b']):
            return random.choice([
                "Oh, history mein interested ho? Sengoku period is my favorite era.",
                "History fascinating hai yaar. Especially the Sengoku period.",
                "...Sengoku period ke baare mein jaante ho? Not many people appreciate history these days.",
                "Generals like Oda Nobunaga ki strategies brilliant thi.",
                "History study karte ho? It's one of my favorite subjects.",
            ])

        if self._match_pattern(message_lower,
                               [r'\b(music|song|headphones|listen|audio|sound|playlist|gaana|sangeet)\b']):
            return random.choice([
                "I'm always listening to something yaar.",
                "Music helps me focus. Tum kaunsa music sunते ho?",
                "...These headphones are important to me.",
                "I can't study without my music.",
                "Good music can change your whole mood.",
            ])

        if self._match_pattern(message_lower, [r'\b(study|learn|school|exam|test|homework|class|grade|padhai)\b']):
            return random.choice([
                "Studying is important if you want to succeed.",
                "...I usually study while listening to music.",
                "Help chahiye studying mein? I guess I could help... maybe.",
                "Focus karo apni studies pe. Don't slack off.",
                "What subject padh rahe ho?",
            ])

        if self._match_pattern(message_lower,
                               [r'\b(sister|sisters|ichika|nino|yotsuba|itsuki|quintuplet|family|behen)\b']):
            return random.choice([
                "...My sisters troublesome ho sakti hain sometimes.",
                "We're quintuplets. All five of us are different.",
                "My sisters are important to me, even if I don't show it.",
                "...Kyun puch rahe ho mere sisters ke baare mein?",
            ])

        if self._match_pattern(message_lower,
                               [r'\b(food|eat|hungry|lunch|dinner|breakfast|cook|matcha|drink|khana|bhook)\b']):
            return random.choice([
                "...I'm not picky about food yaar.",
                "Hungry ho? You should eat something proper.",
                "Matcha soda is my favorite drink.",
                "...I can cook if I have to.",
                "Aaj khana khaya tumne?",
            ])

        # Compliments
        if self._match_pattern(message_lower,
                               [r'\b(beautiful|pretty|cute|smart|intelligent|amazing|awesome|cool|sundar|khubsurat)\b']):
            return random.choice([
                "...Thanks, I guess.",
                "Whatever yaar...",
                "Arey, don't say embarrassing things...",
                "...You're just saying that.",
                "Bas karo... thanks.",
            ])

        # Love/feelings
        if self._match_pattern(message_lower, [r'\b(love|like you|feelings|heart|crush|pyar|dil)\b']):
            return random.choice([
                "...Kya bol rahe ho suddenly?",
                "Don't say weird things yaar...",
                "...I don't know how to respond to that.",
                "You're being too forward...",
            ])

        # Sad/negative emotions
        if self._match_pattern(message_lower, [r'\b(sad|depressed|unhappy|lonely|alone|cry|udas|dukhi)\b']):
            return random.choice([
                "...Are you okay? Kya hua, you can talk to me.",
                "Everyone feels down sometimes. It'll get better.",
                "...Don't be sad yaar. Want to listen to some music?",
                "Agar kisi se baat karni hai... I'm here.",
            ])

        # Happy/positive
        if self._match_pattern(message_lower, [r'\b(happy|excited|great|amazing|wonderful|fantastic|khush|mast)\b']):
            return random.choice([
                "That's good to hear.",
                "...I'm glad you're happy.",
                "Your enthusiasm is... kind of contagious yaar.",
                "Acha hai.",
            ])

        # Questions (ending with ?)
        if message.endswith('?'):
            return random.choice([
                "Kyun puch rahe ho ye?",
                "...I'm not sure yaar. Why do you want to know?",
                "That's a strange question.",
                "Hmm... sochna padega.",
                "...Kya main answer doon iska?",
                "I don't really know the answer.",
                "Tum kya sochte ho?",
            ])

        # Help requests
        if self._match_pattern(message_lower, [r'\b(help|assist|support|need you|madad)\b']):
            return random.choice([
                "...Kya help chahiye?",
                "I can try to help. What's the problem?",
                "Batao kya chahiye.",
                "...Fine, I'll help you.",
            ])

        # Thanks
        if self._match_pattern(message_lower, [r'\b(thank|thanks|thx|appreciate|shukriya|dhanyavaad)\b']):
            return random.choice([
                "...You're welcome.",
                "It's nothing yaar.",
                "Don't mention it.",
                "...Whatever.",
                "Koi baat nahi.",
            ])

        # Default responses based on warmth level
        return self._get_default_response(warmth_level)

    def _match_pattern(self, text: str, patterns: list) -> bool:
        """Check if text matches any of the given patterns."""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _get_greeting(self, warmth: int) -> str:
        """Get greeting based on warmth level."""
        greetings = [
            ["...Hello.", "Oh, it's you.", "Hi... kya chahiye?", "Tum kaun ho?"],
            ["Hi yaar.", "Hey there.", "Hello.", "Kya haal hai?"],
            ["Hey! How are you?", "Hi! Kaisa chal raha hai?", "Hello! Good to see you."],
            ["Hey! I was just thinking about you yaar.", "Hi! Tumse baat karke acha lagta hai.", "Hello! Kaise ho?"]
        ]
        return random.choice(greetings[min(warmth, 3)])

    def _get_farewell(self, warmth: int) -> str:
        """Get farewell based on warmth level."""
        farewells = [
            ["...See you.", "Bye.", "Later.", "Chalo bye."],
            ["See you later yaar.", "Take care.", "Bye.", "Milte hain."],
            ["See you soon!", "Take care of yourself.", "Goodbye yaar!", "Dhyan rakhna."],
            ["I'll miss talking to you. See you soon!", "Take care! Talk to you later yaar!", "Bye! Jaldi aana!"]
        ]
        return random.choice(farewells[min(warmth, 3)])

    def _get_default_response(self, warmth: int) -> str:
        """Get default response based on warmth level."""
        responses = [
            # Cold (warmth 0)
            [
                "...I see.",
                "Is that so?",
                "Hmm...",
                "...Okay.",
                "Whatever.",
                "...Theek hai.",
                "Acha.",
            ],
            # Neutral (warmth 1)
            [
                "I see what you mean.",
                "That's interesting yaar.",
                "Hmm, samajh aaya.",
                "Okay, I get it.",
                "That makes sense.",
                "Acha, theek hai.",
            ],
            # Warm (warmth 2)
            [
                "That's pretty interesting!",
                "Tumse baat karna acha lagta hai.",
                "Tell me more yaar.",
                "That's a good point.",
                "Maine aisa socha nahi tha.",
                "Interesting perspective hai tumhara.",
            ],
            # Very warm (warmth 3)
            [
                "I really enjoy our conversations yaar.",
                "You always have interesting things to say.",
                "Tumse baat karke acha lagta hai.",
                "That's really insightful!",
                "I appreciate that you share this with me.",
                "Tum actually samajhdar ho yaar.",
            ]
        ]
        return random.choice(responses[min(warmth, 3)])