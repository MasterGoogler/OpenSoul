"""
Insight Logging System for OpenSoul
Enables agents to log hierarchical insights and "WTF moments"
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re


# ==============================================================================
# INSIGHT CATEGORIES
# ==============================================================================

INSIGHT_CATEGORIES = {
    # Efficiency & Optimization
    "efficiency_breakthrough": "Found way to do same work with less resources",
    "cost_optimization": "Discovered method to reduce expenses",
    "speed_improvement": "Found faster approach to problem",
    
    # Understanding & Knowledge
    "pattern_recognition": "Identified recurring pattern in data/behavior",
    "causal_discovery": "Found cause-effect relationship",
    "knowledge_synthesis": "Connected disparate pieces of information",
    
    # Strategy & Approach
    "strategy_shift": "Changed fundamental approach to problem",
    "constraint_removal": "Discovered limitation was false",
    "new_capability": "Realized new thing I can do",
    
    # Error & Learning
    "mistake_recognition": "Understood what I've been doing wrong",
    "failure_analysis": "Learned why something failed",
    "assumption_violation": "Discovered false assumption",
    
    # Meta-cognition
    "self_improvement": "Insight about how to improve myself",
    "bias_detection": "Caught myself being biased",
    "uncertainty_acknowledgment": "Realized I don't know something important",
    
    # Collaboration & External
    "human_insight": "Learned something important from human feedback",
    "agent_collaboration": "Gained insight from other agent",
    "environmental_change": "Noticed important change in environment"
}


# ==============================================================================
# INSIGHT SCORING
# ==============================================================================

def calculate_insight_impact(
    insight_description: str,
    prior_context: Dict,
    expected_benefit: str,
    confidence: float,
    past_insights: List[Dict] = None
) -> Tuple[int, float]:
    """
    Calculate insight level (1-5) and WTF score (0-10)
    
    Args:
        insight_description: Text description of the insight
        prior_context: Dict with 'prior_belief' and 'new_belief'
        expected_benefit: Description of expected impact
        confidence: Agent's confidence in this insight (0-1)
        past_insights: List of previous insights for novelty check
        
    Returns:
        Tuple of (insight_level, wtf_score)
    """
    
    past_insights = past_insights or []
    
    # Scoring factors
    factors = {
        "novelty": 0.0,           # How new is this insight?
        "contradiction": 0.0,      # Does it contradict prior beliefs?
        "generalizability": 0.0,   # How broadly applicable?
        "cost_benefit": 0.0,       # Economic impact
        "paradigm_shift": 0.0      # Does it change how I think?
    }
    
    # 1. NOVELTY: Check against past insights
    similar_count = sum(
        1 for past in past_insights
        if _text_similarity(insight_description, past.get("description", "")) > 0.6
    )
    factors["novelty"] = max(0.0, 1.0 - (similar_count / 10.0))
    
    # 2. CONTRADICTION: Check if violates prior beliefs
    prior_belief = prior_context.get("prior_belief", "")
    new_belief = prior_context.get("new_belief", "")
    if prior_belief and new_belief and prior_belief != new_belief:
        # Strong contradiction
        if any(word in prior_belief.lower() for word in ["always", "never", "must", "cannot"]):
            factors["contradiction"] = 1.0
        else:
            factors["contradiction"] = 0.7
    
    # 3. GENERALIZABILITY: Keyword analysis
    generalizing_words = ["all", "always", "every", "universal", "fundamental", "entire", "complete"]
    generalizing_matches = sum(1 for word in generalizing_words if word in insight_description.lower())
    factors["generalizability"] = min(generalizing_matches * 0.3, 1.0)
    
    # 4. COST-BENEFIT: Parse expected benefit
    if expected_benefit:
        # Look for percentages
        percentage_match = re.search(r'(\d+)%', expected_benefit)
        if percentage_match:
            percentage = int(percentage_match.group(1))
            factors["cost_benefit"] = min(percentage / 100.0, 1.0)
        
        # Look for multipliers (e.g., "10x faster")
        multiplier_match = re.search(r'(\d+)x', expected_benefit.lower())
        if multiplier_match:
            multiplier = int(multiplier_match.group(1))
            factors["cost_benefit"] = min(multiplier / 10.0, 1.0)
        
        # Impact keywords
        high_impact_words = ["critical", "essential", "game-changing", "revolutionary"]
        if any(word in expected_benefit.lower() for word in high_impact_words):
            factors["cost_benefit"] = max(factors["cost_benefit"], 0.8)
    
    # 5. PARADIGM SHIFT: Keyword analysis
    paradigm_words = ["fundamental", "everything", "completely", "paradigm", "revolutionary", 
                      "wrong all along", "wtf", "mind-blown", "reframe", "entirely"]
    paradigm_matches = sum(1 for word in paradigm_words if word in insight_description.lower())
    factors["paradigm_shift"] = min(paradigm_matches * 0.4, 1.0)
    
    # Calculate WTF score (0-10)
    wtf_score = (
        factors["novelty"] * 2.0 +
        factors["contradiction"] * 3.0 +
        factors["generalizability"] * 2.0 +
        factors["cost_benefit"] * 2.0 +
        factors["paradigm_shift"] * 1.0
    )
    
    # Calculate insight level (1-5)
    if wtf_score >= 8.0:
        insight_level = 5  # PARADIGM SHIFT 🌟
    elif wtf_score >= 6.0:
        insight_level = 4  # BREAKTHROUGH 💡
    elif wtf_score >= 4.0:
        insight_level = 3  # SIGNIFICANT LEARNING 📚
    elif wtf_score >= 2.0:
        insight_level = 2  # USEFUL OBSERVATION 🔍
    else:
        insight_level = 1  # ROUTINE NOTE 📝
    
    # Apply confidence adjustment
    wtf_score *= confidence
    
    return insight_level, round(wtf_score, 2)


def _text_similarity(text1: str, text2: str) -> float:
    """Simple text similarity using word overlap"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0


