import uvicorn
from dotenv import load_dotenv
from app.config import port

load_dotenv()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)