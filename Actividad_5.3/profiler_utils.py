import cProfile
import pstats
import io

def profile_function(func):
    """
    Ejecuta profiling sobre una función.

    Returns:
        tuple: (resultado función, string profiling)
    """
    pr = cProfile.Profile()
    pr.enable()

    result = func()

    pr.disable()

    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
    ps.print_stats(5)

    return result, s.getvalue()