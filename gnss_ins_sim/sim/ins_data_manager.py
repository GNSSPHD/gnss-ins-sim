# -*- coding: utf-8 -*-
# Filename: ins_data_manager.py

"""
Manage all possible generated in an INS solution.
Created on 2018-04-24
@author: dongxiaoguang
"""

import numpy as np
import matplotlib.pyplot as plt
from . import sim_data
from .sim_data import Sim_data
from ..attitude import attitude
from ..kml_gen import kml_gen

class InsDataMgr(object):
    '''
    A class that manage all data generated in an INS solution. For example, reference data,
    sensor data, algorithm results. These data can be saved to files or plot in figures.
    '''
    def __init__(self, fs, ref_frame=0):
        '''
        Args:
            fs: [fs_imu, fs_gps, fs_mag], Hz.
                fs_imu: The sample rate of IMU.
                fs_gps: The sample rate of GPS.
                fs_mag: not used now. The sample rate of the magnetometer is
                    the same as that of the imu.

            ref_frame: reference frame used as the navigation frame,
                        0: NED (default), with x axis pointing along geographic north,
                            y axis pointing eastward,
                            z axis pointing downward.
                        1: a virtual inertial frame with constant g,
                            x axis pointing along magnetic north,
                            z axis pointing along g,
                            y axis completing a right-handed coordinate system.
                            Notice: For this virtual inertial frame, position is indeed the sum of
                            the initial position in ecef and the relative position in the virutal
                            inertial frame.
        '''
        # sample rate
        self.fs = Sim_data(name='fs',\
                           description='Sample frequency of IMU',\
                           units=['Hz'],\
                           plottable=False)
        self.fs_gps = Sim_data(name='fs_gps',\
                            description='Sample frequency of GPS',\
                            units=['Hz'],\
                            plottable=False)
        self.fs_mag = Sim_data(name='fs_mag',\
                            description='Sample frequency of Magnetometer',\
                            units=['Hz'],\
                            plottable=False)
        # reference frame
        self.ref_frame = Sim_data(name='ref_frame',\
                                    description='Reference frame',\
                                    plottable=False)
        if ref_frame == 0 or ref_frame == 1:
            self.ref_frame.data = ref_frame
        else:
            self.ref_frame.data = 0      # default frame is NED

        ########## possible data generated by simulation ##########
        # reference data
        self.time = Sim_data(name='time',\
                             description='sample time',\
                             units=['sec'])
        self.gps_time = Sim_data(name='gps_time',\
                                 description='GPS sample time',\
                                 units=['sec'])
        self.ref_pos = Sim_data(name='ref_pos',\
                                description='true pos in the navigation frame',\
                                units=['rad', 'rad', 'm'],\
                                output_units=['deg', 'deg', 'm'],\
                                legend=['ref_pos_lat', 'ref_pos_lon', 'ref_pos_alt'])
        self.ref_vel = Sim_data(name='ref_vel',\
                                description='true vel in the body frame',\
                                units=['m/s', 'm/s', 'm/s'],\
                                legend=['ref_vel_N', 'ref_vel_E', 'ref_vel_D'])
        self.ref_att_euler = Sim_data(name='ref_att_euler',\
                                description='true attitude (Euler angles, ZYX)',\
                                units=['rad', 'rad', 'rad'],\
                                output_units=['deg', 'deg', 'deg'],\
                                legend=['ref_Yaw', 'ref_Pitch', 'ref_Roll'])
        self.ref_att_quat = Sim_data(name='ref_att_quat',\
                                     description='true attitude (quaternion)',\
                                     legend=['q0', 'q1', 'q2', 'q3'])
        self.ref_gyro = Sim_data(name='ref_gyro',\
                                 description='true angular velocity',\
                                 units=['rad/s', 'rad/s', 'rad/s'],\
                                 output_units=['deg/s', 'deg/s', 'deg/s'],\
                                 legend=['ref_gyro_x', 'ref_gyro_y', 'ref_gyro_z'])
        self.ref_accel = Sim_data(name='ref_accel',\
                                  description='True accel',\
                                  units=['m/s^2', 'm/s^2', 'm/s^2'],\
                                  legend=['ref_accel_x', 'ref_accel_y', 'ref_accel_z'])
        self.ref_gps = Sim_data(name='ref_gps',\
                                description='true GPS pos/vel',\
                                units=['rad', 'rad', 'm', 'm/s', 'm/s', 'm/s'],\
                                output_units=['deg', 'deg', 'm', 'm/s', 'm/s', 'm/s'],\
                                legend=['ref_gps_lat', 'ref_gps_lon', 'ref_gps_alt',\
                                        'ref_gps_vN', 'ref_gps_vE', 'ref_gps_vD'])
                                # downsampled true pos/vel
        self.ref_mag = Sim_data(name='ref_mag',\
                                description='true magnetic field',\
                                units=['uT', 'uT', 'uT'],\
                                legend=['ref_mag_x', 'ref_mag_y', 'ref_mag_z'])
        # sensor measurements
        self.gyro = Sim_data(name='gyro',\
                             description='gyro measurements',\
                             units=['rad/s', 'rad/s', 'rad/s'],\
                             output_units=['deg/s', 'deg/s', 'deg/s'],\
                             legend=['gyro_x', 'gyro_y', 'gyro_z'])
        self.accel = Sim_data(name='accel',\
                              description='accel measurements',\
                              units=['m/s^2', 'm/s^2', 'm/s^2'],\
                              legend=['accel_x', 'accel_y', 'accel_z'])
        self.gps = Sim_data(name='gps',\
                            description='GPS measurements',\
                            units=['rad', 'rad', 'm', 'm/s', 'm/s', 'm/s'],\
                            output_units=['deg', 'deg', 'm', 'm/s', 'm/s', 'm/s'],\
                            legend=['gps_lat', 'gps_lon', 'gps_alt',\
                                    'gps_vN', 'gps_vE', 'gps_vD'])
        self.mag = Sim_data(name='mag',\
                            description='magnetometer measurements',\
                            units=['uT', 'uT', 'uT'],\
                            legend=['mag_x', 'mag_y', 'mag_z'])
        # calibration algorithm output
        self.gyro_cal = Sim_data(name='gyro_cal',\
                                 description='gyro measurements after factory calibration',\
                                 units=['rad/s', 'rad/s', 'rad/s'],\
                                 output_units=['deg/s', 'deg/s', 'deg/s'],\
                                 legend=['gyro_x', 'gyro_y', 'gyro_z'])
        self.accel_cal = Sim_data(name='accel_cal',\
                                  description='accel measurements after factory calibration',\
                                  units=['m/s^2', 'm/s^2', 'm/s^2'],\
                                  legend=['accel_x', 'accel_y', 'accel_z'])
        self.mag_cal = Sim_data(name='mag_cal',\
                                description='magnetometer measurements after SI&HI calibration',\
                                units=['uT', 'uT', 'uT'],\
                                legend=['mag_x', 'mag_y', 'mag_z'])
        self.soft_iron = Sim_data(name='soft_iron',\
                                description='soft iron calibration matrix',\
                                plottable=False)
        self.hard_iron = Sim_data(name='hard_iron',\
                                description='hard iron',\
                                units=['uT', 'uT', 'uT', 'uT'],\
                                legend=['offset_x', 'offset_y', 'offset_z', 'radius'],\
                                plottable=False)
        # fusion algorithm output
        self.algo_time = Sim_data(name='algo_time',\
                                  description='sample time from algo',\
                                  units=['sec'])
        self.pos = Sim_data(name='pos',\
                            description='simulation position from algo',\
                            units=['rad', 'rad', 'm'],\
                            output_units=['deg', 'deg', 'm'],\
                            legend=['pos_lat', 'pos_lon', 'pos_alt'])
        self.vel = Sim_data(name='vel',\
                            description='simulation velocity from algo',\
                            units=['m/s', 'm/s', 'm/s'],\
                            legend=['vel_N', 'vel_E', 'vel_D'])
        self.att_quat = Sim_data(name='att_quat',\
                                 description='simulation attitude (quaternion)  from algo',\
                                 legend=['q0', 'q1', 'q2', 'q3'])
        self.att_euler = Sim_data(name='att_euler',
                                  description='simulation attitude (Euler, ZYX)  from algo',\
                                  units=['rad', 'rad', 'rad'],\
                                  output_units=['deg', 'deg', 'deg'],\
                                  legend=['Yaw', 'Pitch', 'Roll'])
        self.wb = Sim_data(name='wb',\
                           description='gyro bias estimation',\
                           units=['rad/s', 'rad/s', 'rad/s'],\
                           output_units=['deg/s', 'deg/s', 'deg/s'],\
                           legend=['gyro_bias_x', 'gyro_bias_y', 'gyro_bias_z'])
        self.ab = Sim_data(name='ab',\
                           description='accel bias estimation',\
                           units=['m/s^2', 'm/s^2', 'm/s^2'],\
                           legend=['accel_bias_x', 'accel_bias_y', 'accel_bias_z'])
        self.ad_gyro = Sim_data(name='ad_gyro',\
                                description='Allan deviation of gyro',\
                                units=['rad/s', 'rad/s', 'rad/s'],\
                                output_units=['deg/hr', 'deg/hr', 'deg/hr'],\
                                logx=True, logy=True,\
                                legend=['AD_wx', 'AD_wy', 'AD_wz'])
        self.ad_accel = Sim_data(name='ad_accel',\
                                 description='Allan deviation of accel',\
                                 units=['m/s^2', 'm/s^2', 'm/s^2'],\
                                 logx=True, logy=True,\
                                 legend=['AD_ax', 'AD_ay', 'AD_az'])
        # if using virtual inertial frame
        if self.ref_frame.data == 1:
            # position units and legned
            self.ref_pos.units = ['m', 'm', 'm']
            self.ref_pos.output_units = ['m', 'm', 'm']
            self.ref_pos.legend = ['ref_pos_x', 'ref_pos_y', 'ref_pos_z']
            self.pos.units = ['m', 'm', 'm']
            self.pos.output_units = ['m', 'm', 'm']
            self.pos.legend = ['pos_x', 'pos_y', 'pos_z']
            # velocity units and legend
            self.ref_vel.legend = ['ref_vel_x', 'ref_vel_y', 'ref_vel_z']
            self.vel.legend = ['vel_x', 'vel_y', 'vel_z']
            # GPS units and legend
            self.ref_gps.units = ['m', 'm', 'm', 'm/s', 'm/s', 'm/s']
            self.ref_gps.output_units = ['m', 'm', 'm', 'm/s', 'm/s', 'm/s']
            self.ref_gps.legend = ['ref_gps_x', 'ref_gps_y', 'ref_gps_z',\
                                   'ref_gps_vx', 'ref_gps_vy', 'ref_gps_vz']
            self.gps.units = ['m', 'm', 'm', 'm/s', 'm/s', 'm/s']
            self.gps.output_units = ['m', 'm', 'm', 'm/s', 'm/s', 'm/s']
            self.gps.legend = ['gps_x', 'gps_y', 'gps_z',\
                               'gps_vx', 'gps_vy', 'gps_vz']
        ########## all data ##########
        # __all include all data that may occur in an INS solution.
        self.__all = {
            # input data
            self.fs.name: self.fs,
            self.fs_gps.name: self.fs_gps,
            self.fs_mag.name: self.fs_mag,
            self.ref_frame.name: self.ref_frame,
            self.time.name: self.time,
            self.gps_time.name: self.gps_time,
            self.ref_pos.name: self.ref_pos,
            self.ref_vel.name: self.ref_vel,
            self.ref_att_euler.name: self.ref_att_euler,
            self.ref_att_quat.name: self.ref_att_quat,
            self.ref_gyro.name: self.ref_gyro,
            self.ref_accel.name: self.ref_accel,
            self.ref_gps.name: self.ref_gps,
            self.ref_mag.name: self.ref_mag,
            # sensor data
            self.gyro.name: self.gyro,
            self.accel.name: self.accel,
            self.gps.name: self.gps,
            self.mag.name: self.mag,
            # calibration algorithm output
            self.gyro_cal.name: self.gyro_cal,
            self.accel_cal.name: self.accel_cal,
            self.mag_cal.name: self.mag_cal,
            self.soft_iron.name: self.soft_iron,
            self.hard_iron.name: self.hard_iron,
            # fusion algorithm output
            self.algo_time.name: self.algo_time,
            self.pos.name: self.pos,
            self.vel.name: self.vel,
            self.att_quat.name: self.att_quat,
            self.att_euler.name: self.att_euler,
            self.wb.name: self.wb,
            self.ab.name: self.ab,
            self.ad_gyro.name: self.ad_gyro,
            self.ad_accel.name: self.ad_accel
            }
        # all available data that really occur in the simulation.
        self.available = []
        self.available.append(self.ref_frame.name)
        if fs[0] is not None:
            self.fs.data = fs[0]
            self.available.append(self.fs.name)
        else:
            raise ValueError('IMU sampling frequency cannot be None.')
        if fs[1] is not None:
            self.fs_gps.data = fs[1]
            self.available.append(self.fs_gps.name)
        if fs[2] is not None:
            self.fs_mag.data = fs[2]
            self.available.append(self.fs_mag.name)
        # the following will not be saved
        self.__do_not_save = [self.fs.name, self.fs_gps.name,\
                            self.fs_mag.name, self.ref_frame.name]
        # algorithm output
        self.__algo_output = []
        # associated data mapping. If the user want Euler angles, but only quaternions are
        # available, Euler angles will be automatically calculated, added to self.available and
        # returned.
        self.__data_map = {self.ref_att_euler.name: [self.ref_att_quat, self.__euler2quat_zyx],
                           self.ref_att_quat.name: [self.ref_att_euler, self.__quat2euler_zyx],
                           self.att_euler.name: [self.att_quat, self.__euler2quat_zyx],
                           self.att_quat.name: [self.att_euler, self.__quat2euler_zyx]}

    def add_data(self, data_name, data, key=None, units=None):
        '''
        Add data to available.
        Args:
            data_name: data name
            data: a scalar, a numpy array or a dict of the above two. If data is a dict, each
                value in it should be of same type (scalr or numpy array), same size and same
                units.
            key: There are more than one set of data, key is an index of data added this time.
                If key is None, data can be a scalr, a numpy array or a dict of the above two.
                If key is a valid dict key, data can be a scalr or a numpy.
            units: Units of the data. If you know clearly no units convertion is needed, set
                units to None. If you do not know what units are used in the class InsDataMgr,
                you'd better provide the units of the data. Units convertion will be done
                automatically.
                If data is a scalar, units should be a list of one string to define its unit.
                If data is a numpy of size(m,n), units should be a list of n strings
                to define the units.
                If data is a dict, units should be the same as the above two depending on if
                each value in the dict is a scalr or a numpy array.
        '''
        if data_name in self.__all:
            self.__all[data_name].add_data(data, key, units)
            if data_name not in self.available:
                self.available.append(data_name)
        else:
            raise ValueError("Unsupported data: %s."%data_name)

    def set_algo_output(self, algo_output):
        '''
        Tell data manager what output an algorithm provide
        Args:
            algo_output: a list of data names.
        '''
        for i in algo_output:
            if self.is_supported(i):
                self.__algo_output.append(i)
            else:
                raise ValueError("Unsupported algorithm output: %s."% i)


    def get_data(self, data_names):
        '''
        Get data section of data_names.
        Args:
            data_names: a list of data names
        Returns:
            data: a list of data corresponding to data_names.
            If there is any unavailable data in data_names, return None
        '''
        data = []
        for i in data_names:
            if i in self.available:
                data.append(self.__all[i].data)
            else:
                print('%s is not available.'% i)
                return None
        return data

    def get_data_all(self, data_name):
        '''
        get the Sim_data object accroding to data_name
        '''
        if data_name in self.__all:
            return self.__all[data_name]
        else:
            return None

    def get_error_stat(self, data_name, end_point=False, angle=False, use_output_units=False):
        '''
        Get error statistics of data_name.
        Args:
            data_name: name of data whose error will be calculated.
            end_point: True if want to calculate only the end point error. In this case,
                the result contains statistics of end-point errors of multiple runs.
                False if want to calculate the process error. In this case, the result is
                a dict of statistics of process error of each simulatoin run.
                For example, if we want the end-point error of position from a free-integration
                algorithm ran for n times, the result is {'max': numpy.array([rx, ry, rz]),
                'avg': numpy.array([rx, ry, rz]), 'std': numpy.array([rx, ry, rz])}.
                If we want the process error of an attitude determination algorithm ran for n
                times, the result is {'max': a dict of numpy.array([yaw, pitch, roll]),
                                      'avg': a dict of numpy.array([yaw, pitch, roll]),
                                      'std': a dict of numpy.array([yaw, pitch, roll])}.
            angle: True if this is angle error. Angle error will be converted to be within
                [-pi, pi] before calculating statistics.
            use_output_units: use output units instead of inner units in which the data are
                stored. An automatic unit conversion is done.
        Returns:
            err_stat: error statistics.
        '''
        err_stat = None
        if end_point is True:
            # end-point error
            err_stat = self.__end_point_error_stat(data_name, angle)
        else:
            # process error
            err_stat = self.__process_error_stat(data_name, angle)
        # unit conversion
        if use_output_units:
            for i in err_stat:
                if isinstance(err_stat[i], dict):
                    for j in err_stat[i]:
                        err_stat[i][j] = sim_data.convert_unit(err_stat[i][j],\
                                                               self.__all[data_name].units,\
                                                               self.__all[data_name].output_units)
                else:
                    err_stat[i] = sim_data.convert_unit(err_stat[i],\
                                                        self.__all[data_name].units,\
                                                        self.__all[data_name].output_units)
        return err_stat

    def save_data(self, data_dir):
        '''
        save data to files
        Args:
            data_dir: Data files will be saved in data_idr
        Returns:
            data_saved: a list of data that are saved.
        '''
        data_saved = []
        for data in self.available:
            if data not in self.__do_not_save:
                # print('saving %s'% data)
                self.__all[data].save_to_file(data_dir)
                data_saved.append(data)
        return data_saved

    def plot(self, what_to_plot, keys, opt=None, extra_opt=''):
        '''
        Plot specified results.
        Args:
            what_to_plot: a string to specify what to plot. See manual for details.
            keys: specify the simulation data of multiple run. This can be an integer, or a list
                or tuple. Each element should be within [0, num_times-1]. Default is None, and
                plot data of all simulations.
            opt: a dict to specify plot options. its keys are composed of elements in what_to_plot.
                values can be:
                    'error': plot the error of the data specified by what_to_plot w.r.t ref
                    '3d': 3d plot
            extra_opt: strings to specify matplotlib properties.
        '''
        if what_to_plot in self.available:
            # get plot options
            ref = None
            plot3d = 0
            # this data has plot options?
            if isinstance(opt, dict):
                if what_to_plot in opt:
                    if opt[what_to_plot].lower() == '3d':
                        plot3d = 1
                    elif opt[what_to_plot].lower() == 'projection':
                        plot3d = 2
                    elif opt[what_to_plot].lower() == 'error':
                        # this data have reference, error can be calculated
                        ref_name = 'ref_' + what_to_plot
                        if ref_name in self.available:
                            ref = self.__all[ref_name]
                        else:
                            print(what_to_plot + ' has no reference.')
            # default x axis data
            x_axis = self.time
            # choose proper x axis data for specific y axis data
            if what_to_plot == self.ref_gps.name or what_to_plot == self.gps.name or\
                what_to_plot == self.gps_time.name:
                x_axis = self.gps_time
            elif what_to_plot in self.__algo_output and self.algo_time.name in self.available:
                x_axis = self.algo_time
            # plot
            # if data in what_to_plot and data in ref have different dimension, interp is needed.
            if ref is not None:
                # create tmp_ref in order not to change ref
                tmp_ref = Sim_data(name=ref.name,\
                                   description=ref.description,\
                                   units=ref.units,\
                                   output_units=ref.output_units,\
                                   plottable=ref.plottable,\
                                   logx=ref.logx, logy=ref.logy,\
                                   grid=ref.grid,\
                                   legend=ref.legend)
                # interp data in ref to tmp_ref if needed
                if isinstance(self.__all[what_to_plot].data, dict):
                    last_key = None     # key of last interp data
                    for i in self.__all[what_to_plot].data:
                        # ref.data cannot be a dict, only one ref for each data is allowed
                        # data in what_to_plot can have different samples for different keys
                        # so each key should have its own reference data
                        if ref.data.shape[0] != self.__all[what_to_plot].data[i].shape[0]:
                            # if last interp dimension is the same, do not need same interp
                            if last_key is not None:
                                if tmp_ref.data[last_key].shape[0] ==\
                                    self.__all[what_to_plot].data[i].shape[0]:
                                    # print('using results from last interp')
                                    tmp_ref.data[i] = tmp_ref.data[last_key]
                                    continue
                            # interp
                            if self.algo_time.name in self.available and\
                                self.time.name in self.available:
                                tmp_ref.data[i] = self.__interp(self.algo_time.data[i],\
                                                                self.time.data, ref.data)
                                last_key = i
                            # no algo_time or time vars for interp, no error plot is available
                            else:
                                print('need interp for %s, but cannot do that.'% what_to_plot)
                                tmp_ref = None
                                break
                        else:
                            tmp_ref.data[i] = ref.data
                elif isinstance(self.__all[what_to_plot].data, np.ndarray):
                    if ref.data.shape[0] != self.__all[what_to_plot].data[i].shape[0]:
                        if self.algo_time.name in self.available and\
                            self.time.name in self.available:
                            tmp_ref.data[i] = self.__interp(self.algo_time.data[i],\
                                                            self.time.data, ref.data)
                        else:
                            tmp_ref = None
                    else:
                        tmp_ref.data[i] = ref.data
                else:# this is impossible
                    tmp_ref.data = ref.data
                self.__all[what_to_plot].plot(x_axis, key=keys, ref=tmp_ref,\
                                              plot3d=plot3d, extra_opt=extra_opt)
            else:
                self.__all[what_to_plot].plot(x_axis, key=keys, ref=None,\
                                              plot3d=plot3d, extra_opt=extra_opt)
        else:
            print('Unsupported plot: %s.'% what_to_plot)
            # print("Only the following data are available for plot:")
            # print(list(self.supported_plot.keys()))
            # raise ValueError("Unsupported data to plot: %s."%data)

    def save_kml_files(self, data_dir):
        '''
        generate kml files from reference position and simulation position.
        Args:
            data_dir: kml files are saved in data_dir
        '''
        convert_xyz_to_lla = False
        if self.ref_frame.data == 1:
            convert_xyz_to_lla = True
        # ref position
        if 'ref_pos' in self.available:
            kml_gen.kml_gen(data_dir,\
                            self.__all['ref_pos'].data,\
                            name='ref_pos',\
                            convert_to_lla=convert_xyz_to_lla)
        # simulation position
        if 'pos' in self.available:
            for i in self.__all['pos'].data.keys():
                pos_name = 'pos_' + str(i)
                kml_gen.kml_gen(data_dir,\
                                self.__all['pos'].data[i],\
                                name=pos_name,\
                                convert_to_lla=convert_xyz_to_lla)

    def is_supported(self, data_name):
        '''
        Tell if this set of data is supported or not
        '''
        return data_name in self.__all.keys()

    def __end_point_error_stat(self, data_name, angle=False):
        '''
        end-point error statistics
        '''
        if data_name not in self.available:
            print('__end_point_error_stat: %s is not available.'% data_name)
            return None
        ref_data_name = 'ref_' + data_name
        if ref_data_name not in self.available:
            print('%s has no reference.'% data_name)
            return None
        if isinstance(self.__all[data_name].data, dict):
            # a dict contains data of multiple runs
            err = []
            for i in self.__all[data_name].data:
                err.append(self.__all[data_name].data[i][-1, :] -\
                           self.__all[ref_data_name].data[-1, :])
            # convert list to np.array
            err = np.array(err)
            return self.__array_stat(err, angle)
        elif isinstance(self.__all[data_name].data, np.ndarray):
            err = self.__all[data_name].data[-1, :] - self.__all[ref_data_name].data[-1, :]
            return self.__array_stat(err, angle)
        else:
            print('Unsupported data type to calculate error statitics for %s'% data_name)
            return None

    def __process_error_stat(self, data_name, angle=False):
        '''
        process error statistics
        '''
        # data_name is available
        if data_name not in self.available:
            print('__process_error_stat: %s is not available.'% data_name)
            return None
        # reference of data_name is available
        ref_data_name = 'ref_' + data_name
        if ref_data_name not in self.available:
            print('%s has no reference.'% data_name)
            return None
        # begin to calculate error stat
        if isinstance(self.__all[data_name].data, dict):
            stat = {'max': {}, 'avg': {}, 'std': {}}
            ref_data = None
            for i in self.__all[data_name].data:
                # get raw reference data for first key in the dict, use reference from last
                # step for other keys to avoid multiple interps.
                if ref_data is None:
                    # use copy to avoid changing data if interp
                    ref_data = self.__all[ref_data_name].data.copy()
                # Interpolation. using ref_data to avoid multiple interps
                if ref_data.shape[0] != self.__all[data_name].data[i].shape[0]:
                    # print("%s has different number of samples from its reference."% data_name)
                    # print('Interpolation needed.')
                    if self.algo_time.name in self.available and self.time.name in self.available:
                        ref_data = self.__interp(self.algo_time.data[i],\
                                                 self.time.data, self.__all[ref_data_name].data)
                    else:
                        print("%s or %s is not available."% (self.algo_time.name, self.time.name))
                        return None
                # error stat
                err = self.__all[data_name].data[i] - ref_data
                tmp = self.__array_stat(err, angle)
                stat['max'][i] = tmp['max']
                stat['avg'][i] = tmp['avg']
                stat['std'][i] = tmp['std']
            return stat
        elif isinstance(self.__all[data_name].data, np.ndarray):
            ref_data = self.__all[ref_data_name].data.copy()
            # Interpolation
            if ref_data.shape[0] != self.__all[data_name].data.shape[0]:
                print("%s has different number of samples from its reference."% data_name)
                print('Interpolation needed.')
                if self.algo_time.name in self.available and self.time.name in self.available:
                    ref_data = self.__interp(self.algo_time.data, self.time.data, ref_data)
                else:
                    print("%s or %s is not available."% (self.algo_time.name, self.time.name))
                    return None
            # error stat
            err = self.__all[data_name].data - ref_data
            return self.__array_stat(err, angle)
        else:
            print('Unsupported data type to calculate error statitics for %s'% data_name)
            return None

    def __array_stat(self, x, angle=False):
        '''
        statistics of array x.
        Args:
            x is a numpy array of size (m,n) or (m,). m is number of sample. n is its dimension.
            angle: True if this is angle error. Angle error will be converted to be within
                [-pi, pi] before calculating statistics.
        Returns:
            {'max':, 'avg':, 'std': }
        '''
        # convert angle error to be within [-pi, pi] if necessary
        if angle is True:
            for i in range(len(x.flat)):
                x.flat[i] = attitude.angle_range_pi(x.flat[i])
        # statistics
        return {'max': np.max(np.abs(x), 0),\
                'avg': np.average(x, 0),\
                'std': np.std(x, 0)}

    def __interp(self, x, xp, fp):
        '''
        data interpolation
        '''
        m = x.shape[0]
        ndim = fp.ndim
        if ndim == 1:
            return np.interp(x, xp, fp)
        elif ndim == 2:
            y = np.zeros((m, fp.shape[1]))
            for i in range(fp.shape[1]):
                y[:, i] = np.interp(x, xp, fp[:, i])
            return y
        else:
            raise ValueError('only 1-D or 2-D fp is supported.')

    def __quat2euler_zyx(self, src, dst):
        '''
        quaternion to Euler angles (zyx)
        '''
        if isinstance(src.data, np.ndarray):
            n = src.data.shape[0]
            dst.data = np.zeros((n, 3))
            for j in range(n):
                dst.data[j, :] = attitude.quat2euler(src.data[j, :])
        elif isinstance(src.data, dict):
            for i in src.data:
                n = src.data[i].shape[0]
                euler = np.zeros((n, 3))
                for j in range(n):
                    euler[j, :] = attitude.quat2euler(src.data[i][j, :])
                dst.data[i] = euler
        else:
            raise ValueError('%s is not a dict or numpy array.'% src.name)

    def __euler2quat_zyx(self, src, dst):
        '''
        Euler angles (zyx) to quaternion
        '''
        # array
        if isinstance(src.data, np.ndarray):
            n = src.data.shape[0]
            dst.data = np.zeros((n, 4))
            for j in range(n):
                dst.data[j, :] = attitude.euler2quat(src.data[j, :])
        # dict
        elif isinstance(src.data, dict):
            for i in src.data:
                n = src.data[i].shape[0]
                quat = np.zeros((n, 4))
                for j in range(n):
                    quat[j, :] = attitude.euler2quat(src.data[i][j, :])
                dst.data[i] = quat
        else:
            raise ValueError('%s is not a dict or numpy array.'% src.name)
