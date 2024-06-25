'''Entry point for CTG signals processing

TODO:
'''
import  os

import  wfdb
import  matplotlib.pyplot                as      plt
import  matplotlib.patches               as      patches

import  numpy                            as      np
import  time

from    scipy.stats                      import  pearsonr, spearmanr
from    sklearn.linear_model             import  LinearRegression
from    sklearn.cluster                  import  DBSCAN, KMeans
from    sklearn.preprocessing            import  MinMaxScaler

from    src.dataset.ctg_record_dataset   import  CTGRecordDataset
from    src.metrics                      import  metrics_funcs

'''CONSTANTS

* ZERO_PARTS_THRESHOLD: threshold in samples for removing intermediate
    zero parts (SAMPLING_FREQUENCY*SECONDS)
* LOWER_BPM_VALUE_THRESHOLD: bpm with values smaller than LOWER_BPM_VALUE_THRESHOLD are
    interpolated
* UPPER_BPM_VALUE_THRESHOLD: bpm with values greater than UPPER_BPM_VALUE_THRESHOLD are
    interpolated
* TYPE_OF_INTERPOLATION:
* SDANN_INTERVAL_LENGTH: length in samples for SDANN calculation
    (SAMPLING_FREQUENCY*SECONDS)
* DELIVERY_TYPE: delivery type of signals to load
    (1: vaginal, 2: caesarean section)

'''
# --- CONSTANTS --- #
ZERO_PARTS_THRESHOLD            = 4*7
LOWER_BPM_VALUE_THRESHOLD       = 50
UPPER_BPM_VALUE_THRESHOLD       = 200
TYPE_OF_INTERPOLATION           = 'linear'

SDANN_INTERVAL_LENGTH           = 4*300

DELIVERY_TYPE                   = 1



def analyze_hrv_to_ph(hrv_arr, ph_arr, deliv_type):

    plt.figure()
    plt.grid()

    #
    # ------------- Simple Linear Regression -------------
    #
    lr_model = LinearRegression()
    lr_model.fit(hrv_arr.reshape((-1, 1)), ph_arr)

    print("R squared: %f" % lr_model.score(hrv_arr.reshape((-1, 1)), ph_arr))

    lr_line_x = np.linspace(np.amin(hrv_arr), np.amax(hrv_arr))
    lr_line_y = lr_model.intercept_ + lr_model.coef_*lr_line_x
    plt.plot(lr_line_x,
             lr_line_y,
             color='g',
             label='Linear Regression line',
             alpha=0.5)

    # create training dataset by combining hrv_arr and ph_arr pairwise
    X = np.stack((hrv_arr, ph_arr), axis=-1)

    # need of scaling due to vast difference in values ranges
    scaler = MinMaxScaler()

    deliv_type_str = 'vaginal' if deliv_type == 1 else 'CS'
    # vaginal delivery analysis
    if deliv_type == 1:
        #
        # ------------- DBSCAN -------------
        # apply DBSCAN clustering to discover (density based) clusters of
        # normal and abnormal pH values
        #

        DBSCAN_model = DBSCAN(eps=0.09, min_samples=20).fit(scaler.fit_transform(X))
        labels = DBSCAN_model.labels_

        for label in np.unique(labels):
            plt.scatter(hrv_arr[labels == label],
                        ph_arr[labels == label],
                        label='DBSCAN cluster: {}'.format(label),
                        alpha=0.5)

        plt.title('Delivery type: %s\nNum of samples: %d\nDBSCAN: eps=0.09, min_pts=20' % (deliv_type_str, len(hrv_arr)))

    # caesarean section delivery analysis
    else:
        kmeans_model = KMeans(n_clusters=2).fit(scaler.fit_transform(X))
        labels = kmeans_model.labels_

        for label in np.unique(labels):
            plt.scatter(hrv_arr[labels == label],
                        ph_arr[labels == label],
                        label='K-means cluster: {}'.format(label),
                        alpha=0.5)

        plt.title('Delivery type: %s\nNum of samples: %d\nK-means clustering' % (deliv_type_str, len(hrv_arr)))

    plt.xlabel('HRV (bpm)')
    plt.ylabel('pH')

    plt.legend()
    plt.show()


