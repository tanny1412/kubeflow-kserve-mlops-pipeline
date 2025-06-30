from kfp import dsl
from kfp.dsl import Input, Output, Dataset

@dsl.component(base_image="python:3.9")
def preprocess_data(input_csv: Input[Dataset], output_train: Output[Dataset], output_test: Output[Dataset], 
                    output_ytrain: Output[Dataset], output_ytest: Output[Dataset]):
    import subprocess
    subprocess.run(["pip", "install", "pandas", "scikit-learn"], check=True)

    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

    df = pd.read_csv(input_csv.path)

    if df.isnull().values.any():
        df = df.dropna()

    features = df.drop(columns=['target'])
    target = df['target']

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    X_train, X_test, y_train, y_test = train_test_split(
        scaled_features, target, test_size=0.2, random_state=42
    )

    X_train_df = pd.DataFrame(X_train, columns=features.columns)
    X_test_df = pd.DataFrame(X_test, columns=features.columns)
    y_train_df = pd.DataFrame(y_train)
    y_test_df = pd.DataFrame(y_test)

    X_train_df.to_csv(output_train.path, index=False)
    X_test_df.to_csv(output_test.path, index=False)
    y_train_df.to_csv(output_ytrain.path, index=False)
    y_test_df.to_csv(output_ytest.path, index=False)
