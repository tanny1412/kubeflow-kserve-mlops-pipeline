from kfp import dsl
from kfp.dsl import Output, Dataset

@dsl.component(base_image="python:3.9")
def load_data(output_csv: Output[Dataset]):
    import subprocess
    subprocess.run(["pip", "install", "pandas", "scikit-learn"], check=True)

    from sklearn.datasets import load_iris
    import pandas as pd
    iris = load_iris()
    df = pd.DataFrame(data=iris.data, columns=iris.feature_names)
    df['target'] = iris.target
    df.to_csv(output_csv.path, index=False)
