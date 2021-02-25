# Initial plotting of jet data for analyzing tau tagging possibilities

import csv
import matplotlib.pyplot as plt


def get_column(data, title):
    column = []
    for row in data:
        try:
            point = int(row[title])
        except ValueError:
            try:
                point = float(row[title])
            except ValueError:
                point = row[title]
        if point == '':
            continue
        column.append(point)
    try:
        column.sort()
    except TypeError:
        pass
    return column


def create_bins(column, n_bins):
    min_value = 100000
    max_value = -100000
    for point in column:
        if point > max_value:
            max_value = point
        if point < min_value:
            min_value = point
    value_range = max_value - min_value
    step = value_range / n_bins
    bins = [min_value]
    for i in range(n_bins):
        min_value += step
        bins.append(min_value)
    return bins


def filter_data(data, filter, filtervalue):
    filtered_data = []
    for row in data:
        if row[filter] == filtervalue:
            filtered_data.append(row)
    return filtered_data


data = []

with open('data/tau_tagger.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        data.append(row)

true_taus = filter_data(data, 'truth', 'True')

plt.figure(figsize=(20, 40))
bins = [0, 1, 2, 3, 4, 5]

n_charged = get_column(data, 'n_charged')
n_charged_taus = get_column(true_taus, 'n_charged')
p1 = plt.subplot(421, title='Number of charged particles')
p1.hist(n_charged, bins=5, label='all jets', histtype='step')
p1.hist(n_charged_taus, bins=5, label='tau jets', histtype='step')
p1.legend()

n_neutral = get_column(data, 'n_neutral')
n_neutral_taus = get_column(true_taus, 'n_neutral')
p2 = plt.subplot(422, title='Number of neutral particles')
p2.hist(n_neutral, label='all jets', histtype='step')
p2.hist(n_neutral_taus, label='tau jets', histtype='step')
p2.legend()

f_charged = get_column(data, 'charged_fraction')
f_charged_taus = get_column(true_taus, 'charged_fraction')
bins = create_bins(f_charged, 10)
p3 = plt.subplot(423, title='Charged fraction')
p3.hist(f_charged, bins=bins, label='all jets', histtype='step')
p3.hist(f_charged_taus, bins=bins, label='tau jets', histtype='step')
p3.legend()

f_neutral = get_column(data, 'neutral_fraction')
f_neutral_taus = get_column(true_taus, 'neutral_fraction')
bins = create_bins(f_neutral, 10)
p4 = plt.subplot(424, title='Neutral fraction')
p4.hist(f_neutral, bins=bins, label='all jets', histtype='step')
p4.hist(f_neutral_taus, bins=bins, label='tau jets', histtype='step')
p4.legend()

dR = get_column(data, 'd_R')
dR_taus = get_column(true_taus, 'd_R')
bins = create_bins(dR, 10)
p5 = plt.subplot(425, title='Cone size')
p5.hist(dR, bins=bins, label='all jets', histtype='step')
p5.hist(dR_taus, bins=bins, label='tau jets', histtype='step')
p5.legend()

eta = get_column(data, 'eta')
eta_taus = get_column(true_taus, 'eta')
bins = create_bins(eta, 10)
p6 = plt.subplot(426, title='Eta')
p6.hist(eta, bins=bins, label='all jets', histtype='step')
p6.hist(eta_taus, bins=bins, label='tau jets', histtype='step')
p6.legend()

mass = get_column(data, 'm')
mass_taus = get_column(true_taus, 'm')
bins = create_bins(mass, 10)
p7 = plt.subplot(427, title='Mass')
p7.hist(mass, bins=bins, label='all jets', histtype='step')
p7.hist(mass_taus, bins=bins, label='tau jets', histtype='step')
p7.legend()

plt.savefig('data/plots.png')
