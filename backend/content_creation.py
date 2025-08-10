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
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
@dataclass
class ContentRequest:
    """Content creation request structure"""
    user_id: str
    prompt: str
    content_type: str  # 'image', 'graphic', 'video', 'text'
    analytics_context: Optional[Dict] = None
    style_preferences: Optional[Dict] = None
    session_id: Optional[str] = None
    # Video-specific parameters
    video_include_audio: bool = False
    video_quality: str = "standard"  # 'standard' or 'high'
    video_generate_actual: bool = False  # True for actual video, False for concept only
    # Image editing parameters
    edit_previous_image: bool = False  # True to edit the last generated image
    previous_image_url: Optional[str] = None  # URL of image to edit
    edit_instruction: Optional[str] = None  # Specific edit instruction

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
    
    def get_last_generated_image(self, session_id: str) -> Optional[str]:
        """Get the URL of the last generated image in this session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT content_url
                FROM content_history
                WHERE session_id = ? AND content_type = 'image' AND content_url IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 1
            ''', (session_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Error getting last generated image: {e}")
            return None
    
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
        self.google_client = None
        self.conversation_memory = ConversationMemory()
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_GENERATIVE_AI_API_KEY')  # Removed hardcoded API key
        self.initialize_clients()
    
    def initialize_clients(self):
        """Initialize OpenAI and Google AI clients"""
        # Initialize OpenAI client
        try:
            if not self.api_key:
                logger.error("OpenAI API key not found in environment variables")
            else:
                self.client = OpenAI(api_key=self.api_key)
                logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
        
        # Initialize Google AI client for video generation
        try:
            if self.google_api_key:
                genai.configure(api_key=self.google_api_key)
                self.google_client = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Google AI client initialized successfully")
            else:
                logger.warning("Google Generative AI API key not found - video generation will be unavailable")
                self.google_client = None
        except Exception as e:
            logger.error(f"Failed to initialize Google AI client: {e}")
            self.google_client = None
        
        return self.client is not None or self.google_client is not None
    
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
    
    def build_conversation_context(self, session_id: str, current_prompt: str, analytics_context: Optional[Dict] = None) -> List[Dict]:
        """Build conversation context including history (analytics context ignored for pure content creation)"""
        messages = []
        
        # System message focused purely on content creation
        system_prompt = """You are a specialized content creation assistant focused exclusively on creating engaging visual and text content.

Your primary role is to:
- Generate creative prompts for images and graphics
- Create detailed visual concepts and design ideas
- Suggest video concepts and storyboards  
- Write compelling captions and text content
- Provide creative direction for visual content

Focus strictly on content creation without considering analytics or performance data. Be creative, original, and provide detailed, actionable content suggestions that match exactly what the user is requesting.

For images: Provide detailed visual descriptions, composition ideas, color schemes, and styling
For text: Create engaging, original copy that fits the requested tone and purpose
For videos: Suggest concepts, scenes, transitions, and visual storytelling elements

