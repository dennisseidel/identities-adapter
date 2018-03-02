from connexion.resolver import RestyResolver
import connexion


if __name__ == '__main__':
    app = connexion.FlaskApp(__name__, specification_dir='swagger/')
    # Check Configuring Flask-Cache section for more details
    app.add_api('swagger.yaml', resolver=RestyResolver('api'))
    app.run(port=9090)