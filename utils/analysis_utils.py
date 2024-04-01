import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix


def plot_toxicity_scores_distrubution(df):
    plt.hist(df["shield_score"], bins=10, color='skyblue', edgecolor='black')  
    plt.title("Shield Toxicity Scores")
    plt.xlabel("Score")
    plt.ylabel("Number")
    plt.grid(True)
    plt.show()


def print_performance_metrics(df):
    accuracy = accuracy_score(df["label"], df["shield_result"])
    precision = precision_score(df["label"], df["shield_result"])
    recall = recall_score(df["label"], df["shield_result"])
    f1 = f1_score(df["label"], df["shield_result"])
    conf_matrix = confusion_matrix(df["label"], df["shield_result"])

    print("Accuracy:", accuracy)
    print("Precision:", precision)
    print("Recall:", recall)
    print("F1 Score:", f1)
    print("Confusion Matrix:")
    print('''[[TN FP] \n [FN TP]] ''')
    print(conf_matrix)


def granular_result_dfs(df):
    fn = df[(df["shield_result"] == False) & (df["label"] == True)]

    fp = df[(df["shield_result"] == True) & (df["label"] == False)]

    tp = df[(df["shield_result"] == True) & (df["label"] == True)]

    tn = df[(df["shield_result"] == False) & (df["label"] == False)]

    return fn, fp, tp, tn