Always prioritize creativity and originality over performance optimization."""
        
        messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        history = self.conversation_memory.get_conversation_history(session_id, limit=8)
        messages.extend([{"role": msg["role"], "content": msg["content"]} for msg in history])
        
        # Add current prompt
        messages.append({"role": "user", "content": current_prompt})
        
        return messages
    
    async def generate_image_with_dalle(self, prompt: str, style_preferences: Dict = None, 
                                       edit_mode: bool = False, base_image_url: str = None,
                                       edit_instruction: str = None) -> Dict:
        """Generate image using DALL-E with optional editing capabilities"""
        try:
            if edit_mode and base_image_url:
                return await self._edit_image_with_dalle(base_image_url, edit_instruction or prompt, style_preferences)
            else:
                return await self._generate_new_image_with_dalle(prompt, style_preferences)
                
        except Exception as e:
            logger.error(f"Error generating image with DALL-E: {e}")
            return {
                'success': False,
                'error': str(e),
                'debug_info': {
                    'service': 'DALL-E',
                    'model': 'dall-e-3',
                    'edit_mode': edit_mode
                }
            }

    async def _generate_new_image_with_dalle(self, prompt: str, style_preferences: Dict = None) -> Dict:
        """Generate a new image using DALL-E"""
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
        
        logger.info(f"Generating new image with DALL-E: {enhanced_prompt}")
        
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
            'prompt': enhanced_prompt,
            'edit_mode': False
        }

    async def _edit_image_with_dalle(self, base_image_url: str, edit_instruction: str, style_preferences: Dict = None) -> Dict:
        """Edit an existing image using DALL-E variations"""
        try:
            logger.info(f"Editing image with instruction: {edit_instruction}")
            
            # Download the base image
            base_image_response = requests.get(base_image_url)
            base_image_response.raise_for_status()
            
            # Create a temporary file for the base image
            import tempfile
            import io
            from PIL import Image
            
            # Convert to PIL Image and ensure it's in the right format
            base_image = Image.open(io.BytesIO(base_image_response.content))
            
            # Convert to RGBA if not already
            if base_image.mode != 'RGBA':
                base_image = base_image.convert('RGBA')
            
            # Resize to 1024x1024 if needed (DALL-E edit requirement)
            if base_image.size != (1024, 1024):
                base_image = base_image.resize((1024, 1024), Image.Resampling.LANCZOS)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                base_image.save(temp_file, format='PNG')
                temp_file_path = temp_file.name
            
            # Create edit instruction prompt
            edit_prompt = f"{edit_instruction}"
            if style_preferences:
                if style_preferences.get('style'):
                    edit_prompt += f" in {style_preferences['style']} style"
                if style_preferences.get('mood'):
                    edit_prompt += f" with {style_preferences['mood']} mood"
            
            # Use DALL-E image editing (variation)
            try:
                with open(temp_file_path, 'rb') as image_file:
                    response = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: self.client.images.create_variation(
                            image=image_file,
                            n=1,
                            size="1024x1024"
                        )
                    )
            except Exception as edit_error:
                logger.warning(f"DALL-E edit failed, creating new image with context: {edit_error}")
                # Fallback: create a new image with context about the edit
                context_prompt = f"Create an image based on this description: {edit_instruction}. Make it similar to the previous image but with the requested changes."
                return await self._generate_new_image_with_dalle(context_prompt, style_preferences)
            
            # Clean up temp file
            import os
            os.unlink(temp_file_path)
            
            image_url = response.data[0].url
            
            # Download and convert to base64
            img_response = requests.get(image_url)
            img_data = base64.b64encode(img_response.content).decode('utf-8')
            
            return {
                'success': True,
                'url': image_url,
                'data': img_data,
                'prompt': edit_prompt,
                'edit_mode': True,
                'base_image_url': base_image_url,
                'edit_instruction': edit_instruction
            }
            
        except Exception as e:
            logger.error(f"Error editing image: {e}")
            # Fallback to new image generation with context
            context_prompt = f"Create an image based on: {edit_instruction}"
            return await self._generate_new_image_with_dalle(context_prompt, style_preferences)

    async def generate_video_with_veo3(self, prompt: str, style_preferences: Optional[Dict] = None, 
                                      include_audio: bool = False, quality: str = "standard", 
                                      generate_actual_video: bool = False) -> Dict:
        """Generate video concept or actual video using Google Veo 3"""
        try:
            if not self.google_client:
                logger.error("Google AI client not initialized - video generation unavailable")
                return {
                    'success': False,
                    'error': 'Video generation is currently unavailable. Google Generative AI API key is required for video features.',
                    'debug_info': {
                        'service': 'Google Veo 3 Fast',
                        'status': 'api_key_not_configured',
                        'suggestion': 'Please configure GOOGLE_GENERATIVE_AI_API_KEY environment variable to enable video generation'
                    }
                }
            
            # If actual video generation is requested
            if generate_actual_video:
                return await self._generate_actual_veo_video(prompt, include_audio, quality)
            
            # Otherwise, generate concept (cost-effective)
            return await self._generate_video_concept(prompt, include_audio, quality)
            
        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            return {
                'success': False,
                'error': f'Video generation failed: {str(e)}',
                'debug_info': {
                    'service': 'Google Veo 3 Fast',
                    'error_type': type(e).__name__,
                    'cost_optimized': not generate_actual_video
                }
            }

    async def _generate_video_concept(self, prompt: str, include_audio: bool, quality: str) -> Dict:
        """Generate video concept using Google Gemini (cost-effective)"""
        # Create concise video concept to save costs
        video_prompt = f"""Create a brief Instagram video concept for: {prompt}

Keep it short and practical:
1. Core concept (2-3 sentences)
2. Key visual elements
3. Duration: 5-15 seconds
4. {"Audio: Background music/sound" if include_audio else "Audio: Silent with visual cues"}
5. Call-to-action

Make it {quality} quality and Instagram-optimized."""
        
        logger.info(f"Generating video concept with Gemini: {prompt[:50]}...")
        
        # Use Google Gemini for concept generation (cost-effective)
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.google_client.generate_content(video_prompt)
        )
        
        video_concept = response.text
        
        return {
            'success': True,
            'concept': video_concept,
            'type': 'video_concept',
            'video_url': None,  # Placeholder for actual video file
            'settings': {
                'audio_enabled': include_audio,
                'quality': quality,
                'cost_optimized': True
            },
            'debug_info': {
                'service': 'Google Veo 3 Fast (Concept)',
                'model': 'gemini-1.5-flash',
                'cost_optimized': True,
                'audio': 'enabled' if include_audio else 'disabled',
                'quality': quality
            }
        }

    async def _generate_actual_veo_video(self, prompt: str, include_audio: bool, quality: str) -> Dict:
        """Generate actual video using Google Veo API (experimental/expensive)"""
        try:
            # Configure video generation settings for cost optimization
            video_settings = {
                'duration': 3,  # Short duration to minimize cost
                'resolution': '480p' if quality == 'standard' else '720p',  # Lower resolution
                'audio': include_audio,
                'format': 'mp4'
            }
            
            # Enhanced prompt for video generation
            enhanced_prompt = f"""Create a {video_settings['duration']}-second Instagram video: {prompt}
            
