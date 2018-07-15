import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt


def objective_plotter(evaluated_listings, on1, on2):

    x = [e.scores[on1] for e in evaluated_listings]
    y = [e.scores[on2] for e in evaluated_listings]

    for e in evaluated_listings:
        x, y = e.scores[on1], e.scores[on2]
        plot = plt.plot(x, y, 'o')
        plt.annotate(e.listing.address, [x, y])
    plt.xlabel(on1)
    plt.ylabel(on2)
    plt.show()