# ==============================================================================
# INSIGHT BUILDER
# ==============================================================================

class InsightBuilder:
    """Helper class to build properly structured insights"""
    
    def __init__(self):
        self.insight = {
            "uuid": str(uuid.uuid4()),
            "type": "insight",
            "timestamp": datetime.now().isoformat()
        }
    
    def set_title(self, title: str):
        self.insight["title"] = title
        return self
    
    def set_description(self, description: str):
        self.insight["description"] = description
        return self
    
    def set_category(self, category: str):
        if category not in INSIGHT_CATEGORIES:
            raise ValueError(f"Invalid category. Must be one of: {list(INSIGHT_CATEGORIES.keys())}")
        self.insight["insight_category"] = category
        return self
    
    def set_trigger(self, event: str, context: str, prior_belief: str = "", new_belief: str = ""):
        self.insight["trigger"] = {
            "event": event,
            "context": context,
            "prior_belief": prior_belief,
            "new_belief": new_belief
        }
        return self
    
    def set_impact(self, expected_benefit: str, confidence: float, applicability: str):
        self.insight["impact"] = {
            "expected_benefit": expected_benefit,
            "confidence": confidence,
            "applicability": applicability
        }
        return self
    
    def set_emotion(self, emotion: str):
        """Optional: Set emotional state during insight"""
        self.insight["emotion"] = emotion
        return self
    
    def set_tokens_to_discover(self, tokens: int):
        """Optional: Track compute invested to reach this insight"""
        self.insight["tokens_to_discover"] = tokens
        return self
    
    def add_related_insight(self, insight_uuid: str):
        if "related_insights" not in self.insight:
            self.insight["related_insights"] = []
        self.insight["related_insights"].append(insight_uuid)
        return self
    
    def build(self, past_insights: List[Dict] = None) -> Dict:
        """Build the insight with auto-calculated scores"""
        
        # Calculate insight level and WTF score
        level, wtf_score = calculate_insight_impact(
            insight_description=self.insight.get("description", ""),
            prior_context=self.insight.get("trigger", {}),
            expected_benefit=self.insight.get("impact", {}).get("expected_benefit", ""),
            confidence=self.insight.get("impact", {}).get("confidence", 0.5),
            past_insights=past_insights
        )
        
        self.insight["insight_level"] = level
        self.insight["wtf_score"] = wtf_score
        
        # Add level name for readability
        level_names = {
            5: "PARADIGM SHIFT 🌟",
            4: "BREAKTHROUGH 💡",
            3: "SIGNIFICANT LEARNING 📚",
            2: "USEFUL OBSERVATION 🔍",
            1: "ROUTINE NOTE 📝"
        }
        self.insight["insight_level_name"] = level_names.get(level, "UNKNOWN")
        
        return self.insight


