from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import time
from loguru import logger
from sqlalchemy import event
from sqlalchemy.engine import Engine
import threading

local = threading.local()

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    if not hasattr(local, "query_start_time"):
        local.query_start_time = {}
    
    local.query_start_time[threading.get_ident()] = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - local.query_start_time[threading.get_ident()]
    
    # Log slow queries (more than 100ms)
    if total > 0.1:
        logger.warning(
            f"Slow Query ({total:.2f}s): {statement}\nParameters: {parameters}"
        )

class DBProfilerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Initialize query counters
        if not hasattr(local, "query_count"):
            local.query_count = {}
        
        thread_id = threading.get_ident()
        local.query_count[thread_id] = 0
        
        response = await call_next(request)
        
        # Log request statistics
        process_time = time.time() - start_time
        logger.info(
            f"Path: {request.url.path} | "
            f"Queries: {local.query_count.get(thread_id, 0)} | "
            f"Time: {process_time:.2f}s"
        )
        
        return response 