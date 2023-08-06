#!/usr/bin/env python

from __future__ import division
import sys
import mpgutils.fk_utils as fk

intensities_fname = 'data.txt.fixed'
genotypes_fname = 'genotypes.txt.fixed'
#genotypes_fname = 'ST3_CNP_genotypes_fixed.txt'
output_fname = 'clusters.txt'

min_variance = 0.0001

intensities = {}

f = open(intensities_fname)

intensities_header = f.readline().split()
intensities_header.pop(0)
intensities_header = [fk.extract_na(e) for e in intensities_header]

for line in f:
    fields = line.split()
    intensities[fields[0]] = [float(e) for e in fields[1:]]

f.close()

f = open(genotypes_fname)
g = open(output_fname,'w')

genotypes_header = f.readline().split()
genotypes_header.pop(0)

genotypes_header = [fk.extract_na(e) for e in genotypes_header]

print intensities_header,len(intensities_header)
print genotypes_header,len(genotypes_header)

matchup = [intensities_header.index(e) for e in genotypes_header]

cluster_intensities = {}

def float_format(x):
    return "%2.4f" % x

for line in f:
    fields = line.split()
    cnv = fields[0]
    print cnv
    genotypes = fields[1:]

    unique_genotypes = fk.unique(genotypes)
    unique_genotypes.sort()
    if unique_genotypes[0] == '-1':
        unique_genotypes.pop(0)
    if len(unique_genotypes) == 0:
        continue
    total_genotypes = 0
    if cnv not in intensities:
        print "cnv " + cnv + " not found in intensities"
        continue
    for genotype in unique_genotypes:
        genotype_indices = fk.indices(genotypes,genotype)
        relevant_intensities_indices = fk.arbslice(matchup,genotype_indices)
        relevant_intensities = fk.arbslice(intensities[cnv],
                                           relevant_intensities_indices)
        cluster_intensities[genotype] = relevant_intensities
        total_genotypes += len(relevant_intensities)
    g.write(cnv)
    g.write(' ' + str(len(unique_genotypes)))
    for genotype in unique_genotypes:
        g.write(' ' + genotype)
    for genotype in unique_genotypes:
        g.write(' ' + float_format(len(cluster_intensities[genotype]) /
                                   total_genotypes))
    for genotype in unique_genotypes:
        g.write(' ' + float_format(fk.mean(cluster_intensities[genotype])))
    for genotype in unique_genotypes:
        var = fk.variance(cluster_intensities[genotype])
        if (var < min_variance):
            var = min_variance
        if str(var) == 'NaN':
            var = min_variance
        g.write(' ' + float_format(var))
    g.write('\n')

f.close()
