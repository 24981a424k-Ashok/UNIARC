from mangum import Mangum
from api.index import app

handler = Mangum(app)
