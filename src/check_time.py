import timeit
from statistics import fmean, variance
from os import listdir
from os.path import isdir, isfile, join
from classes import Graph
from grammar import scan_cfg, to_crf


def cfpq_time(args):
    paths = [join(args.files[0], folder) for folder in listdir(args.files[0]) if isdir(join(args.files[0], folder))]
    for i in range(len(paths)):
        path = paths[i]
        subfolders = [join(path, folder) for folder in listdir(path) if isdir(join(path, folder))]
        grammars = [join(subfolders[0], grm) for grm in listdir(subfolders[0]) if isfile(join(subfolders[0], grm))]
        graphs = [join(subfolders[1], grph) for grph in listdir(subfolders[1]) if isfile(join(subfolders[1], grph))]
        grammars.sort(key=len)
        graphs.sort(key=len)
        for gram in grammars:
            f = open("time_out.txt", 'a')
            f.write("grammar: " + gram.split('/')[-3] + " " + gram.split('/')[-1] + '\n')
            print(gram)
            f.close()
            for graph in graphs:
                graph = Graph()
                graph.scan(graph)
                cfg = scan_cfg(gram)
                cfg_in_crf = to_crf(cfg)
                output = "   "
                time_hel = timeit.repeat("cfpq_hellings(graph, cfg_in_crf)",
                                         setup="from src.main import cfpq_hellings",
                                         repeat=5,
                                         number=1,
                                         globals=locals())
                output += "Hel: " + str(round(fmean(time_hel), 6)) + "   "

                time_MxM = timeit.repeat("cfpq_MxM(graph, cfg_in_crf)",
                                         setup="from src.main import cfpq_MxM",
                                         repeat=5,
                                         number=1,
                                         globals=locals())
                output += "MxM: " + str(round(fmean(time_MxM), 6)) + "   "

                rec_auto, heads = build_rec_automaton(cfg)
                time_tensor = timeit.repeat("cfpq_tensor(graph, cfg, rec_auto, heads)",
                                            setup="from src.main import cfpq_tensor",
                                            repeat=5,
                                            number=1,
                                            globals=locals())
                output += "tensor: " + str(round(fmean(time_tensor), 6)) + "   "

                rec_auto, heads = build_rec_automaton(cfg_in_crf)
                time_tensor_crf = timeit.repeat("cfpq_tensor(graph, cfg_in_crf, rec_auto, heads)",
                                                setup="from src.main import cfpq_tensor",
                                                repeat=5,
                                                number=1,
                                                globals=locals())
                output += "tensor crf: " + str(round(fmean(time_tensor_crf), 6)) + "   "
                f = open("time_out.txt", 'a')
                f.write("graph: " + graph.split('/')[-3] + " " + graph.split('/')[-1] + "   " + output.replace('.', ',') + '\n')
                print("graph: " + graph.split('/')[-3] + " " + graph.split('/')[-1] + "   " + output.replace('.', ','))
                f.close()


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
    if args.type[0] == "clos_graph":
        graph.scan(args.files[0])
    elif args.type[0] == "clos_regexp":
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
