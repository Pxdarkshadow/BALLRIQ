"""
Create standard Academic Jupyter Notebooks for BALLRIQ:
- 02_preprocessing_analysis.ipynb
- 03_nlp_model_training.ipynb
- 04_ir_evaluation.ipynb
- 05_bda_analytics.ipynb
"""
import json
from pathlib import Path

NOTEBOOKS_DIR = Path(__file__).resolve().parents[1] / "notebooks"
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)


def make_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.10"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }


def md_cell(text):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.split("\n")]
    }


def code_cell(code):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in code.split("\n")]
    }


def generate_all_notebooks():
    # Notebook 02: Preprocessing Analysis
    nb02_cells = [
        md_cell("# 02 - Preprocessing Pipeline Analysis\n## BALLRIQ: Unicode, Cleaning, Number & Domain Normalization"),
        code_cell("""import sys
sys.path.insert(0, "..")
import json
from backend.app.nlp.preprocessing.pipeline import NLPPreprocessingPipeline

pipeline = NLPPreprocessingPipeline()

sample_texts = [
    "कोहली ने  शानदार!!!  चौका मारा और ४ रन लिए",
    "बुमराहने अप्रतिम यॉर्कर टाकला आणि फलंदाज बाद झाला!!!",
    "Virat Kohli ne amazing cover drive maara and ball boundary paar gayi"
]

for t in sample_texts:
    res = pipeline.process(t)
    print(f"Original: {res.original_text}")
    print(f"Language: {res.detected_language} (Conf: {res.language_confidence:.2f})")
    print(f"Final:    {res.final_text}")
    print(f"Tokens:   {res.tokens}")
    print("-" * 50)
"""),
        md_cell("### Step-by-Step Breakdown Analysis"),
        code_cell("""res = pipeline.process(sample_texts[0])
for i, step in enumerate(res.steps, 1):
    print(f"Step {i}: {step.step_name} -> {step.output_text}")
""")
    ]

    # Notebook 03: NLP Model Training
    nb03_cells = [
        md_cell("# 03 - NLP Event Classification Model Training\n## Baseline (TF-IDF + Logistic Regression) vs Transformer (XLM-R)"),
        code_cell("""import sys
sys.path.insert(0, "..")
import json
from pathlib import Path
from backend.app.nlp.models.baseline import BaselineEventClassifier, load_split_data

data_dir = Path("../data/processed/nlp")
train, val, test = load_split_data(data_dir)
print(f"Loaded Splits -> Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
"""),
        code_cell("""# Evaluate trained baseline model
model_dir = Path("../models/nlp/event_classifier_baseline")
classifier = BaselineEventClassifier.load(model_dir)

test_metrics = classifier.evaluate(test)
print(f"Test Accuracy: {test_metrics['accuracy']:.4f}")
print(f"Macro F1:      {test_metrics['macro_f1']:.4f}")
"""),
        code_cell("""# Inspect per-class classification metrics
import pandas as pd
df_metrics = pd.DataFrame(test_metrics['per_class']).T
print(df_metrics[['precision', 'recall', 'f1', 'support']])
""")
    ]

    # Notebook 04: IR Evaluation
    nb04_cells = [
        md_cell("# 04 - Information Retrieval (IR) Benchmark & Evaluation\n## TF-IDF vs BM25 vs Semantic vs Hybrid Search"),
        code_cell("""import sys
sys.path.insert(0, "..")
import json
from pathlib import Path
from backend.app.ir.tfidf_search import TFIDFRetriever, load_ir_documents
from backend.app.ir.bm25_search import BM25Retriever
from backend.app.ir.hybrid_search import HybridRetriever

docs_path = Path("../data/processed/ir/documents.jsonl")
documents = load_ir_documents(docs_path)
print(f"Total documents loaded: {len(documents)}")
"""),
        code_cell("""# Run Sample Hybrid Search
hybrid = HybridRetriever(documents, alpha=0.5)
bm25 = BM25Retriever(documents)
bm25.build_index()
hybrid.bm25_retriever = bm25

results = hybrid.search("कोहली चौका", top_k=5)
for r in results:
    print(f"Rank {r.get('rank')}: [{r.get('match_id')} Over {r.get('over')}.{r.get('ball')}] Score: {r.get('score'):.4f}")
    print(f"  Content: {r.get('content')}")
"""),
        code_cell("""# Load official IR evaluation report
with open("../reports/ir/ir_evaluation_report.json", "r", encoding="utf-8") as f:
    ir_report = json.load(f)

import pandas as pd
pd.DataFrame(ir_report['comparison_table'])
""")
    ]

    # Notebook 05: BDA Analytics
    nb05_cells = [
        md_cell("# 05 - Big Data Analytics (BDA) with DuckDB & Parquet\n## OLAP Aggregations, Player Matchups & Phase Analysis"),
        code_cell("""import sys
sys.path.insert(0, "..")
from backend.app.bda.olap_engine import CricketOLAPEngine
import pandas as pd

engine = CricketOLAPEngine()
print("Lakehouse Summary:")
print(engine.get_lakehouse_summary())
"""),
        code_cell("""# Phase-wise match aggregations
phase_df = pd.DataFrame(engine.get_phase_analytics())
print("Phase Analytics:")
print(phase_df[['phase', 'total_balls', 'total_runs', 'estimated_run_rate', 'boundary_percentage', 'dot_percentage']])
"""),
        code_cell("""# Custom analytical query directly over Parquet Lake
res = engine.execute_custom_sql(\"\"\"
    SELECT
        b.batter_name,
        SUM(b.runs) as total_runs,
        ROUND(SUM(b.runs)*100.0/SUM(b.balls), 2) as strike_rate,
        SUM(b.sixes) as total_sixes
    FROM batting_stats b
    GROUP BY b.batter_name
    ORDER BY total_runs DESC
    LIMIT 10;
\"\"\")

pd.DataFrame(res['rows'], columns=res['columns'])
""")
    ]

    # Save all
    notebooks = {
        "02_preprocessing_analysis.ipynb": nb02_cells,
        "03_nlp_model_training.ipynb": nb03_cells,
        "04_ir_evaluation.ipynb": nb04_cells,
        "05_bda_analytics.ipynb": nb05_cells,
    }

    for name, cells in notebooks.items():
        nb_path = NOTEBOOKS_DIR / name
        with open(nb_path, "w", encoding="utf-8") as f:
            json.dump(make_notebook(cells), f, indent=2)
        print(f"Created notebook: {nb_path}")

    print("\nAll academic notebooks generated successfully!")


if __name__ == "__main__":
    generate_all_notebooks()
