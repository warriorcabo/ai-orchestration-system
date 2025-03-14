# stress_test.py

import os
import sys
import time
import json
import logging
import datetime
import requests
import concurrent.futures
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Test configuration
BASE_URL = "https://ai-orch-warrior-5ff152a0e1f8.herokuapp.com"
CONCURRENT_REQUESTS = 5  # Number of concurrent requests
TOTAL_REQUESTS = 20      # Total number of requests to make
DELAY_BETWEEN_BATCHES = 2  # Seconds between batches
TEST_QUERIES = [
    "What is machine learning?",
    "Explain the difference between supervised and unsupervised learning",
    "Give me a simple Python example of data visualization",
    "What are the key components of an AI system?",
    "How does natural language processing work?"
]

def send_request(query_id, query):
    """Send a request to the orchestration system"""
    start_time = time.time()
    try:
        url = f"{BASE_URL}/api/process"
        payload = {
            "user_id": f"stress_test_user_{query_id}",
            "message": query
        }
        
        logger.info(f"[{query_id}] Sending request: {query[:30]}...")
        response = requests.post(url, json=payload, timeout=60)
        
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            logger.info(f"[{query_id}] Request successful ({elapsed_time:.2f}s)")
            return {
                "query_id": query_id,
                "status": "success",
                "elapsed_time": elapsed_time,
                "status_code": response.status_code,
                "response_size": len(response.text)
            }
        else:
            logger.error(f"[{query_id}] Request failed: {response.status_code}")
            return {
                "query_id": query_id,
                "status": "error",
                "elapsed_time": elapsed_time,
                "status_code": response.status_code,
                "response": response.text[:100]
            }
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"[{query_id}] Exception: {str(e)}")
        return {
            "query_id": query_id,
            "status": "exception",
            "elapsed_time": elapsed_time,
            "error": str(e)
        }

def run_stress_test():
    """Run the stress test"""
    logger.info(f"Starting stress test with {TOTAL_REQUESTS} total requests, {CONCURRENT_REQUESTS} concurrent")
    
    results = []
    request_count = 0
    
    # Create a timestamp for this test run
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
        # Submit batches of requests
        while request_count < TOTAL_REQUESTS:
            batch = []
            batch_size = min(CONCURRENT_REQUESTS, TOTAL_REQUESTS - request_count)
            
            logger.info(f"Submitting batch of {batch_size} requests")
            
            for i in range(batch_size):
                query = TEST_QUERIES[request_count % len(TEST_QUERIES)]
                batch.append(
                    executor.submit(send_request, f"{timestamp}_{request_count}", query)
                )
                request_count += 1
            
            # Collect results from this batch
            for future in concurrent.futures.as_completed(batch):
                results.append(future.result())
            
            # Delay between batches
            if request_count < TOTAL_REQUESTS:
                logger.info(f"Waiting {DELAY_BETWEEN_BATCHES}s before next batch...")
                time.sleep(DELAY_BETWEEN_BATCHES)
    
    # Calculate statistics
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "error"]
    exceptions = [r for r in results if r["status"] == "exception"]
    
    response_times = [r["elapsed_time"] for r in results if "elapsed_time" in r]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    max_response_time = max(response_times) if response_times else 0
    min_response_time = min(response_times) if response_times else 0
    
    # Print summary
    logger.info("\n===== STRESS TEST RESULTS =====")
    logger.info(f"Total requests: {len(results)}")
    logger.info(f"Successful: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    logger.info(f"Failed: {len(failed)} ({len(failed)/len(results)*100:.1f}%)")
    logger.info(f"Exceptions: {len(exceptions)} ({len(exceptions)/len(results)*100:.1f}%)")
    logger.info(f"Average response time: {avg_response_time:.2f}s")
    logger.info(f"Min response time: {min_response_time:.2f}s")
    logger.info(f"Max response time: {max_response_time:.2f}s")
    
    # Save results to file
    results_file = f"stress_test_results_{timestamp}.json"
    with open(results_file, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "config": {
                "total_requests": TOTAL_REQUESTS,
                "concurrent_requests": CONCURRENT_REQUESTS,
                "delay_between_batches": DELAY_BETWEEN_BATCHES
            },
            "results": results,
            "summary": {
                "total": len(results),
                "successful": len(successful),
                "failed": len(failed),
                "exceptions": len(exceptions),
                "avg_response_time": avg_response_time,
                "min_response_time": min_response_time,
                "max_response_time": max_response_time
            }
        }, f, indent=2)
    
    logger.info(f"Results saved to {results_file}")

if __name__ == "__main__":
    run_stress_test()
