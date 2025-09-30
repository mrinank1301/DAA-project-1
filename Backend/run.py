#!/usr/bin/env python3
"""
FlavorGraph startup script.
This script provides an easy way to start the FlavorGraph server with different configurations.
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path


def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import networkx
        import numpy
        import pandas
        import sklearn
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False


def run_tests():
    """Run the system tests."""
    print("Running FlavorGraph system tests...")
    try:
        import asyncio
        from test_system import test_system, test_sample_request
        
        # Run the async test
        asyncio.run(test_system())
        test_sample_request()
        return True
    except Exception as e:
        print(f"Tests failed: {str(e)}")
        return False


def start_server(host="127.0.0.1", port=8000, reload=True, log_level="info"):
    """Start the FlavorGraph server."""
    print(f"Starting FlavorGraph server on {host}:{port}")
    print(f"Reload mode: {'ON' if reload else 'OFF'}")
    print(f"Log level: {log_level}")
    print("-" * 50)
    
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Failed to start server: {str(e)}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="FlavorGraph: Intelligent Recipe Navigator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                          # Start server with defaults
  python run.py --host 0.0.0.0          # Allow external connections
  python run.py --port 8080             # Use different port
  python run.py --no-reload             # Disable auto-reload
  python run.py --test                  # Run system tests
  python run.py --production            # Production mode (no reload, warning level)
        """
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)"
    )
    
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable auto-reload on code changes"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        default="info",
        help="Log level (default: info)"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run system tests instead of starting server"
    )
    
    parser.add_argument(
        "--production",
        action="store_true",
        help="Run in production mode (no reload, warning level, bind to 0.0.0.0)"
    )
    
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check if all dependencies are installed"
    )
    
    args = parser.parse_args()
    
    print("🍳 FlavorGraph: Intelligent Recipe Navigator")
    print("=" * 50)
    
    # Check dependencies first
    if args.check_deps:
        check_dependencies()
        return
    
    if not check_dependencies():
        sys.exit(1)
    
    # Run tests
    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)
    
    # Configure for production
    if args.production:
        args.host = "0.0.0.0"
        args.no_reload = True
        args.log_level = "warning"
        print("🚀 Production mode enabled")
    
    # Start server
    start_server(
        host=args.host,
        port=args.port,
        reload=not args.no_reload,
        log_level=args.log_level
    )


if __name__ == "__main__":
    main() 