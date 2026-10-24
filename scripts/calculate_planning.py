"""Exact-binomial planning examples added after the primary analysis.

Run from any working directory. Writes results/validation_planning.csv only.
No participant data or network access is required.
"""
from pathlib import Path
import csv,math
from scipy.stats import beta,binom
ROOT=Path(__file__).resolve().parents[1]
rows=[]
for k in [0,1,2,3,5]:
    row={'maximum_errors_k':k}
    for alpha,label in [(.10,'90'),(.05,'95')]:
        def direct(n):
            return math.fsum(math.comb(n,j)*alpha**j*(1-alpha)**(n-j) for j in range(k+1))
        n=next(n for n in range(k+1,2000) if direct(n)<=.025)
        upper=float(beta.ppf(.975,k+1,n-k))
        assert direct(n-1)>.025 and upper<=alpha
        assert abs(direct(n)-binom.cdf(k,n,alpha))<1e-12
        row['minimum_n_'+label]=n
        row['upper_error_bound_'+label]=upper
    rows.append(row)
(ROOT/'results').mkdir(exist_ok=True)
with (ROOT/'results/validation_planning.csv').open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
print('Supplementary Table 4: exact-binomial planning examples reproduced.')
