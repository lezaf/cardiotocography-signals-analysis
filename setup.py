from setuptools import setup, find_packages

setup(
	name='ctg-processing',
	version='1.0.0',
	description='CTG signals processing',
	author='lezaf',
	packages=find_packages(include=['src', 'src.*',
					'data', 'data.*']),
	install_requires=[
		'certifi==2021.10.8',
		'charset-normalizer==2.0.7',
		'cycler==0.11.0',
		'idna==3.3',
		'joblib==1.1.0',
		'kiwisolver==1.3.1',
		'matplotlib==3.3.4',
		'numpy==1.19.5',
		'pandas==1.1.5',
		'Pillow==8.3.1',
		'pkg-resources==0.0.0',
		'pyparsing==3.0.4',
		'python-dateutil==2.8.2',
		'pytz==2021.3',
		'requests==2.26.0',
		'scikit-learn==0.24.2',
		'scipy==1.5.4',
		'six==1.16.0',
		'sklearn==0.0',
		'threadpoolctl==3.0.0',
		'urllib3==1.26.7',
		'wfdb==3.4.1']
)
