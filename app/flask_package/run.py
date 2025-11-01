from flask_package import create_app
from database.initdatabase import initdatabase
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)