import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt


def objective_plotter(evaluated_listings, objectives):
    nrows = ncols = len(objectives)
    index = 0

    for objective1 in objectives:
        for objective2 in objectives:
            index += 1

            on1 = objective1.name
            on2 = objective2.name

            if on1 == on2:
                continue

            plt.subplot(nrows, ncols, index)

            for e in evaluated_listings:
                x, y = e.scores[on1], e.scores[on2]
                plt.plot(x, y, 'o')
                plt.annotate(e.listing.address, [x, y])
                plt.xlabel(on1)
                plt.ylabel(on2)

    plt.show()
