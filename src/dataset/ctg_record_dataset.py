'''Dataset to represent the CTG wdfb-type records

TODO:
    * Make class iteratable overriding __iter__() or __getitem__() (PyTorch)
        instead of explicitly getting item by index

'''

import  os

import  wfdb
import  numpy                            as      np

from    src.preprocessing                import  preprocessing_funcs

import matplotlib.pyplot as plt

class CTGRecordDataset():
    '''The class represents a dataset of wfdb-type records

    Attributes:
        records (list): a list with Record records loaded

    Methods:
        perform_preprocessing(self,
                              zero_parts_threshold,
                              lower_bpm_value_threshold,
                              upper_bpm_value_threshold
                              type_of_interpolation): preprocesses the records
        get_item(self, index): returns record in position index from records
        __len__(self): returns the number of items in records

    '''

    def __init__(self,
                 records_dir_path,
                 record_filenames,
                 delivery_type,
                 channels_to_load):

        '''Constructor info

        Args:
            records_dir_path (str): The path to the directory of CTG records
            record_filenames (str): The name of the file that contains CTG
                record names
            delivery_type (int): Delivery type of signals to load
                (1: vaginal, 2: caesarean section)
            channels_to_load (list): Which channels to load from signal files
                ([0]: FHR, [1]: UC, [0, 1]: both)
        '''

        # routine value checks
        if delivery_type not in {1, 2}:
            raise ValueError("Invalid delivery type. Allowed options:\n"
                            + "1: vaginal"
                            + "2: caesarean section"
            )

        if not set(channels_to_load).issubset([0, 1]):
            raise ValueError("Invalid channels. Allowed options:\n"
                            + "[0]: Fetus Heart Rate"
                            + "[1]: Uterine Contractions"
                            + "[0, 1]: FHR and UC"
            )

        self.records = []

        # load records in self.records attribute
        with open(os.path.join(records_dir_path, record_filenames), 'r') as rec_names:
            for rec_name in rec_names:
                record = wfdb.rdrecord(
                            os.path.join(records_dir_path, rec_name.strip()),
                            channels=channels_to_load
                         )

                # check delivery type
                # to understand following line check .hae files formatting
                if int(record.__dict__['comments'][-6].split(' ')[-1]) != delivery_type:
                    continue

                self.records.append(record)


    def perform_preprocessing(self,
                              zero_parts_threshold,
                              lower_bpm_value_threshold,
                              upper_bpm_value_threshold,
                              type_of_interpolation):
        '''Performs the necessary preprocessing on FHR signals in records

        Preprocessing actions performed:
            * remove leading and trailing zero parts
            * remove intermediate zero parts with
                duration >= zero_parts_threshold samples
            * interpolate remaining zero values
            * interpolate bpm values smaller than lower_bpm_value_threshold
            * interpolate bpm values greater than upper_bpm_value_threshold


        Args:
            zero_parts_threshold (int): intermediate zero parts with length
                equal or above zero_parts_threshold are removed
            lower_bpm_value_threshold (int): lower bpm value threshold
            upper_bpm_value_threshold (int): upper bpm value threshold
            type_of_interpolation (str): type of interpolation for remaining
                zero parts of signal

        '''

        for record in self.records:
            ctg_signal = np.copy(record.__dict__['p_signal'])

            # remove leading and trailing zero parts from signal
            ctg_signal = np.trim_zeros(ctg_signal)

            # remove intermediate zero parts that lasts more than
            # zero_parts_threshold samples
            ctg_signal = preprocessing_funcs.remove_zero_parts_with_threshold(
                                                arr=ctg_signal,
                                                threshold=zero_parts_threshold)

            # apply linear interpolation
            if type_of_interpolation == 'linear':
                ctg_signal = preprocessing_funcs.apply_linear_interpolation(ctg_signal)
                ctg_signal = preprocessing_funcs.apply_linear_interpolation_below_threshold(ctg_signal, lower_bpm_value_threshold)
                ctg_signal = preprocessing_funcs.apply_linear_interpolation_above_threshold(ctg_signal, upper_bpm_value_threshold)
            else:
                print("Not supported interpolation method.")
                exit(-1)

            # update signal in record with the preprocessed signal
            record.__dict__['p_signal'] = ctg_signal


    def get_item(self, index):
        return self.records[index]

    def __len__(self):
        '''Get the number of records loaded
        '''

        return len(self.records)