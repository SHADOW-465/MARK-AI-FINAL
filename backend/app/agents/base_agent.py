"""
Abstract base class for all agents in the EduGrade AI application.

This file defines the interface that all agents must implement.
"""

from abc import ABC, abstractmethod
import logging

class BaseAgent(ABC):
    """
    Abstract base class for all agents.

    All agents should inherit from this class and implement the `process` method.
    """
    def __init__(self, logger_name: str):
        """
        Initializes the agent with a logger.

        Args:
            logger_name: The name of the logger to use.
        """
        self.logger = logging.getLogger(logger_name)

    @abstractmethod
    def process(self, *args, **kwargs):
        """
        Processes the input data.

        This method must be implemented by all agents.
        """
        raise NotImplementedError("Each agent must implement the 'process' method.")

    def _execute_safely(self, func, *args, **kwargs):
        """
        Executes a function with error handling and logging.

        Args:
            func: The function to execute.
            *args: The arguments to pass to the function.
            **kwargs: The keyword arguments to pass to the function.

        Returns:
            The result of the function.
        """
        try:
            self.logger.info(f"Starting execution of {func.__name__}")
            result = func(*args, **kwargs)
            self.logger.info(f"Finished execution of {func.__name__}")
            return result
        except Exception as e:
            self.logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            raise
