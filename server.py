from ocr_api import app  # import the app from ocr-api.py
import os

# Local---
if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(host="0.0.0.0", port=5000, debug=True)

# Live---
# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 10000))  # Use Render's PORT
#     app.run(host="0.0.0.0", port=port)