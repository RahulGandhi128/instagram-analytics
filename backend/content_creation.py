#!/usr/bin/env python3
"""
Content Creation Service with LLM Integration
Provides visual content generation with analytics context and conversational memory
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import openai
from openai import OpenAI
import sqlite3
import hashlib
import base64
import requests
from io import BytesIO
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ContentRequest:
    """Content creation request structure"""
    user_id: str
    prompt: str
    content_type: str  # 'image', 'graphic', 'video', 'text'
    analytics_context: Optional[Dict] = None
    style_preferences: Optional[Dict] = None
    session_id: Optional[str] = None

@dataclass
class ContentResponse:
    """Content creation response structure"""
    content_id: str
    content_type: str
    content_url: Optional[str] = None
    content_data: Optional[str] = None  # Base64 encoded for images
    description: str = ""
    metadata: Optional[Dict] = None
    error: Optional[str] = None
    debug_info: Optional[Dict] = None

class ConversationMemory:
    """Manages conversational context and memory"""
    
    def __init__(self, db_path: str = "content_conversations.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize conversation database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    message_type TEXT NOT NULL,  -- 'user' or 'assistant'
                    content TEXT NOT NULL,
                    metadata TEXT,  -- JSON string
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS content_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT UNIQUE NOT NULL,
                    session_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    content_url TEXT,
                    analytics_context TEXT,  -- JSON string
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Conversation database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing conversation database: {e}")
    
    def add_message(self, session_id: str, user_id: str, message_type: str, content: str, metadata: Dict = None):
        """Add a message to conversation history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversations (session_id, user_id, message_type, content, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, user_id, message_type, content, json.dumps(metadata) if metadata else None))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error adding message to conversation: {e}")
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get recent conversation history for a session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT message_type, content, metadata, created_at
                FROM conversations
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (session_id, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            history = []
            for row in reversed(results):  # Reverse to get chronological order
                history.append({
                    'role': 'user' if row[0] == 'user' else 'assistant',
                    'content': row[1],
                    'metadata': json.loads(row[2]) if row[2] else None,
                    'timestamp': row[3]
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def save_content(self, content_id: str, session_id: str, user_id: str, 
                    content_type: str, prompt: str, content_url: str = None, 
                    analytics_context: Dict = None):
        """Save created content to history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO content_history 
                (content_id, session_id, user_id, content_type, prompt, content_url, analytics_context)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (content_id, session_id, user_id, content_type, prompt, content_url, 
                  json.dumps(analytics_context) if analytics_context else None))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving content history: {e}")

class ContentCreationService:
    """Main content creation service with LLM integration"""
    
    def __init__(self):
        self.client = None
        self.conversation_memory = ConversationMemory()
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize OpenAI client"""
        try:
            if not self.api_key:
                logger.error("OpenAI API key not found in environment variables")
                return False
            
            self.client = OpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {e}")
            return False
    
    def get_analytics_context_prompt(self, analytics_context: Dict) -> str:
        """Convert analytics context to a prompt-friendly format"""
        if not analytics_context:
            return ""
        
        context_parts = []
        
        # Basic stats
        if 'basic_stats' in analytics_context:
            stats = analytics_context['basic_stats']
            context_parts.append(f"Account has {stats.get('total_content', 0)} total posts with {stats.get('total_engagement', 0)} total engagement")
            context_parts.append(f"Average engagement per post: {stats.get('avg_engagement_per_post', 0)}")
        
        # Top performing content
        if 'top_posts' in analytics_context and analytics_context['top_posts']:
            top_post = analytics_context['top_posts'][0]
            context_parts.append(f"Best performing content type: {top_post.get('media_type', 'unknown')}")
            if 'hashtags' in top_post and top_post['hashtags']:
                context_parts.append(f"Successful hashtags: {', '.join(top_post['hashtags'][:3])}")
        
        # Content type breakdown
        if 'content_type_breakdown' in analytics_context.get('basic_stats', {}):
            breakdown = analytics_context['basic_stats']['content_type_breakdown']
            popular_types = [f"{k}: {v}" for k, v in breakdown.items() if v > 0]
            if popular_types:
                context_parts.append(f"Content distribution: {', '.join(popular_types)}")
        
        # Optimal posting times
        if 'optimal_posting_times' in analytics_context:
            times = analytics_context['optimal_posting_times']
            if 'favoured_posting_time' in times:
                context_parts.append(f"Best posting time: {times['favoured_posting_time']}")
        
        return "\n".join(context_parts)
    
    def build_conversation_context(self, session_id: str, current_prompt: str, analytics_context: Dict = None) -> List[Dict]:
        """Build conversation context including history and analytics"""
        messages = []
        
        # System message with analytics context
        system_prompt = """You are a creative content generation assistant for Instagram marketing. 
You help create engaging visual content, graphics, and video concepts based on analytics data and user preferences.

Your capabilities:
- Generate creative prompts for images and graphics
- Suggest video concepts and storyboards
- Create text content for captions and posts
- Analyze performance data to inform content strategy

Always consider the user's analytics context when making suggestions."""
        
        if analytics_context:
            analytics_prompt = self.get_analytics_context_prompt(analytics_context)
            if analytics_prompt:
                system_prompt += f"\n\nCurrent Analytics Context:\n{analytics_prompt}"
        
        messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        history = self.conversation_memory.get_conversation_history(session_id, limit=8)
        messages.extend([{"role": msg["role"], "content": msg["content"]} for msg in history])
        
        # Add current prompt
        messages.append({"role": "user", "content": current_prompt})
        
        return messages
    
    async def generate_image_with_dalle(self, prompt: str, style_preferences: Dict = None) -> Dict:
        """Generate image using DALL-E"""
        try:
            # Enhance prompt based on style preferences
            enhanced_prompt = prompt
            if style_preferences:
                if style_preferences.get('style'):
                    enhanced_prompt += f" in {style_preferences['style']} style"
                if style_preferences.get('colors'):
                    enhanced_prompt += f" using {style_preferences['colors']} color palette"
                if style_preferences.get('mood'):
                    enhanced_prompt += f" with {style_preferences['mood']} mood"
            
            # Add Instagram-specific formatting
            enhanced_prompt += " optimized for Instagram, high quality, professional"
            
            logger.info(f"Generating image with DALL-E: {enhanced_prompt}")
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.images.generate(
                    model="dall-e-3",
                    prompt=enhanced_prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1
                )
            )
            
            image_url = response.data[0].url
            
            # Download and convert to base64
            img_response = requests.get(image_url)
            img_data = base64.b64encode(img_response.content).decode('utf-8')
            
            return {
                'success': True,
                'url': image_url,
                'data': img_data,
                'prompt': enhanced_prompt
            }
            
        except Exception as e:
            logger.error(f"Error generating image with DALL-E: {e}")
            return {
                'success': False,
                'error': str(e),
                'debug_info': {
                    'service': 'DALL-E',
                    'model': 'dall-e-3',
                    'error_type': type(e).__name__
                }
            }
    
    async def generate_video_concept_with_sora(self, prompt: str, style_preferences: Dict = None) -> Dict:
        """Generate video concept (placeholder for Sora API when available)"""
        try:
            # Note: Sora is not yet publicly available via API
            # This is a placeholder implementation
            logger.warning("Sora API not yet available - generating video concept instead")
            
            # For now, generate a detailed video concept using GPT
            video_prompt = f"""Create a detailed video concept for Instagram based on this request: {prompt}

Please provide:
1. Video concept overview
2. Scene breakdown (3-5 scenes)
3. Visual style suggestions
4. Text overlay ideas
5. Music/audio suggestions
6. Duration recommendation
7. Call-to-action suggestions

Format as a detailed storyboard description."""
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": video_prompt}],
                    max_tokens=1000,
                    temperature=0.7
                )
            )
            
            concept = response.choices[0].message.content
            
            return {
                'success': True,
                'concept': concept,
                'type': 'video_concept',
                'debug_info': {
                    'service': 'GPT-4 (Sora placeholder)',
                    'note': 'Sora API not yet publicly available'
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating video concept: {e}")
            return {
                'success': False,
                'error': str(e),
                'debug_info': {
                    'service': 'Sora (unavailable)',
                    'fallback': 'GPT-4 concept generation',
                    'error_type': type(e).__name__
                }
            }
    
    async def generate_text_content(self, prompt: str, analytics_context: Dict = None) -> Dict:
        """Generate text content using GPT"""
        try:
            messages = []
            
            system_prompt = """You are an expert Instagram content creator. Generate engaging captions, hashtags, and text content that drives engagement. Consider current trends and best practices."""
            
            if analytics_context:
                analytics_prompt = self.get_analytics_context_prompt(analytics_context)
                if analytics_prompt:
                    system_prompt += f"\n\nAnalytics Context:\n{analytics_prompt}"
            
            messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    max_tokens=800,
                    temperature=0.8
                )
            )
            
            content = response.choices[0].message.content
            
            return {
                'success': True,
                'content': content,
                'type': 'text'
            }
            
        except Exception as e:
            logger.error(f"Error generating text content: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def create_content(self, request: ContentRequest) -> ContentResponse:
        """Main content creation method"""
        if not self.client:
            return ContentResponse(
                content_id="",
                content_type=request.content_type,
                error="OpenAI client not initialized",
                debug_info={"error": "API key missing or invalid"}
            )
        
        # Generate unique content ID
        content_id = hashlib.md5(f"{request.user_id}_{request.prompt}_{datetime.now().isoformat()}".encode()).hexdigest()
        
        # Build conversation context
        messages = self.build_conversation_context(
            request.session_id or content_id,
            request.prompt,
            request.analytics_context
        )
        
        # Save user message to conversation history
        if request.session_id:
            self.conversation_memory.add_message(
                request.session_id,
                request.user_id,
                "user",
                request.prompt,
                {"content_type": request.content_type}
            )
        
        try:
            result = None
            debug_info = {}
            
            if request.content_type == "image" or request.content_type == "graphic":
                # Generate enhanced prompt first using GPT
                prompt_enhancement = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.chat.completions.create(
                        model="gpt-4",
                        messages=messages + [{"role": "user", "content": f"Create a detailed, visual prompt for generating {request.content_type} content: {request.prompt}"}],
                        max_tokens=200,
                        temperature=0.7
                    )
                )
                
                enhanced_prompt = prompt_enhancement.choices[0].message.content
                result = await self.generate_image_with_dalle(enhanced_prompt, request.style_preferences)
                
            elif request.content_type == "video":
                result = await self.generate_video_concept_with_sora(request.prompt, request.style_preferences)
                
            elif request.content_type == "text":
                result = await self.generate_text_content(request.prompt, request.analytics_context)
            
            else:
                # Default to conversational response
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.chat.completions.create(
                        model="gpt-4",
                        messages=messages,
                        max_tokens=500,
                        temperature=0.7
                    )
                )
                
                result = {
                    'success': True,
                    'content': response.choices[0].message.content,
                    'type': 'conversation'
                }
            
            # Save assistant response to conversation history
            if request.session_id and result and result.get('success'):
                response_content = result.get('content') or result.get('concept') or "Content generated successfully"
                self.conversation_memory.add_message(
                    request.session_id,
                    request.user_id,
                    "assistant",
                    response_content,
                    {"content_type": request.content_type, "content_id": content_id}
                )
            
            # Save content to history
            if result and result.get('success'):
                self.conversation_memory.save_content(
                    content_id,
                    request.session_id or content_id,
                    request.user_id,
                    request.content_type,
                    request.prompt,
                    result.get('url'),
                    request.analytics_context
                )
            
            # Prepare response
            if result and result.get('success'):
                return ContentResponse(
                    content_id=content_id,
                    content_type=request.content_type,
                    content_url=result.get('url'),
                    content_data=result.get('data'),
                    description=result.get('content') or result.get('concept') or "Content generated successfully",
                    metadata={"prompt": result.get('prompt'), "style": request.style_preferences},
                    debug_info=result.get('debug_info', debug_info)
                )
            else:
                return ContentResponse(
                    content_id=content_id,
                    content_type=request.content_type,
                    error=result.get('error') if result else "Unknown error occurred",
                    debug_info=result.get('debug_info', debug_info) if result else {"error": "No result returned"}
                )
                
        except Exception as e:
            logger.error(f"Error in content creation: {e}")
            return ContentResponse(
                content_id=content_id,
                content_type=request.content_type,
                error=str(e),
                debug_info={"error_type": type(e).__name__, "error_details": str(e)}
            )

