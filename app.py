from connexion.resolver import RestyResolver
import connexion
from flask_cors import CORS



if __name__ == '__main__':
    app = connexion.FlaskApp(__name__, specification_dir='swagger/')
    
    # add CORS support
    CORS(app.app)
    
    app.add_api('swagger.yaml', resolver=RestyResolver('api'))
    app.run(port=9090)