from kfp import dsl
from kfp.dsl import Input, Output, Dataset, Model

@dsl.component(base_image="python:3.9")
def evaluate_model(test_data: Input[Dataset], ytest_data: Input[Dataset], model: Input[Model], metrics_output: Output[Dataset]):
    import subprocess
    subprocess.run(["pip", "install", "pandas", "scikit-learn", "matplotlib", "joblib"], check=True)

    import pandas as pd
    from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
    import matplotlib.pyplot as plt
    from joblib import load

    X_test = pd.read_csv(test_data.path)
    y_test = pd.read_csv(ytest_data.path)
    model = load(model.path)

    y_pred = model.predict(X_test)

    report = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred)
    accuracy = accuracy_score(y_test, y_pred)

    with open(metrics_output.path, 'w') as f:
        f.write(f"Accuracy: {accuracy}\n")
        f.write(str(report))

    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Confusion Matrix')
    plt.colorbar()
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.savefig(metrics_output.path.replace('.txt', '.png'))
