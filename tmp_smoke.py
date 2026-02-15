import os,sys
os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from scoring_engine.evaluation import compute_subscores
print('imported compute_subscores OK')
