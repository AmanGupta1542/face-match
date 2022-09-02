from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer 

from ..user.dependencies.common import get_db
from .dependencies import common as CDepends
from .routers import users

auth_admin = HTTPBearer()

app = FastAPI(dependencies=[Depends(get_db), Depends(CDepends.get_active_user)])

app.include_router(users.router)

@app.get('/')
def index():
    return {'status': 'success'}