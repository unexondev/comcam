from pyrealsense2 import option
from pyrealsense2 import sensor as rs_sensor

from time import sleep

import logging

logger = logging.getLogger(__name__)


class OptimizationMixin:


    def apply_optimizations(self, sensor : rs_sensor):
        return all(opt(self, sensor) for opt in self.optimizations)


    def optimize_low_stereo_temperature(self, sensor : rs_sensor):

        logger.debug("Optimizing low stereo temperature for depth sensor...")

        # early exit if not depth sensor
        if not sensor.is_depth_sensor():
            logger.debug("Not a depth sensor, skipping...")
            return True

        asic_temp_min = self.opts.asic_temp_range_stereo[0]
        projector_temp_min = self.opts.projector_temp_range_stereo[0]

        prf_max_fps = None
        for prf in sensor.get_stream_profiles():
            if prf_max_fps is None or prf.fps() > prf_max_fps.fps():
                prf_max_fps = prf

        try:
            sensor.open(prf_max_fps) # turn on the sensor
        except RuntimeError:
            logger.debug("Couldn't turn the sensor on, skipping...")
            return False

        try:
            sensor.start(lambda _ : None) # start stressing
        except RuntimeError:
            logger.debug("Couldn't start the sensor, skipping...")
            return False

        while True:

            opt_asic_temp = option.asic_temperature
            opt_projector_temp = option.projector_temperature

            opts_valid = sensor.get_supported_options()

            asic_temp = None
            projector_temp = None

            if opt_asic_temp in opts_valid:
                asic_temp = sensor.get_option(opt_asic_temp)
            if opt_projector_temp in opts_valid:
                projector_temp = sensor.get_option(opt_projector_temp)

            logger.debug(
                "%-25s %.1f - min. requested: %.1f",
                "ASIC temperature:",
                asic_temp,
                asic_temp_min
            )
            logger.debug(
                "%-25s %.1f - min. requested: %.1f",
                "Projector temperature:",
                projector_temp,
                projector_temp_min
            )

            asic_temp_ok = asic_temp is None or asic_temp >= asic_temp_min
            projector_temp_ok = projector_temp is None or projector_temp >= projector_temp_min
        
            if asic_temp_ok and projector_temp_ok:
                logger.debug("Done optimizing low temperatures for depth sensor.")

                sensor.stop() # stop stressing
                sensor.close() # turn off the sensor

                break # break the loop check

            sleep(0.5)


    optimizations = {
        optimize_low_stereo_temperature,
    }