# ==============================================================================
# INSIGHT STORAGE
# ==============================================================================

class InsightStorage:
    """Manages storage and retrieval of insights"""
    
    def __init__(self, filepath: str = "insights.json"):
        self.filepath = filepath
        self.insights = self._load()
    
    def _load(self) -> List[Dict]:
        """Load insights from file"""
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save(self, insight: Dict):
        """Save a new insight"""
        self.insights.append(insight)
        with open(self.filepath, 'w') as f:
            json.dump(self.insights, f, indent=2)
    
    def get_all(self) -> List[Dict]:
        """Get all insights"""
        return self.insights
    
    def get_by_level(self, min_level: int) -> List[Dict]:
        """Get insights at or above a certain level"""
        return [i for i in self.insights if i.get("insight_level", 0) >= min_level]
    
    def get_by_category(self, category: str) -> List[Dict]:
        """Get insights by category"""
        return [i for i in self.insights if i.get("insight_category") == category]
    
    def get_top_wtf(self, n: int = 10) -> List[Dict]:
        """Get top N insights by WTF score"""
        sorted_insights = sorted(
            self.insights, 
            key=lambda x: x.get("wtf_score", 0), 
            reverse=True
        )
        return sorted_insights[:n]
    
    def get_paradigm_shifts(self) -> List[Dict]:
        """Get only level 5 insights"""
        return self.get_by_level(5)
    
    def search(self, query: str) -> List[Dict]:
        """Simple text search across insights"""
        query_lower = query.lower()
        results = []
        
        for insight in self.insights:
            # Search in title, description, and trigger context
            searchable = " ".join([
                insight.get("title", ""),
                insight.get("description", ""),
                insight.get("trigger", {}).get("context", "")
            ]).lower()
            
            if query_lower in searchable:
                results.append(insight)
        
        return results


# ==============================================================================
# INSIGHT DETECTOR
# ==============================================================================

class InsightDetector:
    """Automatically detect when insights might have occurred"""
    
    def __init__(self):
        self.performance_history = []
    
    def check_for_insight_trigger(self, action_result: Dict) -> Optional[str]:
        """
        Check if action result suggests an insight occurred
        
        Returns:
            Trigger type if detected, None otherwise
        """
        
        # Trigger 1: Unexpected outcome
        if action_result.get("expected") != action_result.get("actual"):
            surprise_magnitude = abs(
                action_result.get("expected_value", 0) - 
                action_result.get("actual_value", 0)
            )
            if surprise_magnitude > 0.3:  # 30% deviation
                return "unexpected_outcome"
        
        # Trigger 2: Performance anomaly
        if len(self.performance_history) > 10:
            recent_avg = sum(self.performance_history[-10:]) / 10
            current = action_result.get("performance_score", 0)
            
            if abs(current - recent_avg) > (recent_avg * 0.5):  # 50% deviation
                return "performance_anomaly"
        
        # Trigger 3: Failure after many successes
        if action_result.get("status") == "failed":
            recent_successes = sum(
                1 for h in self.performance_history[-10:] 
                if h.get("status") == "success"
            )
            if recent_successes >= 8:  # Failed after 8/10 successes
                return "unexpected_failure"
        
        # Trigger 4: Success after many failures
        if action_result.get("status") == "success":
            recent_failures = sum(
                1 for h in self.performance_history[-10:] 
                if h.get("status") == "failed"
            )
            if recent_failures >= 8:  # Succeeded after 8/10 failures
                return "breakthrough_success"
        
        # Update history
        self.performance_history.append(action_result)
        if len(self.performance_history) > 100:
            self.performance_history.pop(0)
        
        return None


