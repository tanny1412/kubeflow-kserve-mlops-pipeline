from kfp import dsl
from kfp.dsl import Input, Output, Dataset, Model

@dsl.component(
    base_image="python:3.9",
    packages_to_install=["pandas", "scikit-learn", "joblib", "boto3", "s3fs"]
)
def train_model(
    train_data: Input[Dataset], 
    ytrain_data: Input[Dataset], 
    model_output: Output[Model],
    aws_access_key_id: str,
    aws_secret_access_key: str,
    s3_bucket: str,
    s3_key: str
) -> str:
    import pandas as pd
    from sklearn.linear_model import LogisticRegression
    from joblib import dump
    import boto3
    import os
    from datetime import datetime
    import json

    X_train = pd.read_csv(train_data.path)
    y_train = pd.read_csv(ytrain_data.path).values.ravel()

    model = LogisticRegression()
    model.fit(X_train, y_train)

    local_path = model_output.path
    dump(model, local_path)

    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    s3_path = f"{s3_key}/model_{timestamp}.joblib"

    s3_client.upload_file(local_path, s3_bucket, s3_path)

    model_uri = f"s3://{s3_bucket}/{s3_path}"
    return model_uri
