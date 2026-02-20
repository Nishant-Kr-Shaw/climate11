
# Visibility distance prediction

## Problem Statement :-

The objective of this project is to develop a machine learning model that can accurately predict the maximum visibility distance in a given location and weather condition. The model should take into account various weather parameters such as humidity, temperature, wind speed, and atmospheric pressure, as well as geographical features such as elevation, terrain, and land cover. The model should be trained on a large dataset of historical weather and visibility data, and validated using a separate test dataset. The ultimate goal is to provide a tool that can help improve safety and efficiency in various applications such as aviation, transportation, and outdoor activities.


## Tech Stack Used

1. Python
2. FastAPI
3. Machine learning algorithms
4. Docker
5. MongoDB

## Infrastructure required

1. AWS S3
2. Azure
3. Github Actions

## How to run

Before you run this project make sure you have MongoDB Atlas account and you have the shipping dataset into it.

Step 1. Cloning the repository.

```

git clone https://github.com/Machine-Learning-01/Customer_segmentation.git

```

Step 2. Create a conda environment.

```

conda create --prefix venv python=3.7 -y

```

```

conda activate venv/

```

Step 3. Install the requirements

```

pip install -r requirements.txt

```

Step 4. Export the environment variable

```bash

export AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID>


export AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY>


export AWS_DEFAULT_REGION=<AWS_DEFAULT_REGION>


export MONGODB_URL= <MONGODB_URL>


```

Step 5. Run the application server

```

python app.py

```

Step 6. Train application

```bash

http://localhost:5000/train

```

Step 7. Prediction application

```bash

http://localhost:5000/predict

```

## Run locally

1. Check if the Dockerfile is available in the project directory
2. Build the Docker image

```

docker build --build-arg AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID> --build-arg AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY> --build-arg AWS_DEFAULT_REGION=<AWS_DEFAULT_REGION> --build-arg MONGODB_URL=<MONGODB_URL> . 

```

3. Run the Docker image

```

docker run -d -p 5000:5000 <IMAGE_NAME>

```

## Project Architecture -

![WhatsApp Image 2022-09-22 at 15 29 19](https://user-images.githubusercontent.com/71321529/192722336-54016f79-89ef-4c8c-9d71-a6e91ebab03f.jpeg)

## Data Collection Architecture -

![WhatsApp Image 2022-09-22 at 15 29 10](https://user-images.githubusercontent.com/71321529/192721926-de265f9b-f301-4943-ac7d-948bff7be9a0.jpeg)

## Deployment Architecture -

![deployment](https://user-images.githubusercontent.com/104005791/199660875-c8e63457-432a-44cb-8a95-800870f3da15.png)

## Models Used

* [K-Means](https://www.javatpoint.com/k-means-clustering-algorithm-in-machine-learning)
* [LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)

From these above models after hyperparameter optimization we selected these two models which were K-Means for clustering and Logistic Regression for classification and used the following in Pipeline.

* GridSearchCV is used for Hyperparameter Optimization in the pipeline.

## `src` is the main package folder which contains

**Components** : Contains all components of Machine Learning Project

- Data Ingestion
- Data Validation
- Data Transformation
- Data Clustering
- Model Trainer
- Model Evaluation
- Model Pusher

**Custom Logger and Exceptions** are used in the Project for better debugging purposes.

## Conclusion

- This Project can be used in real-life by Users.
