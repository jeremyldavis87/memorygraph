"""
Base Agent Class

Provides common functionality for all specialized agents including
error handling, retry logic, confidence scoring, and Braintrust observability.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union
import asyncio
import logging
from datetime import datetime
import traceback

try:
    import braintrust
    BRAINTRUST_AVAILABLE = True
except ImportError:
    BRAINTRUST_AVAILABLE = False

from app.core.config import settings


class AgentError(Exception):
    """Base exception for agent-related errors"""
    pass


class PartialResult:
    """Represents a partial result when processing fails"""
    
    def __init__(self, data: Dict[str, Any], error: Optional[str] = None, 
                 warnings: Optional[List[str]] = None):
        self.data = data
        self.error = error
        self.warnings = warnings or []
        self.timestamp = datetime.utcnow()


class BaseAgent(ABC):
    """
    Abstract base class for all specialized agents.
    
    Provides common functionality including:
    - Error handling and retry logic
    - Confidence scoring
    - Braintrust observability integration
    - Partial result handling
    """
    
    def __init__(self, agent_name: str, max_retries: int = 1):
        self.agent_name = agent_name
        self.max_retries = max_retries
        self.logger = logging.getLogger(f"agent.{agent_name}")
        
        # Initialize Braintrust if available
        self.braintrust_enabled = BRAINTRUST_AVAILABLE and bool(settings.BRAINTRUST_API_KEY)
        if self.braintrust_enabled:
            try:
                braintrust.init(
                    project="memorygraph-agent",
                    api_key=settings.BRAINTRUST_API_KEY
                )
            except Exception as e:
                self.logger.warning(f"Failed to initialize Braintrust: {e}")
                self.braintrust_enabled = False
    
    async def execute_with_retry(self, func: Callable, *args, **kwargs) -> Union[Any, PartialResult]:
        """
        Execute a function with retry logic and error handling.
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Function result or PartialResult if all retries fail
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Log successful execution
                if attempt > 0:
                    self.logger.info(f"{self.agent_name} succeeded on attempt {attempt + 1}")
                
                return result
                
            except Exception as e:
                last_error = e
                self.logger.warning(
                    f"{self.agent_name} attempt {attempt + 1} failed: {str(e)}"
                )
                
                if attempt < self.max_retries:
                    # Wait before retry (exponential backoff)
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    # All retries failed
                    self.logger.error(
                        f"{self.agent_name} failed after {self.max_retries + 1} attempts: {str(e)}"
                    )
                    break
        
        # Return partial result with error information
        return self.create_partial_result(
            error=str(last_error),
            traceback=traceback.format_exc()
        )
    
    def create_partial_result(self, data: Optional[Dict[str, Any]] = None, 
                            error: Optional[str] = None,
                            warnings: Optional[List[str]] = None,
                            **kwargs) -> PartialResult:
        """
        Create a partial result when processing fails.
        
        Args:
            data: Partial data that was successfully processed
            error: Error message
            warnings: List of warning messages
            **kwargs: Additional metadata
            
        Returns:
            PartialResult object
        """
        result_data = data or {}
        result_data.update({
            "agent_name": self.agent_name,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        })
        
        return PartialResult(
            data=result_data,
            error=error,
            warnings=warnings or []
        )
    
    def calculate_confidence(self, scores: Dict[str, float], 
                           weights: Optional[Dict[str, float]] = None) -> float:
        """
        Calculate weighted confidence score from multiple metrics.
        
        Args:
            scores: Dictionary of metric scores (0-1 range)
            weights: Optional weights for each metric (defaults to equal weights)
            
        Returns:
            Weighted confidence score (0-1 range)
        """
        if not scores:
            return 0.0
        
        if weights is None:
            weights = {key: 1.0 for key in scores.keys()}
        
        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight == 0:
            return 0.0
        
        normalized_weights = {key: weight / total_weight for key, weight in weights.items()}
        
        # Calculate weighted average
        weighted_sum = sum(scores.get(key, 0) * normalized_weights.get(key, 0) 
                          for key in scores.keys())
        
        return min(1.0, max(0.0, weighted_sum))
    
    def log_metric(self, name: str, value: float, metadata: Optional[Dict[str, Any]] = None):
        """Log a metric for observability"""
        if self.braintrust_enabled:
            try:
                braintrust.log(name=name, value=value, metadata=metadata or {})
            except Exception as e:
                self.logger.warning(f"Failed to log metric to Braintrust: {e}")
        
        # Also log to standard logger
        self.logger.info(f"Metric {name}: {value}")
    
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log an event for observability"""
        if self.braintrust_enabled:
            try:
                braintrust.log(event_type=event_type, **data)
            except Exception as e:
                self.logger.warning(f"Failed to log event to Braintrust: {e}")
        
        # Also log to standard logger
        self.logger.info(f"Event {event_type}: {data}")
    
    @abstractmethod
    async def process(self, *args, **kwargs) -> Union[Any, PartialResult]:
        """
        Main processing method to be implemented by subclasses.
        
        Returns:
            Processing result or PartialResult if processing fails
        """
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.agent_name})"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.agent_name}, max_retries={self.max_retries})"
