import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='\n %(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AgenticWorkflow")

decision_log = []

def log_decision(step : str,reasoning : str,tool_used : str | None):
    """Log agent decisions for transparency"""
    decision = {
        "timestamp": datetime.now().isoformat(),
        "step": step,
        "reasoning": reasoning,
        "tool_used": tool_used
    }
    decision_log.append(decision)
    logger.info(f"Decision logged: {step} - {reasoning}")