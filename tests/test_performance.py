"""
Performance benchmark tests for FAIX AI Chatbot.

This module provides performance testing and benchmarking for:
- Conversation processing
- Intent detection
- LLM response times
- Context retrieval
"""

import time
import logging
import statistics
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Import backend modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.chatbot.conversation_manager import (
    process_conversation,
    ConversationProcessor,
    ConversationContext,
    IntentDetector,
)
from backend.llm.llm_client import get_llm_client, LLMError


@dataclass
class BenchmarkResult:
    """Container for benchmark results."""
    operation: str
    iterations: int
    avg_time: float
    min_time: float
    max_time: float
    std_dev: float
    total_time: float
    success_rate: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceBenchmark:
    """Performance benchmarking suite for FAIX AI Chatbot."""

    def __init__(self, warmup_iterations: int = 3):
        self.warmup_iterations = warmup_iterations
        self.results: List[BenchmarkResult] = []
        logger.info("PerformanceBenchmark initialized")

    def warmup(self) -> None:
        """Run warmup iterations to stabilize performance."""
        logger.info(f"Running {self.warmup_iterations} warmup iterations...")
        for i in range(self.warmup_iterations):
            try:
                # Warmup with a simple conversation
                context = {}
                process_conversation("Hello", context)
                process_conversation("I want to register", context)
                logger.debug(f"Warmup iteration {i+1}/{self.warmup_iterations} completed")
            except Exception as e:
                logger.warning(f"Warmup iteration {i+1} failed: {e}")
        logger.info("Warmup completed")

    def benchmark_intent_detection(self, iterations: int = 100) -> BenchmarkResult:
        """Benchmark intent detection performance."""
        logger.info(f"Benchmarking intent detection ({iterations} iterations)...")
        
        test_messages = [
            "I want to register for courses",
            "What is the contact email?",
            "When does registration open?",
            "How do I contact the office?",
            "Thank you for your help",
            "Hello, I need assistance",
            "What are the course requirements?",
            "Can I get the phone number?",
            "Goodbye and thanks",
            "Hi, how are you?",
        ]
        
        times = []
        successes = 0
        
        start_total = time.time()
        
        for i in range(iterations):
            try:
                msg = test_messages[i % len(test_messages)]
                start = time.time()
                intent = IntentDetector.detect(msg)
                end = time.time()
                
                times.append(end - start)
                if intent is not None:
                    successes += 1
                    
            except Exception as e:
                logger.error(f"Intent detection failed on iteration {i}: {e}")
        
        total_time = time.time() - start_total
        
        result = BenchmarkResult(
            operation="intent_detection",
            iterations=iterations,
            avg_time=statistics.mean(times) if times else 0,
            min_time=min(times) if times else 0,
            max_time=max(times) if times else 0,
            std_dev=statistics.stdev(times) if len(times) > 1 else 0,
            total_time=total_time,
            success_rate=successes / iterations if iterations > 0 else 0,
            metadata={"test_messages": len(test_messages)},
        )
        
        self.results.append(result)
        logger.info(f"Intent detection benchmark: {result}")
        return result

    def benchmark_conversation_processing(self, iterations: int = 50) -> BenchmarkResult:
        """Benchmark full conversation processing."""
        logger.info(f"Benchmarking conversation processing ({iterations} iterations)...")
        
        conversation_flows = [
            [
                ("Hello", {}),
                ("I want to register", {}),
                ("When is registration open?", {}),
                ("How do I do it?", {}),
                ("Thank you", {}),
            ],
            [
                ("Hello", {}),
                ("Can I contact the office?", {}),
                ("What's their email?", {}),
                ("Bye", {}),
            ],
            [
                ("Hi", {}),
                ("I have a question", {}),
                ("Tell me more", {}),
            ],
        ]
        
        times = []
        successes = 0
        
        start_total = time.time()
        
        for i in range(iterations):
            try:
                flow = conversation_flows[i % len(conversation_flows)]
                flow_start = time.time()
                
                context = {}
                for msg, _ in flow:
                    start = time.time()
                    _, context = process_conversation(msg, context)
                    end = time.time()
                    times.append(end - start)
                
                flow_end = time.time()
                if flow_end - flow_start > 0:
                    successes += 1
                    
            except Exception as e:
                logger.error(f"Conversation processing failed on iteration {i}: {e}")
        
        total_time = time.time() - start_total
        
        result = BenchmarkResult(
            operation="conversation_processing",
            iterations=iterations,
            avg_time=statistics.mean(times) if times else 0,
            min_time=min(times) if times else 0,
            max_time=max(times) if times else 0,
            std_dev=statistics.stdev(times) if len(times) > 1 else 0,
            total_time=total_time,
            success_rate=successes / iterations if iterations > 0 else 0,
            metadata={"conversation_flows": len(conversation_flows)},
        )
        
        self.results.append(result)
        logger.info(f"Conversation processing benchmark: {result}")
        return result

    def benchmark_context_management(self, iterations: int = 100) -> BenchmarkResult:
        """Benchmark context management performance."""
        logger.info(f"Benchmarking context management ({iterations} iterations)...")
        
        test_contexts = [
            {},
            {"current_topic": "registration", "history": [{"user": "Hello"}]},
            {"current_topic": "contact", "history": [{"user": "Hi"}, {"bot": "Hello!"}]},
            {"current_topic": "farewell", "history": [{"user": "Thanks"}]},
        ]
        
        test_messages = [
            "I want to register",
            "What's the email?",
            "When is it open?",
            "How do I do it?",
        ]
        
        times = []
        successes = 0
        
        start_total = time.time()
        
        for i in range(iterations):
            try:
                ctx = test_contexts[i % len(test_contexts)]
                msg = test_messages[i % len(test_messages)]
                
                start = time.time()
                # Test context conversion
                conv_ctx = ConversationContext.from_dict(ctx) if isinstance(ctx, dict) else ctx
                # Test context update
                conv_ctx.history.append({"user": msg})
                # Test context serialization
                _ = conv_ctx.to_dict()
                end = time.time()
                
                times.append(end - start)
                successes += 1
                    
            except Exception as e:
                logger.error(f"Context management failed on iteration {i}: {e}")
        
        total_time = time.time() - start_total
        
        result = BenchmarkResult(
            operation="context_management",
            iterations=iterations,
            avg_time=statistics.mean(times) if times else 0,
            min_time=min(times) if times else 0,
            max_time=max(times) if times else 0,
            std_dev=statistics.stdev(times) if len(times) > 1 else 0,
            total_time=total_time,
            success_rate=successes / iterations if iterations > 0 else 0,
            metadata={"test_contexts": len(test_contexts)},
        )
        
        self.results.append(result)
        logger.info(f"Context management benchmark: {result}")
        return result

    def benchmark_llm_client(self, iterations: int = 10) -> BenchmarkResult:
        """Benchmark LLM client performance (if available)."""
        logger.info(f"Benchmarking LLM client ({iterations} iterations)...")
        
        try:
            client = get_llm_client()
            
            # Check if LLM is available
            if not client.enabled:
                logger.warning("LLM is disabled, skipping LLM benchmark")
                return BenchmarkResult(
                    operation="llm_client",
                    iterations=0,
                    avg_time=0,
                    min_time=0,
                    max_time=0,
                    std_dev=0,
                    total_time=0,
                    success_rate=0,
                    metadata={"status": "disabled"},
                )
            
            # Test messages
            test_messages = [
                [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "Hello"}],
                [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is 2+2?"}],
            ]
            
            times = []
            successes = 0
            
            start_total = time.time()
            
            for i in range(iterations):
                try:
                    messages = test_messages[i % len(test_messages)]
                    
                    start = time.time()
                    response = client.chat(messages, temperature=0.3, max_tokens=50)
                    end = time.time()
                    
                    times.append(end - start)
                    if response and response.content:
                        successes += 1
                        
                except LLMError as e:
                    logger.warning(f"LLM request failed on iteration {i}: {e}")
                except Exception as e:
                    logger.error(f"LLM benchmark failed on iteration {i}: {e}")
            
            total_time = time.time() - start_total
            
            result = BenchmarkResult(
                operation="llm_client",
                iterations=iterations,
                avg_time=statistics.mean(times) if times else 0,
                min_time=min(times) if times else 0,
                max_time=max(times) if times else 0,
                std_dev=statistics.stdev(times) if len(times) > 1 else 0,
                total_time=total_time,
                success_rate=successes / iterations if iterations > 0 else 0,
                metadata={"status": "enabled", "model": client.model},
            )
            
            self.results.append(result)
            logger.info(f"LLM client benchmark: {result}")
            return result
            
        except Exception as e:
            logger.error(f"LLM client benchmark failed: {e}")
            return BenchmarkResult(
                operation="llm_client",
                iterations=0,
                avg_time=0,
                min_time=0,
                max_time=0,
                std_dev=0,
                total_time=0,
                success_rate=0,
                metadata={"status": "error", "error": str(e)},
            )

    def run_all_benchmarks(self) -> None:
        """Run all benchmark tests."""
        logger.info("=" * 70)
        logger.info("Starting FAIX AI Chatbot Performance Benchmarks")
        logger.info("=" * 70)
        
        # Warmup
        self.warmup()
        
        # Run benchmarks
        self.benchmark_intent_detection(iterations=100)
        self.benchmark_conversation_processing(iterations=50)
        self.benchmark_context_management(iterations=100)
        self.benchmark_llm_client(iterations=10)
        
        # Print summary
        self.print_summary()

    def print_summary(self) -> None:
        """Print benchmark summary."""
        logger.info("=" * 70)
        logger.info("BENCHMARK SUMMARY")
        logger.info("=" * 70)
        
        if not self.results:
            logger.warning("No benchmark results to display")
            return
        
        for result in self.results:
            logger.info(f"\nOperation: {result.operation}")
            logger.info(f"  Iterations: {result.iterations}")
            logger.info(f"  Avg Time: {result.avg_time:.6f}s")
            logger.info(f"  Min Time: {result.min_time:.6f}s")
            logger.info(f"  Max Time: {result.max_time:.6f}s")
            logger.info(f"  Std Dev: {result.std_dev:.6f}s")
            logger.info(f"  Total Time: {result.total_time:.3f}s")
            logger.info(f"  Success Rate: {result.success_rate:.1%}")
            if result.metadata:
                logger.info(f"  Metadata: {result.metadata}")
        
        logger.info("=" * 70)

    def get_summary_report(self) -> Dict[str, Any]:
        """Get benchmark summary as a dictionary."""
        return {
            "total_benchmarks": len(self.results),
            "results": [
                {
                    "operation": r.operation,
                    "iterations": r.iterations,
                    "avg_time": r.avg_time,
                    "min_time": r.min_time,
                    "max_time": r.max_time,
                    "std_dev": r.std_dev,
                    "total_time": r.total_time,
                    "success_rate": r.success_rate,
                    "metadata": r.metadata,
                }
                for r in self.results
            ],
        }


def main():
    """Main entry point for performance benchmarking."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run performance benchmarks for FAIX AI Chatbot")
    parser.add_argument("--iterations", type=int, default=50, help="Number of iterations for each benchmark")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level")
    parser.add_argument("--log-file", type=str, help="Log file path")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = getattr(logging, args.log_level)
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    
    if args.log_file:
        file_handler = logging.FileHandler(args.log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        logging.getLogger().addHandler(file_handler)
    
    # Run benchmarks
    benchmark = PerformanceBenchmark()
    benchmark.run_all_benchmarks()


if __name__ == "__main__":
    main()
