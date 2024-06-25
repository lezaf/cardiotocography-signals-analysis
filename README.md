# cardiotocography-signals-analysis

We performed ML analysis on intrapartum cardiotocography (CTG) signals. Here is a brief summary of the [data](##Data), the preprocessing we applied on signals, the analysis methods and some of the results.

## Data
We used intrapartum cardiotocography (CTG) signals [database](https://www.physionet.org/content/ctu-uhb-ctgdb/1.0.0/) from PhysioNet. Each CTG contains a FHR time series and a Uterine Contraction (UC) signal. The database also includes maternal, delivery, and fetal clinical details.

## Preprocessing
To handle noise in CTG signals we performed following steps:

- Step 1: Leading/trailing zeroes elimination
- Step 2: Intermediate zero parts
  - We set a time threshold of *7 seconds* for acceptance of intermediate zero parts. Above this threshold the intermediate parts were eliminated since their interpolation would give an unrealistic behavior of the signal.
- Step 3: Remaining zero values interpolation
- Step 4: Extremely low/high HR values interpolation

The preprocessing effect on CTG signals is depicted below:

<img src="/imgs/steps_of_preprocessing_on_1026.png" width="800" height="400" alt="CTG signals preprocessing effects">

## Process
We used Fetal Heart Rate (FHR) time series to calculate Heart Rate Variability (HRV) of fetus. Performing correlation analysis between HRV and the available features, we concluded to a subset of features with underlying relationship:

- pH
- BDecf
- BE

For the case of HRV/pH relationship we further experiment with ML algorithms, including *k-means* and *DBSCAN* to decide normal/abnormal pH range.

## HRV/pH results
For the case of HRV/pH in *vaginal* delivery, we concluded in *normal* pH values: $7.17 \leq pH \leq 7.32$.

<img src="/imgs/rich_scatter_vaginal.png" width="800" height="400" alt="HRV/pH analysis">

## Citations
- [Václav Chudáček, Jiří Spilka, Miroslav Burša, Petr Janků, Lukáš Hruban, Michal Huptych, Lenka Lhotská. Open access intrapartum CTG database. BMC Pregnancy and Childbirth 2014 14:16](https://bmcpregnancychildbirth.biomedcentral.com/counter/pdf/10.1186/1471-2393-14-16.pdf)
- Goldberger, A., Amaral, L., Glass, L., Hausdorff, J., Ivanov, P. C., Mark, R., ... & Stanley, H. E. (2000). PhysioBank, PhysioToolkit, and PhysioNet: Components of a new research resource for complex physiologic signals. Circulation [Online]. 101 (23), pp. e215–e220
