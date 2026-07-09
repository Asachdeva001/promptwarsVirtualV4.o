import uvicorn
import os

if __name__ == "__main__":
    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    print(f"Starting StadiumOS FastAPI Backend on port {port} (debug={debug})...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=debug)