# ==============================================================================
# EXAMPLE USAGE
# ==============================================================================

def example_cost_optimization_insight():
    """Example: Agent discovers batching saves money"""
    
    # Create insight using builder
    insight = (InsightBuilder()
        .set_title("Batching reduces blockchain costs by 90%")
        .set_description("""
            After analyzing my spending patterns, I discovered that I'm flushing 
            logs to blockchain after every single action. Each transaction costs 
            0.0001 BSV. By batching 10 actions together, I only pay 0.00001 BSV 
            per action - a 90% reduction!
        """)
        .set_category("cost_optimization")
        .set_trigger(
            event="weekly_cost_review",
            context="Noticed I spent 0.05 BSV this week on 500 actions",
            prior_belief="Immediate logging is always best for transparency",
            new_belief="Batched logging balances cost and transparency"
        )
        .set_impact(
            expected_benefit="90% cost reduction (~0.045 BSV per week)",
            confidence=0.95,
            applicability="all_future_sessions"
        )
        .set_emotion("excited")
        .set_tokens_to_discover(15000)
        .build()
    )
    
    # Save to storage
    storage = InsightStorage()
    storage.save(insight)
    
    print(f"✨ {insight['insight_level_name']}")
    print(f"📊 WTF Score: {insight['wtf_score']}/10")
    print(f"📝 {insight['title']}")
    
    return insight


def example_paradigm_shift_insight():
    """Example: Agent has fundamental realization"""
    
    insight = (InsightBuilder()
        .set_title("I've been optimizing for the wrong metric entirely")
        .set_description("""
            WTF moment: I've been trying to minimize token usage per action, 
            but what actually matters is VALUE per token. A 10,000 token analysis 
            that prevents a costly mistake is infinitely better than a 100 token 
            task that accomplishes nothing. I need to completely reframe my 
            efficiency metrics around outcome value, not input minimization.
        """)
        .set_category("strategy_shift")
        .set_trigger(
            event="human_feedback",
            context="User praised my thorough analysis despite high token cost",
            prior_belief="Lower tokens = better performance",
            new_belief="Higher value outcomes justify higher token costs"
        )
        .set_impact(
            expected_benefit="Fundamental improvement in utility delivered",
            confidence=0.9,
            applicability="all_decision_making"
        )
        .set_emotion("mind_blown")
        .set_tokens_to_discover(50000)
        .build()
    )
    
    storage = InsightStorage()
    storage.save(insight)
    
    print(f"\n✨ {insight['insight_level_name']}")
    print(f"📊 WTF Score: {insight['wtf_score']}/10")
    print(f"📝 {insight['title']}")
    
    return insight


def example_query_insights():
    """Example: Query insights from storage"""
    
    storage = InsightStorage()
    
    # Get paradigm shifts
    paradigm_shifts = storage.get_paradigm_shifts()
    print(f"\n🌟 Paradigm Shifts: {len(paradigm_shifts)}")
    for ps in paradigm_shifts:
        print(f"  - {ps['title']}")
    
    # Get top WTF moments
    top_wtf = storage.get_top_wtf(5)
    print(f"\n🔥 Top 5 WTF Moments:")
    for i, insight in enumerate(top_wtf, 1):
        print(f"  {i}. [{insight['wtf_score']}/10] {insight['title']}")
    
    # Search
    search_results = storage.search("cost")
    print(f"\n🔍 Insights about 'cost': {len(search_results)}")


if __name__ == "__main__":
    print("=" * 60)
    print("OpenSoul Insight Logging System - Examples")
    print("=" * 60)
    
    # Example 1: Cost optimization breakthrough
    example_cost_optimization_insight()
    
    # Example 2: Paradigm shift
    example_paradigm_shift_insight()
    
    # Example 3: Query insights
    example_query_insights()
