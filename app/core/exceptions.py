from fastapi import Request
from fastapi.responses import JSONResponse

# 定義一個專屬於 RentGuard 專案的自訂錯誤類別
class RentGuardException(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

# 定義當系統捕捉到 RentGuardException 時，要如何回傳給前端
async def rentguard_exception_handler(request: Request, exc: RentGuardException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "path": request.url.path # 順便紀錄是哪一支 API 發生錯誤，方便你除錯
        }
    )