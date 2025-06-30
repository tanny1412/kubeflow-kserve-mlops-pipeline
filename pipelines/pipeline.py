import os
from kfp import dsl, compiler

# Import modular components
from pipelines.components.load_data import load_data
from pipelines.components.preprocess import preprocess_data
from pipelines.components.train import train_model
from pipelines.components.evaluate import evaluate_model

@dsl.pipeline(name="ml-pipeline")
def ml_pipeline(
    aws_access_key_id: str = os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key: str = os.getenv('AWS_SECRET_ACCESS_KEY'),
    s3_bucket: str = "kubeflow-bucket-iquant00",
    s3_key: str = "models/iris"
):
    # Step 1: Load data
    load_op = load_data()

    # Step 2: Preprocess
    preprocess_op = preprocess_data(
        input_csv=load_op.outputs["output_csv"]
    )

    # Step 3: Train
    train_op = train_model(
        train_data=preprocess_op.outputs["output_train"],
        ytrain_data=preprocess_op.outputs["output_ytrain"],
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        s3_bucket=s3_bucket,
        s3_key=s3_key
    )

    # Step 4: Evaluate
    evaluate_model(
        test_data=preprocess_op.outputs["output_test"],
        ytest_data=preprocess_op.outputs["output_ytest"],
        model=train_op.outputs["model_output"]
    )

if __name__ == "__main__":
    compiler.Compiler().compile(
        pipeline_func=ml_pipeline,
        package_path="pipeline.yaml"
    )
