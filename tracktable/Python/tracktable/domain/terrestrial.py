# Copyright (c) 2014, Sandia Corporation.
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

from ._terrestrial import BasePointTerrestrial as BasePoint
from ._terrestrial import TrajectoryPointTerrestrial as TrajectoryPoint
from ._terrestrial import TrajectoryTerrestrial as Trajectory
from ._terrestrial import BasePointReaderTerrestrial as BasePointReader
from ._terrestrial import TrajectoryPointReaderTerrestrial as TrajectoryPointReader
from ._terrestrial import TrajectoryReaderTerrestrial as TrajectoryReader
from ._terrestrial import BoundingBoxTerrestrial as BoundingBox
from ._terrestrial import BasePointWriterTerrestrial as BasePointWriter
from ._terrestrial import TrajectoryPointWriterTerrestrial as TrajectoryPointWriter
from ._terrestrial import TrajectoryWriterTerrestrial as TrajectoryWriter

domain_classes = {
    'BasePoint': BasePoint,
    'TrajectoryPoint': TrajectoryPoint,
    'BasePointReader': BasePointReader,
    'TrajectoryPointReader': TrajectoryPointReader,
    'TrajectoryReader': TrajectoryReader,
    'Trajectory': Trajectory,
    'BoundingBox': BoundingBox,
    'BasePointWriter': BasePointWriter,
    'TrajectoryPointWriter': TrajectoryPointWriter,
    'TrajectoryWriter': TrajectoryWriter
}

for domain_class in [
        BasePoint,
        TrajectoryPoint,
        Trajectory,
        BasePointReader,
        TrajectoryPointReader,
        TrajectoryReader,
        BasePointWriter,
        TrajectoryPointWriter,
        TrajectoryWriter,
        BoundingBox ]:
    domain_class.domain_classes = domain_classes