# Global service instance
content_service = ContentCreationService()

def get_content_service():
    """Get the global content creation service instance"""
    return content_service

# FastAPI route functions (to be imported in main.py)
async def create_content_endpoint(request_data: dict):
    """FastAPI endpoint for content creation"""
    try:
        request = ContentRequest(
            user_id=request_data.get('user_id', 'anonymous'),
            prompt=request_data.get('prompt', ''),
            content_type=request_data.get('content_type', 'text'),
            analytics_context=request_data.get('analytics_context'),
            style_preferences=request_data.get('style_preferences'),
            session_id=request_data.get('session_id')
        )
        
        response = await content_service.create_content(request)
        return asdict(response)
        
    except Exception as e:
        logger.error(f"Error in content creation endpoint: {e}")
        return {
            "content_id": "",
            "content_type": request_data.get('content_type', 'unknown'),
            "error": str(e),
            "debug_info": {"endpoint_error": str(e)}
        }

async def get_conversation_history_endpoint(session_id: str):
    """FastAPI endpoint for getting conversation history"""
    try:
        history = content_service.conversation_memory.get_conversation_history(session_id)
        return {"history": history}
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        return {"error": str(e), "history": []}

if __name__ == "__main__":
    # Test the service
    async def test_service():
        service = ContentCreationService()
        
        test_request = ContentRequest(
            user_id="test_user",
            prompt="Create a motivational Instagram post about morning routines",
            content_type="text",
            analytics_context={
                "basic_stats": {
                    "total_content": 50,
                    "total_engagement": 5000,
                    "avg_engagement_per_post": 100
                }
            }
        )
        
        response = await service.create_content(test_request)
        print(f"Test Response: {response}")
    
    # Uncomment to test
    # asyncio.run(test_service())
