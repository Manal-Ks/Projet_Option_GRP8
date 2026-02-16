import pandas as pd
from src.pipeline import run

df_cv = pd.read_csv("data/samples/candidates_sample.csv")
df_jobs = pd.read_csv("data/samples/jobs_sample.csv")

out, meta = run(df_cv, df_jobs, config_path="config.yaml", export=True)

print(out.head(5))
print(meta)
