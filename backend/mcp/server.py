"""
MCP Server for Task Tooling System.

Provides HTTP-based MCP server with task management tools.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from datetime import datetime
import logging

from backend.mcp.config import config
from backend.mcp.logging_config import setup_logging

# Import tool routers
from backend.mcp.tools.add_task import router as add_task_router
from backend.mcp.tools.list_tasks import router as list_tasks_router
from backend.mcp.tools.complete_task import router as complete_task_router
from backend.mcp.tools.delete_task import router as delete_task_router
from backend.mcp.tools.update_task import router as update_task_router

# Setup logging
logger = setup_logging(config.LOG_LEVEL)

# Initialize FastAPI app
app = FastAPI(
    title="MCP Task Tooling Server",
    description="Model Context Protocol server for AI-driven task management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize MCP server on startup."""
    logger.info("Starting MCP Task Tooling Server")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    logger.info(f"Port: {config.MCP_SERVER_PORT}")
    
    # Validate configuration
    try:
        config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration validation failed: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on server shutdown."""
    logger.info("Shutting down MCP Task Tooling Server")


@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "name": "MCP Task Tooling Server",
        "version": "1.0.0",
        "status": "running",
        "environment": config.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns server status and timestamp.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.get("/tools")
async def list_tools():
    """
    List all available MCP tools.
    
    Returns tool names and descriptions.
    """
    tools = [
        {
            "name": "add_task",
            "description": "Create a new task for a user"
        },
        {
            "name": "list_tasks",
            "description": "Retrieve all tasks for a user with optional status filter"
        },
        {
            "name": "complete_task",
            "description": "Mark a task as completed"
        },
        {
            "name": "delete_task",
            "description": "Permanently remove a task"
        },
        {
            "name": "update_task",
            "description": "Modify task attributes (partial update)"
        }
    ]
    
    return {
        "tools": tools,
        "count": len(tools)
    }


# Register tool routers
app.include_router(add_task_router)
app.include_router(list_tasks_router)
app.include_router(complete_task_router)
app.include_router(delete_task_router)
app.include_router(update_task_router)


# Tool endpoints will be added in subsequent phases
# Each tool will be registered at /tools/{tool_name}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.mcp.server:app",
        host=config.MCP_SERVER_HOST,
        port=config.MCP_SERVER_PORT,
        reload=config.ENVIRONMENT == "development"
    )