def initialize_analysis(records_dataset, feature_choice, deliv_type):
    if feature_choice == 'pH':
        position_in_comments = 2
    elif feature_choice == 'BDecf':
        position_in_comments = 3
    elif feature_choice == 'pCO2':
        position_in_comments = 4
    elif feature_choice == 'BE':
        position_in_comments = 5
    elif feature_choice == 'Apgar1':
        position_in_comments = 6
    elif feature_choice == 'Apgar5':
        position_in_comments = 7
    elif feature_choice == 'Weight':
        position_in_comments = 17
    else:
        print("%s is not valid feature to compare." % feature_choice)
        exit()


    hrv_arr = []
    feature_arr = []

    # load feature values
    for index in range(len(records_dataset)):
        record = records_dataset.get_item(index)
        ctg_signal = np.copy(record.__dict__['p_signal'])

        # if no value has been recorded, skip record
        if record.__dict__['comments'][position_in_comments].split(' ')[-1] == 'NaN':
            continue

        hrv_arr.append(metrics_funcs.calculate_SDNN(ctg_signal))

        # examine .hae files to understand following line
        feature_arr.append(float(
            record.__dict__['comments'][position_in_comments].split(' ')[-1])
        )

    hrv_arr = np.array(hrv_arr)
    feature_arr = np.array(feature_arr)

    # Disable scientific notation of numpy
    np.set_printoptions(suppress=True)

    #
    # ------------- common statistics calculations -------------
    #
    print("\n\t#----- Correlation analysis -----#\n")
    print("# Independent variable: HRV (bpm)")
    print("# Dependent variable:   %s" % feature_choice)
    print("# Delivery type:        %d" % (DELIVERY_TYPE))
    print()
    print("Covariance matrix:\n" + str(np.around(np.cov(hrv_arr, feature_arr), 3)))
    print("Pearson's correlation: %.3f (p-value: %f)" % pearsonr(hrv_arr, feature_arr))
    print("Spearman's correlation: %.3f (p-value: %f)" % spearmanr(hrv_arr, feature_arr))


    # create simple scatter plot
    plt.figure()
    plt.grid()

    # simple scatter plot of HRV/feature_choice
    plt.scatter(hrv_arr, feature_arr,
                c='g',
                alpha=0.5)

    deliv_type_str = 'vaginal' if deliv_type == 1 else 'CS'
    plt.title('Delivery type: %s\nNum of samples: %d' % (deliv_type_str, len(hrv_arr)))
    plt.xlabel('HRV (bpm)')
    plt.ylabel('%s' % feature_choice)

    # call corresponding analysis function
    if feature_choice == 'pH':
        analyze_hrv_to_ph(hrv_arr, feature_arr, deliv_type)
    else:
        #
        # ------------- Simple Linear Regression -------------
        #
        lr_model = LinearRegression()
        lr_model.fit(hrv_arr.reshape((-1, 1)), feature_arr)

        print("R squared: %f" % lr_model.score(hrv_arr.reshape((-1, 1)), feature_arr))

        lr_line_x = np.linspace(np.amin(hrv_arr), np.amax(hrv_arr))
        lr_line_y = lr_model.intercept_ + lr_model.coef_*lr_line_x
        plt.plot(lr_line_x,
                 lr_line_y,
                 color='g',
                 label='Linear Regression line',
                 alpha=0.5)

        plt.show()



def main():

    # create records dataset object to handle signals (vaginal delivery)
    records_dataset_vag = CTGRecordDataset(
                            records_dir_path='../data/ctu-chb-ctg-db',
                            record_filenames='RECORDS',
                            delivery_type=DELIVERY_TYPE,
                            channels_to_load=[0]
    )

    # start_time = time.time()
    records_dataset_vag.perform_preprocessing(
                        zero_parts_threshold=ZERO_PARTS_THRESHOLD,
                        lower_bpm_value_threshold=LOWER_BPM_VALUE_THRESHOLD,
                        upper_bpm_value_threshold=UPPER_BPM_VALUE_THRESHOLD,
                        type_of_interpolation=TYPE_OF_INTERPOLATION
    )
    # end_time = time.time()
    # print("Execution time: %.3f s" % (end_time-start_time))


    initialize_analysis(records_dataset_vag, 'pH', DELIVERY_TYPE)



if __name__ == '__main__':
    main()