from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .errors import AppError
from .routers.game import router as game_router
from .routers.player_game import router as player_router

app = FastAPI(title="RAWR Escape Game")
app.include_router(game_router)
app.include_router(player_router)


@app.exception_handler(AppError)
async def handle_app_error(request: Request, error: AppError):
    return JSONResponse(status_code=error.status_code, content={"detail": error.detail})


if __name__ == "__main__":
    from .cli import play_game

    play_game()