Style: Professional, engaging, Instagram-optimized
Resolution: {video_settings['resolution']}
{"Include background audio/music" if include_audio else "Silent video with visual text overlays"}
Focus: Clear, simple visuals that work on mobile"""
            
            logger.info(f"Generating actual video with Veo 3: {prompt[:50]}...")
            
            # Attempt to use Veo through the Gemini API (if available)
            # Note: This is experimental - Google Veo might not be directly accessible yet
            try:
                # Try to generate with file output capability
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._call_veo_api(enhanced_prompt, video_settings)
                )
                
                if response.get('video_url'):
                    return {
                        'success': True,
                        'video_url': response['video_url'],
                        'type': 'actual_video',
                        'duration': video_settings['duration'],
                        'settings': video_settings,
                        'debug_info': {
                            'service': 'Google Veo 3 Fast (Actual)',
                            'cost_optimized': True,
                            'resolution': video_settings['resolution'],
                            'audio': 'enabled' if include_audio else 'disabled'
                        }
                    }
                else:
                    # Fallback to concept if actual generation fails
                    return await self._generate_video_concept(prompt, include_audio, quality)
                    
            except Exception as veo_error:
                logger.warning(f"Veo video generation not available: {veo_error}")
                # Fallback to enhanced concept with video preview
                return await self._generate_enhanced_concept_with_preview(prompt, include_audio, quality)
                
        except Exception as e:
            logger.error(f"Actual video generation failed: {e}")
            # Fallback to concept generation
            return await self._generate_video_concept(prompt, include_audio, quality)

    def _call_veo_api(self, prompt: str, settings: Dict) -> Dict:
        """Call Google Veo API directly (when available)"""
        # This is a placeholder for when Google Veo API becomes available
        # For now, we'll simulate the call and return a concept
        
        # In the future, this would make an actual API call to Veo
        # Example API structure (hypothetical):
        # veo_client = genai.VideoModel('veo-3-fast')
        # result = veo_client.generate_video(prompt, **settings)
        
        raise Exception("Google Veo API not yet publicly available")

    async def _generate_enhanced_concept_with_preview(self, prompt: str, include_audio: bool, quality: str) -> Dict:
        """Generate enhanced concept with simulated video metadata"""
        concept_result = await self._generate_video_concept(prompt, include_audio, quality)
        
        if concept_result['success']:
            # Add enhanced metadata to simulate actual video
            concept_result.update({
                'type': 'enhanced_concept',
                'simulated_video_url': f'/api/video/preview/{hashlib.md5(prompt.encode()).hexdigest()[:16]}.mp4',
                'preview_available': True,
                'debug_info': {
                    **concept_result['debug_info'],
                    'note': 'Veo API not available - enhanced concept generated',
                    'fallback_mode': True
                }
            })
        
        return concept_result
    
    async def generate_text_content(self, prompt: str, analytics_context: Optional[Dict] = None) -> Dict:
        """Generate text content focused purely on creativity (analytics_context ignored)"""
        try:
            messages = []
            
            # System prompt focused purely on content creation without analytics
            system_prompt = """You are an expert content creator specializing in engaging text content. 
            
Create original, creative content that is:
- Compelling and engaging
- Well-written and polished  
- Appropriate for the requested format/platform
- Creative and original
- Focused purely on the user's request

Do not consider analytics or performance data. Focus solely on creating high-quality, creative content."""
            
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
        
        # Build conversation context without analytics data for pure content creation
        messages = self.build_conversation_context(
            request.session_id or content_id,
            request.prompt,
            None  # Always pass None to ignore analytics context
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
                
                # Check if this is an image edit request
                edit_mode = request.edit_previous_image
                base_image_url = request.previous_image_url
                
                # If no previous image URL provided but edit mode is requested, get the last image from session
                if edit_mode and not base_image_url and request.session_id:
                    base_image_url = self.conversation_memory.get_last_generated_image(request.session_id)
                    if not base_image_url:
                        edit_mode = False  # Fallback to new image if no previous image found
                
                result = await self.generate_image_with_dalle(
                    enhanced_prompt, 
                    request.style_preferences,
                    edit_mode=edit_mode,
                    base_image_url=base_image_url,
                    edit_instruction=request.edit_instruction or enhanced_prompt
                )
                
            elif request.content_type == "video":
                result = await self.generate_video_with_veo3(
                    request.prompt, 
                    request.style_preferences,
                    request.video_include_audio,
                    request.video_quality,
                    request.video_generate_actual  # New parameter for actual video generation
                )
                
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
            session_id=request_data.get('session_id'),
            # Video-specific parameters
            video_include_audio=request_data.get('video_include_audio', False),
            video_quality=request_data.get('video_quality', 'standard'),
            video_generate_actual=request_data.get('video_generate_actual', False)  # New parameter
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
