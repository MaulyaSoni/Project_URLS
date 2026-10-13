# app/middleware.py
import time
import logging
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("api_logger")

async def unified_logging_and_exception_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    
    client_host = request.client.host if request.client else "unknown"
    method = request.method
    url = request.url.path
    query_params = dict(request.query_params)
    
    logger.info(f"Incoming: {method} {url} | Params: {query_params} | Client: {client_host}")
    
    try:
        response = await call_next(request)
        process_time = (time.perf_counter() - start_time) * 1000
        logger.info(f"Success: {method} {url} | Status: {response.status_code} | Duration: {process_time:.2f}ms")
        
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        return response

    except Exception as e:
        process_time = (time.perf_counter() - start_time) * 1000
        error_traceback = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        
        logger.error(
            f"Failure: {method} {url} | Duration: {process_time:.2f}ms\n"
            f"Exception: {str(e)}\n"
            f"Traceback:\n{error_traceback}"
        )
        
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred.", "type": type(e).__name__}
        )
