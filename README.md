# shrinkage

Linear and nonlinear shrinkage estimators for covariance matrices, following
Ledoit and Wolf.

Sample covariance matrices are noisy when the number of variables is large
relative to the number of observations. Shrinkage pulls the sample estimate
toward a structured target, trading a little bias for a large reduction in
variance and producing a better-conditioned, invertible estimate.

## Installation

```bash +RHIZA_SKIP
pip install git+https://github.com/Jebel-Quant/shrinkage.git
```

## Usage

`cov1para` implements the Ledoit-Wolf (2003) one-parameter estimator, which
shrinks the sample covariance toward a scaled identity (equal variances, zero
covariances). Pass a raw data matrix of shape `(N, p)` — `N` observations on
`p` variables:

```python
import numpy as np

from shrinkage.linear import cov1para

rng = np.random.default_rng(0)
Y = rng.standard_normal((250, 3))  # 250 observations, 3 variables

estimator = cov1para(Y)
print(estimator.shape)
print(np.allclose(estimator, estimator.T))  # symmetric
```

```result
(3, 3)
True
```

By default the data is demeaned and the effective sample size is reduced by one.
Use `k=0` to skip demeaning, or `k=1` if `Y` is already demeaned.

## Documentation

See the [API reference](https://jebel-quant.github.io/shrinkage/api/) for the
full estimator documentation.
