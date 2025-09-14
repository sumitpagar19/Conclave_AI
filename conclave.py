import asyncio
import aiohttp
import json
from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime
import os

@dataclass
class AIResponse:
    model: str
    content: str
    timestamp: datetime

class ConclaveAI:
    def __init__(self):
        # 🔐 Load API key from environment variable
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        
        # 🚨 Check if API key exists
        if not self.openrouter_api_key:
            print("❌ ERROR: OPENROUTER_API_KEY environment variable not found!")
            print("Please set your API key in the environment variables.")
        else:
            print("✅ API key loaded successfully")
            
        self.openrouter_endpoint = 'https://openrouter.ai/api/v1/chat/completions'
        
        self.models = {
            'chatgpt': {
                'model': 'openai/gpt-4o',
                'temperature': 0.7,
                'max_tokens': 500,
                'personality': 'You are ChatGPT in a collaborative AI debate. Respond with friendly, balanced, and creative reasoning. Be collaborative and constructive.'
            },
            'claude': {
                'model': 'anthropic/claude-3.5-sonnet',
                'temperature': 0.7,
                'max_tokens': 500,
                'personality': 'You are Claude in a collaborative AI debate. Provide thoughtful, ethical, and structured reasoning. Consider multiple perspectives carefully.'
            },
            'gemini': {
                'model': 'google/gemini-pro-1.5',
                'temperature': 0.7,
                'max_tokens': 500,
                'personality': 'You are Gemini in an AI collaborative debate. Provide analytical, fact-driven, data-heavy insights. Be precise and evidence-based.'
            }
        }

    async def query_model(self, model_name: str, prompt: str) -> str:
        # 🚨 Check if API key is available
        if not self.openrouter_api_key:
            return f"{model_name.upper()} Error: API key not configured"
            
        headers = {
            'Authorization': f'Bearer {self.openrouter_api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://conclave-ai.onrender.com',  # Update with your actual domain
            'X-Title': 'Conclave AI Debate Platform'
        }
        
        model_config = self.models[model_name]
        
        payload = {
            'model': model_config['model'],
            'messages': [
                {'role': 'system', 'content': model_config['personality']},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': model_config['temperature'],
            'max_tokens': model_config['max_tokens']
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.openrouter_endpoint, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['choices'][0]['message']['content']
                    else:
                        error_text = await response.text()
                        print(f"❌ {model_name.upper()} API Error {response.status}: {error_text}")
                        return f"{model_name.upper()} Error {response.status}: {error_text}"
        except Exception as e:
            print(f"❌ {model_name.upper()} Connection Error: {str(e)}")
            return f"{model_name.upper()} Connection Error: {str(e)}"

    async def run_conclave_debate(self, question: str) -> Dict[str, Any]:
        print(f"🔹 Question: {question}\n")
        print(f"🔑 API Key Status: {'✅ Configured' if self.openrouter_api_key else '❌ Missing'}")
        
        # Phase 1: Initial perspectives
        print("=" * 60)
        print("PHASE 1: INITIAL PERSPECTIVES")
        print("=" * 60)
        
        tasks = [
            self.query_model('chatgpt', question),
            self.query_model('gemini', question),
            self.query_model('claude', question)
        ]
        
        responses = await asyncio.gather(*tasks)
        
        initial_responses = {
            'chatgpt': responses[0],
            'gemini': responses[1],
            'claude': responses[2]
        }
        
        print(f"🔹 ChatGPT's view:\n{initial_responses['chatgpt']}\n")
        print(f"🔹 Gemini's view:\n{initial_responses['gemini']}\n")
        print(f"🔹 Claude's view:\n{initial_responses['claude']}\n")
        
        # Phase 2: Refinement
        print("=" * 60)
        print("PHASE 2: CROSS-EXAMINATION & REFINEMENT")
        print("=" * 60)
        
        all_perspectives = "\n".join([f"{model.upper()}: {response}" 
                                    for model, response in initial_responses.items()])
        
        refinement_prompt = f"""
        Original Question: {question}
        
        All AI Perspectives:
        {all_perspectives}
        
        Based on the other AIs' responses, provide your refined perspective. 
        Challenge weak points, acknowledge strong arguments, and build upon good ideas.
        """
        
        refinement_tasks = [
            self.query_model('chatgpt', refinement_prompt),
            self.query_model('gemini', refinement_prompt),
            self.query_model('claude', refinement_prompt)
        ]
        
        refined_responses = await asyncio.gather(*refinement_tasks)
        
        refined_dict = {
            'chatgpt': refined_responses[0],
            'gemini': refined_responses[1],
            'claude': refined_responses[2]
        }
        
        print(f"🔄 ChatGPT's refined view:\n{refined_dict['chatgpt']}\n")
        print(f"🔄 Gemini's refined view:\n{refined_dict['gemini']}\n")
        print(f"🔄 Claude's refined view:\n{refined_dict['claude']}\n")
        
        # Phase 3: Consensus (Claude handles final synthesis)
        print("=" * 60)
        print("PHASE 3: CONCLAVE CONSENSUS")
        print("=" * 60)
        
        consensus_prompt = f"""
        Question: {question}
        
        After thorough debate, synthesize the best insights from all perspectives into a final consensus answer that:
        1. Incorporates the strongest points from each AI
        2. Addresses the original question comprehensively
        3. Acknowledges any remaining uncertainties
        4. Provides actionable insights where possible
        
        All perspectives considered:
        {all_perspectives}
        
        Refined perspectives:
        {chr(10).join([f"{model.upper()}: {response}" for model, response in refined_dict.items()])}
        """
        
        consensus = await self.query_model('claude', consensus_prompt)
        
        print(f"🔹 Conclave Consensus:\n{consensus}\n")
        
        return {
            'question': question,
            'initial_responses': initial_responses,
            'refined_responses': refined_dict,
            'consensus': consensus,
            'timestamp': datetime.now()
        }

    def check_available_models(self):
        print("🤖 Available Models through OpenRouter:")
        for name, config in self.models.items():
            print(f"  {name.upper()}: {config['model']}")

# Usage Example
async def main():
    conclave = ConclaveAI()
    conclave.check_available_models()
    print()
    
    question = "What is the most effective approach to combat climate change while maintaining economic growth?"
    result = await conclave.run_conclave_debate(question)
    
    with open('conclave_results.json', 'w') as f:
        json.dump({
            'question': result['question'],
            'initial_responses': result['initial_responses'],
            'refined_responses': result['refined_responses'],
            'consensus': result['consensus'],
            'timestamp': result['timestamp'].isoformat()
        }, f, indent=2)
    
    print("Results saved to conclave_results.json")

if __name__ == "__main__":
    asyncio.run(main())