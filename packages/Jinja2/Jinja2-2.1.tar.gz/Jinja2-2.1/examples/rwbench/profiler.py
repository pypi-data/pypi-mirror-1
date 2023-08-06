from cProfile import Profile
from dozer.profile import buildtree, write_dot_graph


def profile_into(func, filename):
    prof = Profile()
    prof.runcall(func)
    results = prof.getstats()
    tree = buildtree(results)
    write_dot_graph(results, tree, filename)
