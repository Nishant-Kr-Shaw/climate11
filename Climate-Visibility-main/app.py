from flask import Flask, render_template, jsonify, request, send_file
from src.exception import VisibilityException
from src.logger import logging as lg
import os,sys

# pipelines are imported lazily inside route handlers to avoid heavy imports at startup

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/train")
def train_route():
    try:
        try:
            from src.pipeline.training_pipeline import TraininingPipeline
        except Exception as e:
            return jsonify({"error": "Training dependencies not installed", "detail": str(e)}), 500

        train_pipeline = TraininingPipeline()
        train_pipeline.run_pipeline()

        return jsonify("Training Successfull.")

    except Exception as e:
        raise VisibilityException(e,sys)
    

@app.route("/predict", methods = ['POST', 'GET'])
def predict():
    try:
        if request.method == "POST":
            try:
                from src.pipeline.prediction_pipeline import PredictionPipeline
            except Exception as e:
                return jsonify({"error": "Prediction dependencies not installed", "detail": str(e)}), 500

            prediction_pipeline = PredictionPipeline(request=request)
            try:
                predicted_visibility = prediction_pipeline.run_pipeline()
            except VisibilityException as ve:
                # Render UI with actionable guidance
                return render_template("result.html", prediction="N/A", error=str(ve))
            print(predicted_visibility)

            try:
                pred_value = float(predicted_visibility)
                return render_template("result.html", prediction= f"{pred_value :.3f}")
            except Exception:
                try:
                    return render_template("result.html", prediction= f"{predicted_visibility[0] :.3f}")
                except Exception:
                    return render_template("result.html", prediction=str(predicted_visibility))
        else:
            return render_template("predict.html")
    except Exception as e:
        raise VisibilityException(e,sys)

    


# if __name__ == "__main__":
#     print("Starting the Flask server")
#     print("Flask application running on port 8062")
#     print("Click on the link to open the application: http://localhost:8062/")
#     app.run(host="0.0.0.0", port=8062, debug= True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
