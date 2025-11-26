try:
    from sklearn.linear_model import LinearRegression
except ImportError:
    LinearRegression = None

class SimpleCarbonRegressor:
    def __init__(self):
        self.model = LinearRegression() if LinearRegression else None
        self.fitted = False
    def fit(self, rows):
        if not rows or self.model is None: return
        import numpy as np
        X=[]; y=[]
        for r in rows:
            y.append(r.get('baseline_rate',0) or 0)
            X.append([
                r.get('soc',0) or 0,
                r.get('rainfall',0) or 0,
                r.get('temperature',0) or 0,
                r.get('biomass',0) or 0,
                r.get('practice_factor',0) or 0,
            ])
        X=np.array(X); y=np.array(y)
        if len(X)>1:
            try:
                self.model.fit(X,y); self.fitted=True
            except Exception:
                self.fitted=False
    def predict(self, rows):
        if not self.fitted or self.model is None: return [None]*len(rows)
        import numpy as np
        X=[]
        for r in rows:
            X.append([
                r.get('soc',0) or 0,
                r.get('rainfall',0) or 0,
                r.get('temperature',0) or 0,
                r.get('biomass',0) or 0,
                r.get('practice_factor',0) or 0,
            ])
        X=np.array(X)
        try:
            return self.model.predict(X).tolist()
        except Exception:
            return [None]*len(rows)
