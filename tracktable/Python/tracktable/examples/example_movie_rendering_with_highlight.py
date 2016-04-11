# Copyright (c) 2014, Sandia Corporation.  All rights
# reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""example_trajectory_rendering - Arguments and code for drawing trajectories

Once we have a set of trajectories in memory we can make decisions
about how they should look on screen.  That includes...

* How should the line segments in the trajectory be colored?

* What should the line width for each segment be?

* Should there be a dot at the head of the trajectory?  What size and
  color?

* What layer (Z-order) should the trajectories live in?

The convenience methods in this file will render a single group of
trajectories.  You can render several groups by instantiating several
of them.
"""

from __future__ import print_function, division, absolute_import

import matplotlib.animation
from matplotlib import pyplot
import datetime
import shlex
import pdb

from tracktable.core import Timestamp
from tracktable.core.timestamp import SimpleTimeZone
from tracktable.filter.trajectory import ClipToTimeWindow as ClipTrajectoryToTimeWindow, FilterByBoundingBox as FilterTrajectoriesByBoundingBox
from tracktable.render import clock
from tracktable.feature import annotations
from tracktable.examples import example_trajectory_rendering

ANNOTATED_TRAJECTORIES = None
HIGHLIGHT_ANNOTATED_TRAJECTORIES = None

# ----------------------------------------------------------------------

def setup_encoder(encoder='ffmpeg',
                  codec=None,
                  encoder_args=list(),
                  movie_title='Tracktable Movie',
                  movie_artist='Tracktable Trajectory Toolkit',
                  movie_comment='',
                  fps=20,
                  **kwargs):

    if encoder not in matplotlib.animation.writers.list():
        raise KeyError("Movie encoder {} is not available.  This system has the following encoders available: {}".format(encoder, matplotlib.animation.writers.list()))

    movie_metadata = { 'title': movie_title,
                       'artist': movie_artist,
                       'comment': movie_comment }

    if type(encoder_args) is str or type(encoder_args) is unicode:
        encoder_args = shlex.split(encoder_args)

#    print("setup_encoder: encoder_args are '{}' with type {}".format(encoder_args, type(encoder_args)))

    writer = matplotlib.animation.writers[encoder]( fps=fps,
                                                    codec=codec,
                                                    metadata=movie_metadata,
                                                    extra_args=encoder_args )


    return writer

# ----------------------------------------------------------------------

def annotate_trajectories(trajectory_source,
                          trajectory_color_type="scalar",
                          trajectory_color="progress",
                          **kwargs):
    """Decorate trajectories with an appropriate scalar.

    The user can specify different scalars to use to color
    trajectories as well as simple, static colors.  This is a
    convenience function to set those up and decorate all the
    trajectories in advance so that we don't need to duplicate effort
    at render time.

    Args:
      trajectory_source:     Iterable of trajectories
      trajectory_color_type: 'scalar' or 'constant'
      trajectory_color:      color name, hex string or name of a trajectory scalar

    Raises:
      KeyError: if trajectory_color_type is not 'scalar' or 'constant'
      KeyError: if trajectory_color_type is 'scalar' and the user asked for a function that isn't registered

    Returns:
      An iterable of trajectories that have had scalars computed
    """

    print("annotate_trajectories: trajectory color type is {}, trajectory color is {}".format(trajectory_color_type, trajectory_color))

    if trajectory_color_type == 'scalar':
        print("Retrieving annotation function for trajectory scalar function {}".format(trajectory_color))
        annotator = annotations.retrieve_feature_function(trajectory_color)
        def annotation_generator():
            for trajectory in trajectory_source:
                yield(annotator(trajectory))

        return annotation_generator()
    else:
        return trajectory_source

# ----------------------------------------------------------------------

def compute_trajectory_time_bounds(trajectories):

    """Compute the start and end times for a group of trajectories

    Args:
       trajectories: iterable of trajectories

    Returns:
       (start_time, end_time) - both Timestamp objects
    """

    start_time = None
    end_time = None

    for traj in trajectories:
        if len(traj) == 0:
            continue

        if start_time is None:
            start_time = traj[0].timestamp
            end_time = traj[-1].timestamp
        else:
            start_time = min(start_time, traj[0].timestamp)
            end_time = max(end_time, traj[-1].timestamp)

    return (start_time, end_time)


# ----------------------------------------------------------------------

def render_trajectories_for_frame(frame_time,
                                  trail_start_time,
                                  main_trajectories,
                                  basemap,
                                  axes=None,
                                  render_args=dict(),
                                  frame_number=None,
                                  highlight_trajectories=None,
                                  highlight_render_args=None):

    clipped_trajectories = ClipTrajectoryToTimeWindow()
    clipped_trajectories.input = main_trajectories
    clipped_trajectories.start_time = trail_start_time
    clipped_trajectories.end_time = frame_time

    clip_result_main = list(clipped_trajectories.trajectories())

    frame_data = example_trajectory_rendering.render_annotated_trajectories(
        basemap=basemap,
        trajectory_source=clip_result_main,
        axes=axes,
        **render_args)

    if highlight_trajectories is not None and len(highlight_trajectories) > 0:
        clipped_highlight = ClipTrajectoryToTimeWindow()
        clipped_highlight.input = highlight_trajectories
        clipped_highlight.start_time = trail_start_time
        clipped_highlight.end_time = frame_time

        clip_result_highlight = list(clipped_highlight.trajectories())
        frame_data += example_trajectory_rendering.render_annotated_trajectories(
            basemap=basemap,
            trajectory_source=clip_result_highlight,
            axes=axes,
            **highlight_render_args)

    return frame_data;

# ----------------------------------------------------------------------

def format_time(timestamp, utc_offset=0, timezone_name=''):
    minutes = timestamp.time().minute
    minutes = 15 * int(minutes / 15)
    local_timezone = SimpleTimeZone(hours=utc_offset)
    newtime = timestamp.replace(minute=minutes).astimezone(local_timezone)

    timestring = Timestamp.to_string(newtime, format_string='%Y-%m-%d %H:%M', include_tz=False)
    return timestring


# ----------------------------------------------------------------------

def cleanup_frame(artists):
    for artist in artists:
        artist.remove()

# ----------------------------------------------------------------------

def render_trajectory_movie(movie_writer,
                            basemap,
                            main_trajectories,
                            num_frames,
                            trail_duration,
                            first_frame=0,
                            num_frames_overall=None,
                            figure=None,
                            dpi=100,
                            filename='movie.mp4',
                            start_time=None,
                            end_time=None,
                            savefig_kwargs=dict(),
                            trajectory_rendering_args=dict(),
                            frame_batch_size=100,
                            utc_offset=0,
                            timezone_label=None,
                            highlight_trajectories=None,
                            axes=None):

#    pdb.set_trace()

    if timezone_label is None:
        timezone_label = ''

    local_savefig_kwargs = dict(savefig_kwargs)
    local_trajectory_rendering_args = dict(trajectory_rendering_args)

    # First, filter down to just the trajectories that intersect the map
    main_bbox_filter = FilterTrajectoriesByBoundingBox()
    main_bbox_filter.input = main_trajectories
    main_bbox_filter.bounding_box = ( ( basemap.llcrnrlon,
                                        basemap.llcrnrlat ),
                                      ( basemap.urcrnrlon,
                                        basemap.urcrnrlat ) )
    main_trajectories_on_map = list(main_bbox_filter.trajectories())

    highlight_bbox_filter = FilterTrajectoriesByBoundingBox()
    highlight_bbox_filter.input = highlight_trajectories
    highlight_bbox_filter.bounding_box =  ( ( basemap.llcrnrlon,
                                              basemap.llcrnrlat ),
                                            ( basemap.urcrnrlon,
                                              basemap.urcrnrlat ) )
    highlight_trajectories_on_map = list(highlight_bbox_filter.trajectories())
    highlight_rendering_args = dict(trajectory_rendering_args)

    global ANNOTATED_TRAJECTORIES
    if not ANNOTATED_TRAJECTORIES:
        print("Annotating trajectories (should only happen once)")
        annotated_trajectories = list(annotate_trajectories(main_trajectories_on_map,
                                                            **local_trajectory_rendering_args))
        ANNOTATED_TRAJECTORIES = annotated_trajectories

        if len(highlight_trajectories_on_map) > 0:
            highlight_rendering_args['trajectory_initial_linewidth'] = 2
            highlight_rendering_args['trajectory_final_linewidth'] = 1
            highlight_rendering_args['trajectory_color'] = 'white'
            highlight_annotated_trajectories = list(annotate_trajectories(highlight_trajectories_on_map,
                                                                          **highlight_rendering_args))
            HIGHLIGHT_ANNOTATED_TRAJECTORIES = highlight_annotated_trajectories
    else:
        print("Re-using trajectory annotations")
        annotated_trajectories = ANNOTATED_TRAJECTORIES
        highlight_annotated_trajectories = HIGHLIGHT_ANNOTATED_TRAJECTORIES

    print("Annotated trajectories retrieved.")

    if local_trajectory_rendering_args['trajectory_color_type'] == 'static':
        local_trajectory_rendering_args['trajectory_colormap'] = example_trajectory_rendering.make_constant_colormap(local_trajectory_rendering_args['trajectory_color'])

    (data_start_time, data_end_time) = compute_trajectory_time_bounds(annotated_trajectories)
    if end_time is None:
        end_time = data_end_time
    else:
        end_time = Timestamp.from_any(end_time)
    if start_time is None:
        start_time = data_start_time
    else:
        start_time = Timestamp.from_any(start_time)

    print("INFO: Movie covers time span from {} to {}".format(
        start_time.strftime("%Y-%m-%d %H:%M:%S"),
        end_time.strftime("%Y-%m-%d %H:%M:%S")))
    print("INFO: Data set covers time span from {} to {}".format(
        data_start_time.strftime("%Y-%m-%d %H:%M:%S"),
        data_end_time.strftime("%Y-%m-%d %H:%M:%S")))

    if num_frames_overall is None:
        num_frames_overall = num_frames
    frame_duration = (end_time - start_time) / num_frames_overall
    first_frame_time = start_time + trail_duration

    if (local_trajectory_rendering_args['trajectory_color_type'] == 'scalar' and
        local_trajectory_rendering_args.get('trajectory_color', None) is not None):
        scalar_accessor = annotations.retrieve_feature_accessor(local_trajectory_rendering_args['trajectory_color'])
    else:
        scalar_accessor = None

    # We've handled these args ourselves - don't pass them on
    del local_trajectory_rendering_args['trajectory_color_type']
    del local_trajectory_rendering_args['trajectory_color']

    if scalar_accessor is not None:
        local_trajectory_rendering_args['trajectory_scalar_accessor'] = scalar_accessor

    def frame_time(which_frame):
        return first_frame_time + which_frame * frame_duration


    def my_format_time(timestamp):
        minutes = timestamp.time().minute
        minutes = 15 * int(minutes / 15)
        local_timezone = SimpleTimeZone(hours=utc_offset)
        newtime = timestamp.replace(minute=minutes).astimezone(local_timezone)

        timestring = Timestamp.to_string(newtime, format_string='%Y-%m-%d\n%H:%M {}'.format(
            timezone_label), include_tz=False)

        return timestring



    ## TODO Add arguments to control this
    clock_artist = clock.digital_clock(frame_time(0),
                                       my_format_time,
                                       (0.95, 0.85),
                                       ha='right',
                                       va='baseline',
                                       color='white',
                                       size=18,
                                       backgroundcolor='black',
                                       zorder=20)[0]

    if figure is None:
        figure = pyplot.gcf()

    print("Rendering to {}".format(filename))
    current_trajectory_batch = None
    with movie_writer.saving(figure, filename, dpi):

        for i in range(first_frame, first_frame+num_frames):

            current_time = frame_time(i)
            trail_start_time = frame_time(i) - trail_duration

            print("Rendering frame {}: current_time {}, trail_start_time {}".format(
                i,
                current_time.strftime("%Y-%m-%d %H:%M:%S"),
                trail_start_time.strftime("%Y-%m-%d %H:%M:%S")))

            current_trajectory_batch = list(annotated_trajectories)
#            print("Frame {}: trajectory batch contains {} items".format(i, len(current_trajectory_batch)))

#            if (i+1) % 10 == 0:
#                print("Rendering frame {}.  Batch extends to frame {}.".format(i, first_frame+num_frames-1))

            frame_data = render_trajectories_for_frame(
                frame_time=current_time,
                trail_start_time=trail_start_time,
                trajectories=current_trajectory_batch,
                basemap=basemap,
                axes=axes,
                render_args=local_trajectory_rendering_args,
                frame_number=i
                )

            if len(highlight_annotated_trajectories) > 0:
                frame_data += render_trajectories_for_frame(
                    frame_time=current_frame,
                    trail_start_time=trail_start_time,
                    trajectories=highlight_annotated_trajectories,
                    basemap=basemap,
                    axes=axes,
                    render_args=highlight_rendering_args,
                    frame_number=i
                )

            clock_artist.set_text(my_format_time(current_time))

            next_filename = 'test_frame_{}.png'.format(i)
            movie_writer.grab_frame(**local_savefig_kwargs)
            cleanup_frame(frame_data)

            current_time += frame_duration
            trail_start_time += frame_duration
