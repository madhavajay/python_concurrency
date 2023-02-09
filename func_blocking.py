def cpu_bound_func(total: int) -> None:
    import numpy as np
    x = np.array([range(total)])
    x.sum()
    print("Did work", x)

