from blackfynn import Blackfynn


class BlackfynnDataModel(object):

    def __init__(self):
        self._settings = {'active-profile': ''}
        self._cache = {}
        self._bf = None

    def addProfile(self, profile):
        self._settings[profile['name']] = {'api_token': profile['token'], 'api_secret': profile['secret']}

    def setActiveProfile(self, profile_name):
        self._settings['active-profile'] = profile_name

    def getActiveProfile(self):
        return self._settings['active-profile']

    def getExistingProfileNames(self):
        profile_names = [*self._settings]
        profile_names.remove('active-profile')
        return profile_names

    def _getBlackfynn(self, profile_name):
        api_key = self._settings[profile_name]['api_token']
        api_secret = self._settings[profile_name]['api_secret']
        print('[{0}]:[{1}]'.format(api_key, api_secret))
        self._bf = Blackfynn(api_token=api_key, api_secret=api_secret)
        return self._bf

    def getDatasets(self, profile_name, refresh=False):
        if profile_name in self._cache and not refresh:
            datasets = self._cache[profile_name]['datasets']
        elif refresh:
            bf = self._getBlackfynn(profile_name)
            datasets = bf.datasets()
            if profile_name in self._cache:
                self._cache[profile_name]['datasets'] = datasets
            else:
                self._cache[profile_name] = {'datasets': datasets}
        else:
            datasets = []

        return datasets

    def getDataset(self, profile_name, dataset_name, refresh=False):
        if profile_name in self._cache and dataset_name in self._cache[profile_name] and not refresh:
            dataset = self._cache[profile_name][dataset_name]
        elif refresh:
            bf = self._getBlackfynn(profile_name)
            dataset = bf.get_dataset(dataset_name)
            self._cache[profile_name][dataset_name] = dataset
        else:
            dataset = []

        return dataset

    def getTimeseriesData(self, profile_name, dataset_name, timeseries_name):
        for stored_dataset in self._cache[profile_name][dataset_name]:
            if stored_dataset.name == timeseries_name:
                timeseries_dframe = stored_dataset.get_data(length='16s')

        cache_output = self._create_file_cache(timeseries_dframe)
        return cache_output

    def _create_file_cache(self, data_frame):

        cache_dictionary = {}
        for key in data_frame:
            cache_dictionary[key] = data_frame[key].values.tolist()
        return cache_dictionary


    def uploadRender(self, filePath):
        try:
            ds = self._bf.get_dataset('Zinc Exports')
        except:
            self._bf.create_dataset('Zinc Exports')
            ds = self._bf.get_dataset('Zinc Exports')
        ds.upload(filePath)

    def getSettings(self):
        return self._settings

    def setSettings(self, settings):
        print('set settings {0}',format(settings))
        self._settings.update(settings)
