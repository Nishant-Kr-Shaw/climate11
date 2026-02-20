import shutil
import os,sys
import csv
from datetime import datetime
from src.logger import logging

import sys
from src.cloud_storage.aws_syncer import S3Sync
from flask import request, Request
from src.utils.main_utils import MainUtils
from src.constant import *
from src.exception import VisibilityException

from dataclasses import dataclass
        
        
@dataclass
class PredictionPipelineConfig:
    model_path = os.path.join("artifacts","prediction_model","model.pkl")




class PredictionPipeline:
    def __init__(self, request: Request):

        self.request = request  
        self.s3_sync = S3Sync()     
        self.utils = MainUtils()
        self.prediction_pipeline_config = PredictionPipelineConfig() 


    def download_model(self):
        try:
            model_dir = os.path.dirname(self.prediction_pipeline_config.model_path)
            # If model already exists locally, skip S3 sync
            if os.path.exists(self.prediction_pipeline_config.model_path):
                return self.prediction_pipeline_config.model_path

            # Attempt to sync from S3 (requires AWS CLI/config); don't fail hard here
            try:
                self.s3_sync.sync_folder_from_s3(
                    folder=model_dir,
                    aws_bucket_name=AWS_S3_BUCKET_NAME,
                )
            except Exception:
                # proceed to check local path; raise below if missing
                pass

            if not os.path.exists(self.prediction_pipeline_config.model_path):
                raise VisibilityException(f"Model not found at {self.prediction_pipeline_config.model_path}", sys)

            return self.prediction_pipeline_config.model_path
            
        except Exception as e:
            raise VisibilityException(e,sys)
        
        
    def run_pipeline(self):
        try:
            data = dict(self.request.form.items())
            # preserve form order and coerce to floats
            values = list(data.values())
            if not values:
                raise VisibilityException("No input values provided for prediction", sys)

            try:
                numeric_values = [float(x) for x in values]
            except Exception as e:
                raise VisibilityException(f"Failed to convert input values to numbers: {e}", sys)

            model_path = self.download_model()
            model = self.utils.load_object(file_path=model_path)

            # Type hint to indicate model has predict method
            from typing import Any
            model: Any = model

            # Ensure the input is a 2D array as expected by scikit-learn-like estimators
            try:
                import numpy as _np
                arr = _np.asarray(numeric_values, dtype=float).reshape(1, -1)
            except Exception:
                # fall back to list-in-list if numpy unavailable
                arr = [numeric_values]

            def ensure_monotonic_attr(obj):
                try:
                    if hasattr(obj, "named_steps"):
                        for sub in obj.named_steps.values():
                            ensure_monotonic_attr(sub)

                    if hasattr(obj, "steps"):
                        for _, sub in getattr(obj, "steps"):
                            ensure_monotonic_attr(sub)

                    if hasattr(obj, "estimators_"):
                        for est in getattr(obj, "estimators_"):
                            if not hasattr(est, "monotonic_cst"):
                                setattr(est, "monotonic_cst", None)
                            ensure_monotonic_attr(est)

                    if hasattr(obj, "estimator_"):
                        ensure_monotonic_attr(getattr(obj, "estimator_"))

                    if not hasattr(obj, "monotonic_cst") and hasattr(obj, "tree_"):
                        setattr(obj, "monotonic_cst", None)
                except Exception:
                    pass

            try:
                prediction = model.predict(arr)
            except AttributeError as err:
                # Try to patch missing attributes caused by sklearn version mismatch
                if "monotonic_cst" in str(err) or "monotonic" in str(err):
                    ensure_monotonic_attr(model)
                    try:
                        prediction = model.predict(arr)
                    except Exception as e2:
                        raise VisibilityException(f"Model prediction failed after compatibility fix: {e2}", sys)
                else:
                    raise VisibilityException(f"Model prediction failed: {err}", sys)
            except Exception as e:
                msg = str(e)
                if "Trying to unpickle estimator" in msg or "InconsistentVersionWarning" in msg:
                    raise VisibilityException(
                        "Model appears incompatible with the installed scikit-learn version. "
                        "Either install scikit-learn==1.3.2 (the version used when the model was saved) "
                        "or retrain the model with the current scikit-learn version.",
                        sys,
                    )
                raise VisibilityException(f"Model prediction failed: {e}", sys)

            # Normalize return type: convert numpy types to native Python
            try:
                pred0 = prediction[0]
                # convert numpy scalars to native types
                if hasattr(pred0, 'item'):
                    pred0 = pred0.item()
            except Exception:
                pred0 = prediction

            # persist prediction record
            try:
                preds_dir = os.path.join("artifacts", "predictions")
                os.makedirs(preds_dir, exist_ok=True)
                csv_path = os.path.join(preds_dir, "predictions.csv")
                header = ["timestamp", "model_path", "inputs", "prediction"]
                row = [datetime.now().isoformat(), model_path, repr(numeric_values), repr(pred0)]
                write_header = not os.path.exists(csv_path)
                with open(csv_path, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    if write_header:
                        writer.writerow(header)
                    writer.writerow(row)
            except Exception:
                # don't let logging failures break prediction
                logging.exception("Failed to persist prediction record")

            return pred0


        except Exception as e:
            # persist failed prediction attempt
            try:
                preds_dir = os.path.join("artifacts", "predictions")
                os.makedirs(preds_dir, exist_ok=True)
                csv_path = os.path.join(preds_dir, "predictions.csv")
                header = ["timestamp", "model_path", "inputs", "error"]
                row = [datetime.now().isoformat(), getattr(self.prediction_pipeline_config, 'model_path', ''), repr(list(self.request.form.items())), str(e)]
                write_header = not os.path.exists(csv_path)
                with open(csv_path, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    if write_header:
                        writer.writerow(header)
                    writer.writerow(row)
            except Exception:
                logging.exception("Failed to persist prediction error record")

            raise VisibilityException(e,sys)
            
        

 
        

        