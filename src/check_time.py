import timeit
from statistics import fmean, variance
from classes import Graph


def inter_time(args):
    graph = Graph()
    automaton = Graph()
    res = Graph()
    graph.scan(args.files[0])
    automaton.scan_regexp(args.files[1])
    time_inter = timeit.repeat("res.intersection(automaton, graph)",
                               setup="from classes import Graph",
                               repeat=5,
                               number=1,
                               globals=locals())
    res.intersection(automaton, graph)
    f = open("time_out.txt", 'a')
    f.write(str(args.files[0]) + " " + str(args.files[1]) + "\n")
    average = round(fmean(time_inter), 6)
    D = round(variance(time_inter), 6)
    time_inter = [round(t, 6) for t in time_inter]
    f.write("intersection: " + str(time_inter) + " " +
            str(average) + " " +
            str(D) + "\n")

    time_print = timeit.repeat("res.print_inter()",
                               setup="from classes import Graph",
                               repeat=5,
                               number=1,
                               globals=locals())
    average = round(fmean(time_print), 6)
    D = round(variance(time_print), 6)
    time_print = [round(t, 6) for t in time_print]
    f.write("time_print: " + str(time_print) + " " +
            str(average) + " " +
            str(D) + "\n\n")
    f.close()


def clos_time(args):
    graph = Graph()
    if args.type[0] == "graph":
        graph.scan(args.files[0])
    elif args.type[0] == "regexp":
        graph.scan_regexp(args.files[0])
    f = open("time_out.txt", 'a')
    f.write(str(args.files[0]) + "\n")
    time_clos_adjM = timeit.repeat("graph.transitive_closure_adjM()",
                                   setup="from classes import Graph",
                                   repeat=5,
                                   number=1,
                                   globals=locals())
    res = graph.transitive_closure_adjM()
    print(res.nvals)
    average = round(fmean(time_clos_adjM), 6)
    D = round(variance(time_clos_adjM), 6)
    time_clos_adjM = [round(t, 6) for t in time_clos_adjM]
    f.write("transitive_closure_adjM: " + str(time_clos_adjM) + " " +
            str(average) + " " +
            str(D) + "\n")

    time_clos_squar = timeit.repeat("graph.transitive_closure_squaring()",
                                    setup="from classes import Graph",
                                    repeat=5,
                                    number=1,
                                    globals=locals())
    res = graph.transitive_closure_squaring()
    print(res.nvals)
    average = round(fmean(time_clos_squar), 6)
    D = round(variance(time_clos_squar), 6)
    time_clos_squar = [round(t, 6) for t in time_clos_squar]
    f.write("transitive_closure_squaring: " + str(time_clos_squar) + " " +
            str(average) + " " +
            str(D) + "\n\n")
    f.close()
