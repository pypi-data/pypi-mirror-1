#!/usr/bin/env python

average = lambda L: float(len(L)) and sum(L) / float(len(L))

def main():
    from pycpmc.conf import ui, source

    print "initializing..."
    ui = ui()
    def _inner():
        tot_errors = 0
        cpms = []
        while True:
            target_sentence = source()
            start, last, errors, input_sentence = ui.get_sentence(
                target_sentence)
            tot_errors += errors
            time_delta = last - start
            if input_sentence and time_delta:
                cps = len(input_sentence) / time_delta
                cpms.append(cps * 60)  # CPM.
                ui.display_stats(avg_cpm=average(cpms), tot_errors=tot_errors,
                    last_cpm=cpms[-1], last_errors=errors)
                yield cpms[-1], errors
    L = []
    try:
        try:
            [L.append(x) for x in _inner()]
        except KeyboardInterrupt:
            pass
    finally:
        ui.end()
    for pair in L:
        print "cpm=%r, errors=%r" % pair

if __name__ == "__main__":
    main()
