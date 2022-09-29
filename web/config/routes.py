from web.resources.auth import ApiSignUp, ApiSignIn, ApiForgotPassword, ApiResetPassword
from web.resources.user import ApiUserPassword, ApiUsers, ApiUser
from web.resources.tictactoe_game import ApiTictactoeGames, ApiTictactoeGame
from web.resources.tictactoe_move import ApiTictactoeMoves, ApiTictactoeMove
from app import app

def init_routes(api):
    api.add_resource(ApiSignUp, "/api/auth/signup")
    api.add_resource(ApiSignIn, "/api/auth/signin")
    api.add_resource(ApiForgotPassword, "/api/auth/forgot")
    api.add_resource(ApiResetPassword, "/api/auth/reset")

    api.add_resource(ApiUsers, "/api/users")
    api.add_resource(ApiUser, "/api/user")
    api.add_resource(ApiUserPassword, "/api/user/password")

    api.add_resource(ApiTictactoeGames, "/api/tgames")
    api.add_resource(ApiTictactoeGame, "/api/tgame")

    api.add_resource(ApiTictactoeMoves, "/api/tmoves")
    api.add_resource(ApiTictactoeMove, "/api/tmove")

@app.route('/')
@app.route("/index")
def index():
    return "X"