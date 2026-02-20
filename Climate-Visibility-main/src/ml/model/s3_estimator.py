from src.cloud_storage.aws_storage import SimpleStorageService
from src.exception import VisibilityException
from src.ml.model.estimator import VisibilityModel
import sys
from pandas import DataFrame



class VisibilityEstimator:
    """
    This class is used to save and retrieve visibility model in s3 bucket and to do prediction
    """

    def __init__(self,bucket_name,model_name):
        """
        :param bucket_name: Name of your model bucket
        :param model_path: Name of your model in bucket
        """
        self.bucket_name = bucket_name
        self.s3 = SimpleStorageService()
        self.model_name = model_name
        self.loaded_model:VisibilityModel=None


    def is_model_present(self,model_name):
        try:
            return self.s3.s3_key_path_available(bucket_name=self.bucket_name, s3_key=model_name)
        except Exception as e:
            print(e)
            return False

    def load_model(self,)->VisibilityModel:
        """
        Load the model from the model_path
        :return:
        """

        return self.s3.load_model(self.model_name,bucket_name=self.bucket_name)

    def save_model(self,from_file,remove:bool=False)->None:
        """
        Save the model to the model_path
        :param from_file: Your local system model path
        :param remove: By default it is false that mean you will have your model locally available in your system folder
        :return:
        """
        
        try:
            self.s3.upload_file(from_file,
                                to_filename=self.model_name,
                                bucket_name=self.bucket_name,
                                remove=remove
                                )
        except Exception as e:
            raise (e, sys)


    def predict(self,dataframe:DataFrame):
        """
        :param dataframe:
        :return:
        """
        try:
            if self.loaded_model is None:
                self.loaded_model = self.load_model()
            return self.loaded_model.predict(dataframe)
        except Exception as e:
            raise VisibilityException(e,sys)