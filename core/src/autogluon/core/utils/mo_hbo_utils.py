""" Methods helpful for multi-objective HPO.
"""

import numpy as np


def retrieve_pareto_front(training_history, objectives):
    """Retrieves the pareto efficient points discovered during a
    scheduler's search process.

    Parameters
    ----------
    training_history:
        A training history dictionary generated by the scheduler's
        search process.
    objectives : dict
        Dictionary with the names of objectives of interest. The corresponding
        values are allowed to be either "MAX" or "MIN" and indicate if an
        objective is to be maximized or minimized.

    Returns
    ----------
    front: list
        A list containing the Pareto efficient points among all points
        that were found during the search process.
    """
    vals = []
    refs = []

    for task_id, task_res in training_history.items():
        for step, res_dict in enumerate(task_res):
            vals.append([res_dict[k] for k in objectives])
            refs.append((task_id, step + 1))
    vals = np.array(vals)

    # We determine the Pareto front assuming pure minimization we adapt
    # the signs accordingly
    sign_vector = prepare_sign_vector(objectives)
    a_vals = vals * (-sign_vector)
    eff_mask = np.ones(vals.shape[0], dtype=bool)
    for i, c in enumerate(a_vals):
        if eff_mask[i]:
            eff_mask[eff_mask] = np.any(a_vals[eff_mask] <= c, axis=1)
    indices = [i for i, b in enumerate(eff_mask) if b]

    front = []
    for e in indices:
        r = {"task_id-ressource": refs[e]}
        for i, o in enumerate(objectives):
            r[o] = vals[e][i]
        front.append(r)
    return front


def prepare_sign_vector(objectives):
    """Generates a numpy vector which can be used to flip the signs of the
    objectives values which are intended to be minimized.

    Parameters
    ----------
    objectives: dict
        The dictionary keys name the objectives of interest. The associated
        values can be either "MIN" or "MAX" and indicate if an objective is
        to be minimized or maximized.

    Returns
    ----------
    sign_vector: np.array
        A numpy array containing 1 for objectives to be maximized and -1 for
        objectives to be minimized.
    """
    converter = {"MIN": -1.0, "MAX": 1.0}
    try:
        sign_vector = np.array([converter[objectives[k]] for k in objectives])
    except KeyError:
        raise ValueError(
            "Error, in conversion of objective dict. Allowed \
            values are 'MIN' and 'MAX'"
        )
    return sign_vector


def uniform_from_unit_simplex(dim):
    """Samples a point uniformly at random from the unit simplex using the
    Kraemer Algorithm. The algorithm is described here:
    https://www.cs.cmu.edu/~nasmith/papers/smith+tromble.tr04.pdf

    Parameters
    ----------
    dim: int
        Dimension of the unit simplex to sample from.

    Returns:
    sample: np.array
         A point sampled uniformly from the unit simplex.
    """
    uni = np.random.uniform(size=(dim))
    uni = np.sort(uni)
    sample = np.diff(uni, prepend=0) / uni[-1]
    assert sum(sample) - 1 < 1e-6, "Error in weight sampling routine."
    return np.array(sample)
