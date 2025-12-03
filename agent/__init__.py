# agent/__init__.py 

# Expose the main agent class for easier imports
# CHANGE from .retail_agent to the absolute package path
from agent.retail_agent import RetailAgent 

__all__ = ["RetailAgent"]