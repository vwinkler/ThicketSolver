# Problem
The problem is described in [this Reddit post](https://www.reddit.com/r/AskComputerScience/comments/m4mxgq/is_this_problem_intractable/).

# Solution
The generator requires the size `n x m` of the area and returns a weighted partial MaxSAT formula.
A MaxSAT solver (not included) will provide the optimal solution for this formula as a variable assignment.
For sufficiently large areas (`n > 2` and `m > 2`), the formula is always satisfiable.
The parser reads the output of the solver and produces a solution to the original problem.

A higher scoring solution of the MaxSAT formula corresponds to a higher scoring solution of the original problem,
hence the (optimal) solution of the MaxSAT formula is the optimal solution of the original problem.

# Usage
For an area of `5 x 12` use

    python generate_wcnf.py | solve_maxsat | python parse_result.py

In place of `solve_maxsat` you need to call a MaxSAT solver that abides by the
[DIMACS format of the Max-SAT 2016 evaluation](http://maxsat.ia.udl.cat/requirements/).
One option that has worked flawlessly is [Open-WBO](https://github.com/sat-group/open-wbo).

More generally, e.g. for an area of `4 x 8`, use

    python generate_wcnf.py --width 4 --height 8 | solve_maxsat | python parse_result.py --width 4 --height 8

# Performance
For an area of `5 x 12` on a `Intel(R) Core(TM) i5-2500K CPU @ 3.30GHz` system with 24 GB RAM running Open-WBO
it takes about 3:15 h (tested `n=1` time).

# Output
For `python generate_wcnf.py | solve_maxsat | python parse_result.py` (an area of `5 x 12`)
the output has been observed to be

    An optimum solution was found.

     T T W W W

     T W W T W

     W W T W W

     W T W W T

     T W W T W

     W W T W W

     W T W W T

     W T W T T

     W T W W T

     W W T W W

     T W W T W

     T T W W W

    
Accordingly the optimal solution has a score of 234.
