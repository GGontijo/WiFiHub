from fastapi import FastAPI
import uvicorn
import routes.routes as routes

class API():
    
    def __init__(self) -> None:
        self.api = FastAPI()
        self.api.include_router(routes.router)
        uvicorn.run(self.api)

if __name__ == '__main__':
    api = API()
