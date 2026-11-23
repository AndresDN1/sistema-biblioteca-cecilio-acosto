from dotenv import load_dotenv

import src

if __name__ == "__main__":
    load_dotenv()
    app = src.initialize_app()
    app.logger.info("Attempting to run app at localhost:5000")
    app.run()
