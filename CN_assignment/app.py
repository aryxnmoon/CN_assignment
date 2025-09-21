"""
Excel Mock Interviewer
A conversational system for conducting Excel technical interviews
"""
import streamlit as st
import json
import random
import os
import html
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

def _format_duration(start_time):
    """Format duration in MM:SS or HH:MM:SS format"""
    if not start_time:
        return "0:00"
    duration = datetime.now() - start_time
    total_seconds = int(duration.total_seconds())
    if total_seconds < 3600:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"
    else:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours}:{minutes:02d}:{seconds:02d}"

# Interview States
class InterviewPhase(Enum):
    GREETING = "greeting"
    WARMUP = "warmup"
    CORE_SKILLS = "core_skills"
    SCENARIO_BASED = "scenario_based"
    TROUBLESHOOTING = "troubleshooting"
    WRAPUP = "wrapup"
    FEEDBACK = "feedback"

@dataclass
class InterviewMessage:
    role: str  # "interviewer" or "candidate"
    content: str
    timestamp: datetime
    phase: InterviewPhase
    question_id: Optional[str] = None
    evaluation: Optional[Dict] = None

@dataclass
class InterviewState:
    candidate_name: str
    current_phase: InterviewPhase
    conversation_history: List[InterviewMessage]
    current_question: Optional[Dict] = None
    evaluation_scores: List[Dict] = field(default_factory=list)
    start_time: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)

