# Copyright (c) 2015, Sandia Corporation.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from __future__ import division, print_function, absolute_import

import random
import sys
from six.moves import range

from tracktable.analysis.dbscan import compute_cluster_labels

# Test dbscan in 3 dimensions

def cluster_points_around(central_point, span, count):
    start_point = [ (c - 0.5 * d) for (c, d) in zip(central_point, span) ]

    delta = [ s / float(count-1) for s in span ]

    points = []

    for i in range(count):
        x = start_point[0] + i * delta[0]
        for j in range(count):
            y = start_point[1] + j * delta[1]
            for k in range(count):
                z = start_point[2] + k * delta[2]
                points.append((x, y, z))

    return points

# ----------------------------------------------------------------------

def place_corner_clusters():
    all_points = []

    corners = [
        (0, 0, 0),
        (1, 0, 0),
        (0, 1, 0),
        (1, 1, 0),
        (0, 0, 1),
        (1, 0, 1),
        (0, 1, 1),
        (1, 1, 1)
        ]

    for corner in corners:
        all_points.extend(cluster_points_around(corner, (0.1, 0.1, 0.1), 8))

    return all_points

# ----------------------------------------------------------------------

def place_noise_points(center, span, count):
    all_points = []

    for point_id in range(count):
        x = random.uniform(center[0] - 0.5 * span[0], center[0] + 0.5 * span[0])
        y = random.uniform(center[1] - 0.5 * span[1], center[1] + 0.5 * span[1])
        z = random.uniform(center[2] - 0.5 * span[2], center[2] + 0.5 * span[2])
        all_points.append([x, y, z])

    return all_points

# ----------------------------------------------------------------------

def test_clusters():
    random.seed(0)

    print("Creating points")
    corner_points = place_corner_clusters()
    noise_points = place_noise_points([0.5, 0.5, 0.5], [10, 10, 10], 100)

    all_points = corner_points + noise_points

    print("Learning cluster IDs")
    cluster_ids = compute_cluster_labels(all_points,
                                         [0.05, 0.05, 0.05],
                                         4)

    print("Cluster IDs: {}".format(cluster_ids))

# ----------------------------------------------------------------------

def main():
    test_clusters()
    return 0

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())
    

          