class ExcelInterviewAgent:
    def __init__(self):
        self.questions = self._load_question_bank()
        # Model URLs for potential future use
        self.model_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        self.evaluation_url = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
        
    def _load_question_bank(self) -> Dict[str, List[Dict]]:
        """Load questions from JSON file"""
        try:
            with open('comprehensive_questions.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Organize questions by section
            organized_questions = {
                "warmup": [],
                "core_skills": [],
                "scenario_based": [],
                "troubleshooting": []
            }
            
            for question in data.get('questions', []):
                section = question.get('section', 'warmup')
                # Map sections to phases
                if section == "warmup":
                    organized_questions["warmup"].append(question)
                elif section == "core":
                    organized_questions["core_skills"].append(question)
                elif section == "scenario":
                    organized_questions["scenario_based"].append(question)
                elif section == "troubleshoot":
                    organized_questions["troubleshooting"].append(question)
            
            return organized_questions
        except FileNotFoundError:
            st.error("Question bank file not found. Using fallback questions.")
            return self._get_fallback_questions()
        except Exception as e:
            st.error(f"Error loading question bank: {e}")
            return self._get_fallback_questions()
    
    def _get_fallback_questions(self) -> Dict[str, List[Dict]]:
        """Fallback questions if JSON file fails to load"""
        return {
            "warmup": [
                {"id": "w1", "question": "What's your experience with Excel? How long have you been using it?", "type": "experience"},
                {"id": "w2", "question": "Can you walk me through how you would sum a column of numbers?", "type": "basic"}
            ],
            "core_skills": [
                {"id": "c1", "question": "How would you use VLOOKUP to find data in a table?", "type": "lookup"},
                {"id": "c2", "question": "Explain how PivotTables work and when you'd use them.", "type": "analysis"}
            ],
            "scenario_based": [
                {"id": "s1", "question": "You have a dataset with 10,000 rows of sales data. How would you analyze it to find the top 10 customers?", "type": "analysis"}
            ],
            "troubleshooting": [
                {"id": "t1", "question": "A VLOOKUP formula is returning #N/A. What could be causing this?", "type": "debugging"}
            ]
        }
    
    def _call_ai_model(self, prompt: str, model_url: str) -> str:
        """Call external model for analysis"""
        try:
            headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN', 'hf_demo_token')}"}
            payload = {"inputs": prompt, "parameters": {"max_length": 200, "temperature": 0.7}}
            response = requests.post(model_url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "")
                elif isinstance(result, dict):
                    return result.get("generated_text", "")
            return ""
        except Exception as e:
            print(f"Model call failed: {e}")
            return ""

    def _ai_evaluate_response(self, question: Dict, response: str, phase: InterviewPhase) -> Dict:
        """Advanced evaluation system"""
        try:
            # Scoring algorithm
            response_lower = response.lower()
            question_text = question.get("question", "").lower()
            
            # Initialize scoring components
            technical_accuracy = 0
            completeness = 0
            clarity = 0
            excel_knowledge = 0
            reasoning = []
            strengths = []
            areas_for_improvement = []
            
            # Technical accuracy scoring
            if any(term in response_lower for term in ['function', 'formula', 'cell', 'range', 'data']):
                technical_accuracy += 3
                strengths.append("Uses Excel terminology correctly")
            
            if any(term in response_lower for term in ['=', 'sum', 'count', 'average', 'vlookup', 'index', 'match']):
                technical_accuracy += 4
                strengths.append("Demonstrates knowledge of Excel functions")
            
            if 'pivot' in response_lower or 'table' in response_lower:
                technical_accuracy += 2
                strengths.append("Shows understanding of data analysis tools")
            
            # Completeness scoring
            word_count = len(response.split())
            if word_count > 50:
                completeness += 4
                strengths.append("Provides comprehensive answer")
            elif word_count > 20:
                completeness += 2
            else:
                areas_for_improvement.append("Could provide more detail")
                completeness += 1
            
            # Clarity scoring
            if response.count('.') > 1:
                clarity += 2
                strengths.append("Well-structured response")
            
            if any(term in response_lower for term in ['example', 'for instance', 'such as']):
                clarity += 2
                strengths.append("Provides examples")
            
            # Excel knowledge scoring
            excel_terms = ['excel', 'spreadsheet', 'worksheet', 'workbook', 'formula', 'function']
            excel_term_count = sum(1 for term in excel_terms if term in response_lower)
            excel_knowledge = min(5, excel_term_count)
            
            if excel_knowledge > 2:
                strengths.append("Demonstrates Excel expertise")
            
            # Phase-specific scoring
            if phase.value == "warmup":
                if any(term in response_lower for term in ['experience', 'years', 'used', 'familiar']):
                    technical_accuracy += 2
            elif phase.value == "core_skills":
                if any(term in response_lower for term in ['vlookup', 'index', 'match', 'sumif', 'countif']):
                    technical_accuracy += 3
            elif phase.value == "scenario_based":
                if any(term in response_lower for term in ['analyze', 'pivot', 'filter', 'sort']):
                    technical_accuracy += 3
            elif phase.value == "troubleshooting":
                if any(term in response_lower for term in ['error', 'fix', 'debug', 'check']):
                    technical_accuracy += 3
            
            # Calculate final score
            total_score = (technical_accuracy + completeness + clarity + excel_knowledge) / 4
            final_score = min(10, max(1, total_score))
            
            # Generate reasoning
            if final_score >= 8:
                reasoning.append("Excellent response demonstrating strong Excel knowledge")
            elif final_score >= 6:
                reasoning.append("Good response with solid Excel understanding")
            elif final_score >= 4:
                reasoning.append("Basic response showing some Excel knowledge")
            else:
                reasoning.append("Response needs improvement in technical detail")
                areas_for_improvement.append("Focus on Excel-specific terminology and examples")
            
            return {
                "score": round(final_score, 1),
                "reasoning": ". ".join(reasoning),
                "strengths": strengths if strengths else ["Attempted to answer"],
                "areas_for_improvement": areas_for_improvement if areas_for_improvement else ["Provide more technical detail"],
                "evaluation_type": "advanced"
            }
                
        except Exception as e:
            print(f"Evaluation failed: {e}")
            return self._rule_based_evaluate_response(question, response, phase)

    def _rule_based_evaluate_response(self, question: Dict, response: str, phase: InterviewPhase) -> Dict:
        """Basic evaluation system"""
        try:
            response_lower = response.lower()
            question_text = question.get("question", "").lower()
            
            # Initialize scoring
            score = 0.0
            reasoning = []
            strengths = []
            areas_for_improvement = []
            
            # Basic response quality
            if len(response.strip()) < 10:
                score += 1.0
                reasoning.append("Very short response")
                areas_for_improvement.append("Provide more detailed answers")
            elif len(response.strip()) < 30:
                score += 2.0
                reasoning.append("Short response")
            elif len(response.strip()) > 50:
                score += 3.0
                reasoning.append("Detailed response")
                strengths.append("Provides comprehensive answer")
            
            # Technical accuracy based on question content
            if "sum" in question_text:
                if any(term in response_lower for term in ['add', 'total', 'sum', 'plus', 'addition', 'calculate']):
                    score += 3.0
                    strengths.append("Correctly identifies SUM function purpose")
                else:
                    areas_for_improvement.append("Should mention adding/totaling numbers")
            
            elif "count" in question_text:
                if any(term in response_lower for term in ['count', 'number', 'how many', 'quantity', 'items']):
                    score += 3.0
                    strengths.append("Understands COUNT function purpose")
                else:
                    areas_for_improvement.append("Should mention counting items")
            
            elif "vlookup" in question_text:
                if any(term in response_lower for term in ['lookup', 'find', 'search', 'match', 'reference', 'table']):
                    score += 3.0
                    strengths.append("Shows understanding of VLOOKUP concept")
                else:
                    areas_for_improvement.append("Should mention looking up values in tables")
            
            elif "pivot" in question_text:
                if any(term in response_lower for term in ['pivot', 'table', 'summarize', 'group', 'analyze', 'data']):
                    score += 3.0
                    strengths.append("Understands PivotTable functionality")
                else:
                    areas_for_improvement.append("Should mention data summarization and analysis")
            
            # Excel-specific terminology
            excel_terms = ['excel', 'spreadsheet', 'worksheet', 'workbook', 'cell', 'range', 'formula']
            found_excel_terms = sum(1 for term in excel_terms if term in response_lower)
            if found_excel_terms > 0:
                score += min(found_excel_terms * 0.5, 2.0)
                strengths.append("Uses appropriate Excel terminology")
            
            # Technical depth indicators
            technical_indicators = ['function', 'formula', 'data', 'analysis', 'business', 'report']
            found_technical = sum(1 for term in technical_indicators if term in response_lower)
            if found_technical > 0:
                score += min(found_technical * 0.3, 1.5)
                strengths.append("Shows technical understanding")
            
            # Confidence and experience indicators
            confidence_indicators = ["i think", "i believe", "i would", "i usually", "in my experience", "typically"]
            if any(indicator in response_lower for indicator in confidence_indicators):
                score += 0.5
                strengths.append("Shows confidence in response")
            
            # Ensure score is between 1-10
            score = max(1.0, min(10.0, score))
            
            # Generate detailed reasoning
            if score >= 8:
                reasoning.append("Excellent technical response with clear understanding")
            elif score >= 6:
                reasoning.append("Good response demonstrating solid Excel knowledge")
            elif score >= 4:
                reasoning.append("Basic response showing some understanding")
            else:
                reasoning.append("Response needs significant improvement in technical detail")
            
            return {
                "score": round(score, 1),
                "reasoning": ". ".join(reasoning),
                "strengths": strengths if strengths else ["Attempted to answer"],
                "areas_for_improvement": areas_for_improvement if areas_for_improvement else ["Provide more technical detail"]
            }
            
        except Exception as e:
            # Fallback evaluation
            return {
                "score": 5.0,
                "reasoning": "Basic response evaluation",
                "strengths": ["Responded to question"],
                "areas_for_improvement": ["Could provide more technical detail"]
            }
    
    def _get_next_question(self, state: InterviewState) -> Optional[Dict]:
        """Get the next question based on current phase"""
        phase_questions = self.questions.get(state.current_phase.value, [])
        
        if not phase_questions:
            return None
            
        # Count questions asked in current phase (excluding greeting)
        question_index = len([msg for msg in state.conversation_history 
                            if msg.phase == state.current_phase and msg.role == "interviewer" and msg.question_id])
        
        if question_index < len(phase_questions):
            return phase_questions[question_index]
        
        return None
    
    def _generate_ai_follow_up(self, question: Dict, response: str, phase: InterviewPhase) -> str:
        """AI-powered follow-up generation"""
        try:
            prompt = f"""
            You are Sarah Chen, an Excel expert conducting a technical interview.
            
            Previous question: {question.get('question', '')}
            Candidate's response: {response}
            Current interview phase: {phase.value}
            
            Generate a brief, encouraging follow-up response (1-2 sentences) that:
            1. Acknowledges their answer
            2. Provides gentle feedback if needed
            3. Moves the conversation forward naturally
            
            Be professional, encouraging, and concise.
            """
            
            ai_response = self._call_ai_model(prompt, self.ai_model_url)
            if ai_response and len(ai_response.strip()) > 10:
                return ai_response.strip()
            else:
                return self._generate_follow_up(question, response, phase)
                
        except Exception as e:
            print(f"Follow-up generation failed: {e}")
            return self._generate_follow_up(question, response, phase)

    def _generate_follow_up(self, question: Dict, response: str, phase: InterviewPhase) -> str:
        """Generate follow-up question (fallback)"""
        # Handle nervous responses with empathy
        if "nervous" in response.lower() or "anxious" in response.lower():
            return "I completely understand! It's totally normal to feel nervous in interviews. Don't worry, we'll take this step by step. Let's start with some basic Excel questions to get you comfortable."
        
        # Handle greeting responses - move to Excel questions immediately
        if "hello" in response.lower() or "hi" in response.lower():
            return "Great to meet you! Let's dive right into some Excel questions. I'll start with some basics and we'll work our way up."
        
        # Handle short responses
        if len(response.strip()) < 10:
            return "No worries! Let's continue with the Excel questions. Take your time with each one."
        
        follow_ups = {
            "greeting": "Perfect! Let's start with some Excel questions. I'll begin with the basics.",
            "warmup": "Good! Can you walk me through how you would approach that?",
            "core_skills": "Excellent! What challenges have you faced with that?",
            "scenario_based": "That's a great approach! How would you handle edge cases?",
            "troubleshooting": "Good thinking! What would you do if that didn't work?"
        }
        return follow_ups.get(phase.value, "That's interesting! Let's continue with the next question.")
    
    def _transition_to_next_phase(self, state: InterviewState) -> InterviewPhase:
        """Determine the next phase based on current progress"""
        # Count questions in current phase
        questions_in_phase = len([msg for msg in state.conversation_history 
                                if msg.phase == state.current_phase and msg.role == "interviewer"])
        
        
        # Question count logic is handled in process_candidate_response method
        
        # Check if we should move to next phase - only if we've asked all questions in current phase
        current_phase_questions = self.questions.get(state.current_phase.value, [])
        if questions_in_phase >= len(current_phase_questions) and current_phase_questions:
            # Simple progression logic
            if state.current_phase == InterviewPhase.GREETING:
                return InterviewPhase.WARMUP
            elif state.current_phase == InterviewPhase.WARMUP:
                return InterviewPhase.CORE_SKILLS
            elif state.current_phase == InterviewPhase.CORE_SKILLS:
                return InterviewPhase.SCENARIO_BASED
            elif state.current_phase == InterviewPhase.SCENARIO_BASED:
                return InterviewPhase.TROUBLESHOOTING
            elif state.current_phase == InterviewPhase.TROUBLESHOOTING:
                return InterviewPhase.WRAPUP
            elif state.current_phase == InterviewPhase.WRAPUP:
                return InterviewPhase.WRAPUP  # Stay in WRAPUP for evaluation
            else:
                return InterviewPhase.WRAPUP  # Go to WRAPUP for evaluation
        
        return state.current_phase

    def _generate_ai_final_report(self, state: InterviewState, avg_score: float, phase_scores: Dict) -> str:
        """Generate final interview report"""
        try:
            # Create conversation summary
            conversation_summary = ""
            for msg in state.conversation_history[-10:]:  # Last 10 messages for context
                if msg.role == "candidate":
                    conversation_summary += f"Candidate: {msg.content[:100]}...\n"
            
            prompt = f"""
            You are Sarah Chen, an Excel expert who just conducted a technical interview.
            
            Interview Summary:
            - Candidate: {state.candidate_name}
            - Overall Score: {avg_score:.1f}/10
            - Questions Answered: {len(state.evaluation_scores)}
            - Performance by Category: {phase_scores}
            
            Recent Conversation:
            {conversation_summary}
            
            Generate a professional, encouraging final report that includes:
            1. Congratulations on completion
            2. Overall performance assessment
            3. Specific strengths identified
            4. Areas for improvement
            5. Next steps and recommendations
            
            Be encouraging but honest. Use emojis appropriately.
            Format as markdown with clear sections.
            """
            
            ai_report = self._call_ai_model(prompt, self.evaluation_model_url)
            if ai_report and len(ai_report.strip()) > 50:
                return ai_report.strip()
            else:
                # Use structured report
                return self._generate_fallback_report(avg_score, phase_scores, len(state.evaluation_scores))
                
        except Exception as e:
            print(f"Report generation failed: {e}")
            return self._generate_fallback_report(avg_score, phase_scores, len(state.evaluation_scores))

    def _generate_fallback_report(self, avg_score: float, phase_scores: Dict, total_questions: int) -> str:
        """Generate structured report"""
        feedback_text = f"**Interview Complete!**\n\n"
        feedback_text += f"**Overall Score: {avg_score:.1f}/10**\n\n"
        feedback_text += f"**Questions Answered: {total_questions}**\n\n"
        
        if phase_scores:
            feedback_text += "**Performance by Category:**\n"
            for phase, scores in phase_scores.items():
                phase_avg = sum(scores) / len(scores) if scores else 0
                phase_name = phase.replace('_', ' ').title()
                feedback_text += f"• {phase_name}: {phase_avg:.1f}/10\n"
                
                # Add specific feedback for each category
                if phase_avg >= 8:
                    feedback_text += f"  Excellent performance in {phase_name.lower()}\n"
                elif phase_avg >= 6:
                    feedback_text += f"  Good performance in {phase_name.lower()}\n"
                else:
                    feedback_text += f"  Needs improvement in {phase_name.lower()}\n"
        
        feedback_text += f"\n**Detailed Assessment:**\n"
        if avg_score >= 8:
            feedback_text += "**Excellent Performance!**\n"
            feedback_text += "• You demonstrate advanced Excel proficiency\n"
            feedback_text += "• Strong technical knowledge and practical application\n"
            feedback_text += "• Ready for senior-level Excel roles\n"
            feedback_text += "• Consider pursuing Excel certification\n"
        elif avg_score >= 6:
            feedback_text += "**Good Performance**\n"
            feedback_text += "• Solid foundation in Excel fundamentals\n"
            feedback_text += "• Shows understanding of core functions\n"
            feedback_text += "• Focus on advanced features (VLOOKUP, PivotTables, macros)\n"
            feedback_text += "• Practice with real-world datasets\n"
        elif avg_score >= 4:
            feedback_text += "**Developing Skills**\n"
            feedback_text += "• Basic Excel knowledge demonstrated\n"
            feedback_text += "• Focus on fundamental functions (SUM, COUNT, AVERAGE)\n"
            feedback_text += "• Practice with Excel tutorials and exercises\n"
            feedback_text += "• Consider Excel beginner courses\n"
        else:
            feedback_text += "**Needs Focused Learning**\n"
            feedback_text += "• Start with Excel basics and fundamentals\n"
            feedback_text += "• Practice with simple formulas and functions\n"
            feedback_text += "• Take structured Excel training courses\n"
            feedback_text += "• Build confidence with hands-on practice\n"
        
        feedback_text += f"\n**Next Steps:**\n"
        if avg_score >= 6:
            feedback_text += "• Practice advanced Excel features\n"
            feedback_text += "• Work with complex datasets\n"
            feedback_text += "• Learn Power Query and Power Pivot\n"
        else:
            feedback_text += "• Complete Excel fundamentals training\n"
            feedback_text += "• Practice with sample datasets\n"
            feedback_text += "• Focus on basic formulas and functions\n"
            
        return feedback_text
    
    def process_candidate_response(self, state: InterviewState, response: str) -> InterviewState:
        """Process candidate's response and generate interviewer's next message"""
        
        # Add candidate's response to conversation
        candidate_message = InterviewMessage(
            role="candidate",
            content=response,
            timestamp=datetime.now(),
            phase=state.current_phase
        )
        state.conversation_history.append(candidate_message)
        
        # Evaluate the response if it's answering a question (store for later, don't show now)
        if state.current_question:
            evaluation = self._ai_evaluate_response(state.current_question, response, state.current_phase)
            state.evaluation_scores.append({
                "question_id": state.current_question["id"],
                "score": evaluation["score"],
                "phase": state.current_phase.value
            })
            # Don't show evaluation immediately - will show at the end
            # Clear current question after processing response
            state.current_question = None
        
        # Ask next question (only if not in WRAPUP phase)
        if state.current_phase != InterviewPhase.WRAPUP:
            # Handle greeting phase transition
            if state.current_phase == InterviewPhase.GREETING:
                state.current_phase = InterviewPhase.WARMUP
            
            # Ask next question
            next_question = self._get_next_question(state)
            if next_question:
                state.current_question = next_question
                question_message = InterviewMessage(
                    role="interviewer",
                    content=next_question["question"],
                    timestamp=datetime.now(),
                    phase=state.current_phase,
                    question_id=next_question["id"]
                )
                state.conversation_history.append(question_message)
            else:
                # If no more questions in current phase, move to next phase
                # This will be handled by the phase transition logic below
                pass
        
        # Check if we should move to next phase (only for non-greeting phases)
        if state.current_phase != InterviewPhase.GREETING:
            # Check if we've asked enough questions to move to WRAPUP
            total_questions = len([msg for msg in state.conversation_history 
                                  if msg.role == "interviewer" and msg.phase != InterviewPhase.GREETING])
            
            if total_questions >= 18:  # Ask at least 18 questions
                # Only move to WRAPUP if user has answered the final question (no pending question)
                if state.current_question is None:
                    state.current_phase = InterviewPhase.WRAPUP
                    next_phase = InterviewPhase.WRAPUP
                else:
                    next_phase = state.current_phase  # Stay in current phase
            else:
                next_phase = self._transition_to_next_phase(state)
                if next_phase != state.current_phase:
                    state.current_phase = next_phase
            
            # If we just moved to WRAPUP, show evaluation
            if state.current_phase == InterviewPhase.WRAPUP:
                # Calculate overall score and detailed feedback
                total_score = sum(score.get('score', 0) for score in state.evaluation_scores)
                avg_score = total_score / len(state.evaluation_scores) if state.evaluation_scores else 0
                
                # Calculate scores by phase
                phase_scores = {}
                for score in state.evaluation_scores:
                    phase = score.get('phase', 'unknown')
                    if phase not in phase_scores:
                        phase_scores[phase] = []
                    phase_scores[phase].append(score.get('score', 0))
                
                # Create AI-powered detailed feedback
                feedback_text = self._generate_ai_final_report(state, avg_score, phase_scores)
                
                wrapup_message = InterviewMessage(
                    role="interviewer",
                    content=feedback_text,
                    timestamp=datetime.now(),
                    phase=InterviewPhase.WRAPUP
                )
                state.conversation_history.append(wrapup_message)
        
        return state

def main():
    st.set_page_config(
        page_title="Excel Mock Interviewer",
        page_icon=None,
        layout="wide"
    )
    
    # Custom CSS for chat interface
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
        color: white;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5em;
        font-weight: bold;
    }
    
    .main-header p {
        margin: 10px 0 0 0;
        font-size: 1.2em;
        opacity: 0.9;
    }
    
    .message {
        margin: 20px 0;
        display: flex;
        align-items: flex-start;
        animation: fadeIn 0.3s ease-in;
    }
    
    .message.interviewer {
        justify-content: flex-start;
    }
    
    .message.candidate {
        justify-content: flex-end;
    }
    
    .message-content {
        max-width: 75%;
        padding: 15px 20px;
        border-radius: 20px;
        word-wrap: break-word;
        word-break: break-word;
        white-space: pre-wrap;
        position: relative;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        line-height: 1.4;
    }
    
    .message.interviewer .message-content {
        background: linear-gradient(135deg, #e3f2fd 0%, #f8f9fa 100%);
        border-bottom-left-radius: 6px;
        margin-left: 15px;
        color: #1a1a1a !important;
        border: 1px solid #e0e0e0;
    }
    
    .message.candidate .message-content {
        background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
        color: white !important;
        border-bottom-right-radius: 6px;
        margin-right: 15px;
        border: 1px solid #0056b3;
    }
    
    .message-sender {
        font-weight: 600;
        font-size: 0.85em;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .message.interviewer .message-sender {
        color: #1976d2 !important;
    }
    
    .message.candidate .message-sender {
        color: #ffffff !important;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .evaluation {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 8px 12px;
        margin-top: 8px;
        font-size: 0.85em;
        color: #000000 !important;
    }
    
    .status-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>Excel Mock Interviewer</h1>
        <p>Welcome to your Excel technical interview with Sarah Chen</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if "agent" not in st.session_state:
        st.session_state.agent = ExcelInterviewAgent()
    
    if "interview_state" not in st.session_state:
        st.session_state.interview_state = None
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Interview Status")
        
        if st.session_state.interview_state:
            state = st.session_state.interview_state
            
            # Status card
            st.markdown(f"""
            <div class="status-card">
                <h4>Interview Details</h4>
                <p><strong>Interviewer:</strong> Sarah Chen</p>
                <p><strong>Candidate:</strong> {state.candidate_name}</p>
                <p><strong>Phase:</strong> {state.current_phase.value.title()}</p>
                <p><strong>Duration:</strong> {_format_duration(state.start_time)}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("End Interview", type="secondary"):
                st.session_state.interview_state = None
                st.rerun()
        else:
            st.markdown("No active interview")
    
    # Main content
    if st.session_state.interview_state is None:
        # Start interview form
        st.markdown("### Start Your Excel Interview")
        
        with st.form("start_interview"):
            candidate_name = st.text_input("Enter your name:", placeholder="Your name here...")
            
            if st.form_submit_button("Start Interview", type="primary"):
                if candidate_name.strip():
                    # Initialize interview state
                    st.session_state.interview_state = InterviewState(
                        candidate_name=candidate_name.strip(),
                    current_phase=InterviewPhase.GREETING,
                    conversation_history=[],
                    start_time=datetime.now()
                )
                    
                    # Add initial greeting (NO question yet)
                    greeting_message = InterviewMessage(
                        role="interviewer",
                        content=f"Hello {candidate_name.strip()}! It's great to meet you. I'm Sarah, and I'll be conducting your Excel technical interview today. We'll go through about 20 Excel questions covering different skill levels. Are you ready to begin?",
                        timestamp=datetime.now(),
                        phase=InterviewPhase.GREETING
                    )
                    st.session_state.interview_state.conversation_history.append(greeting_message)
                    
                    # Move to warmup phase but DON'T ask first question yet
                    st.session_state.interview_state.current_phase = InterviewPhase.WARMUP
                    
                st.rerun()
            else:
                st.error("Please enter your name to start the interview.")
    else:
        # Display conversation
        state = st.session_state.interview_state
        
        st.markdown("### Interview Conversation")
        
        # Create a container for messages with auto-scroll
        messages_container = st.container()
        
        with messages_container:
            # Display messages
            for message in state.conversation_history:
                if message.role == "interviewer":
                    # Check if this is an evaluation message
                    if message.phase == InterviewPhase.WRAPUP and "Interview Complete!" in message.content:
                        # Display evaluation as simple markdown without HTML containers
                        st.markdown("---")
                        st.markdown("### Interview Evaluation")
                        st.markdown(f"**From:** Sarah Chen (Interviewer)")
                        st.markdown("")
                        st.markdown(message.content)
                        st.markdown("---")
                    else:
                        # Display regular message as HTML
                        st.markdown(f"""
                        <div class="message interviewer">
                            <div>
                                <div class="message-sender">Sarah Chen (Interviewer)</div>
                                <div class="message-content">
                                    {message.content}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="message candidate">
                        <div>
                            <div class="message-sender">You</div>
                            <div class="message-content">
                                {message.content}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Add auto-scroll script
        st.markdown("""
        <script>
        // Auto-scroll to bottom of messages
        window.scrollTo(0, document.body.scrollHeight);
        </script>
        """, unsafe_allow_html=True)
        
        # Response input section (only show if not in WRAPUP phase)
        if state.current_phase != InterviewPhase.WRAPUP:
            st.markdown("### Your Response")
            
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Use a dynamic key to clear input after submission
                input_key = f"response_input_{len(state.conversation_history)}"
                response = st.text_area(
                    "Type your response here:",
                    placeholder="Share your thoughts and experience...",
                    height=100,
                    key=input_key
                )
        
            with col2:
                if st.button("Send Response", type="primary", use_container_width=True):
                    if response.strip():
                        # Process the response
                        st.session_state.interview_state = st.session_state.agent.process_candidate_response(
                            state, response.strip()
                        )
                        st.rerun()
                    else:
                        st.error("Please provide an answer before submitting.")

if __name__ == "__main__":
    main()