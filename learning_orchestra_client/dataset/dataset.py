__author__ = "Otavio Henrique Rodrigues Mapa & Matheus Goncalves Ribeiro"
__credits__ = "all free source developers"
__status__ = "Prototype"

from response_treat import ResponseTreat
import requests
import time


class Dataset:
    def __init__(self, ip_from_cluster):
        self.cluster_url = "http://" + ip_from_cluster + \
                           "/api/learningOrchestra/v1/dataset"
        self.WAIT_TIME = 3
        self.METADATA_INDEX = 0
        self.response_treat = ResponseTreat()

    def insert_dataset_sync(self, dataset_name, url, pretty_response=False):
        """
        description: This method is responsible to insert a dataset from a URI
        synchronously, i.e., the caller waits until the dataset is inserted into
        the Learning Orchestra storage mechanism.

        pretty_response: If true return indented string, else return dict.
        dataset_name: Is the name of the dataset file that will be created.
        url: Url to CSV file.

        return: A JSON object with an error or warning message or a URL
        indicating the correct operation.
        """
        cluster_url_dataset = self.cluster_url
        request_body = {"datasetName": dataset_name, "url": url}
        response = requests.post(url=cluster_url_dataset, json=request_body)
        self.verify_dataset_processing_done(dataset_name, pretty_response)
        if pretty_response:
            print("\n----------" + " CREATED FILE " + dataset_name + " -------"
                                                                     "---")
        return self.response_treat.treatment(response, pretty_response)

    def insert_dataset_async(self, dataset_name, url, pretty_response=False):
        """
        description: This method is responsible to insert a dataset from a URI
        asynchronously, i.e., the caller does not wait until the dataset is
        inserted into the Learning Orchestra storage mechanism. Instead, the
        caller receives a JSON object with a URL to proceed future calls to
        verify if the dataset is inserted.

        pretty_response: If true return indented string, else return dict.
        dataset_name: Is the name of the dataset file that will be created.
        url: Url to CSV file.

        return: A JSON object with an error or warning message or a URL
        indicating the correct operation (the caller must use such an URL to
        proceed future checks to verify if the dataset is inserted).
        """
        cluster_url_dataset = self.cluster_url
        request_body = {"datasetName": dataset_name, "url": url}
        response = requests.post(url=cluster_url_dataset, json=request_body)
        print("\n----------" + " CREATE FILE " + dataset_name + " ----------")
        return self.response_treat.treatment(response, pretty_response)

    def search_all_datasets(self, pretty_response=False):
        """
        description: This method retrieves all datasets metadata, i.e., it does
        not retrieve the dataset content.

        pretty_response: If true return indented string, else return dict.

        return: All datasets metadata stored in Learning Orchestra or an empty
        result.
        """
        cluster_url_dataset = self.cluster_url
        response = requests.get(cluster_url_dataset)
        return self.response_treat.treatment(response, pretty_response)

    def search_dataset(self, dataset_name, pretty_response=False):
        """
        description: This method is responsible for retrieving a specific
        dataset

        pretty_response: If true return indented string, else return dict.
        dataset_name: Is the name of the dataset file.
        limit: Number of rows to return in pagination(default: 10) (maximum is
        set at 20 rows per request)
        skip: Number of rows to skip in pagination(default: 0)

        return Specific dataset metadata stored in Learning Orchestra or an
        error if there is no such dataset.
        """
        response = self.search_dataset_content(dataset_name, limit=1,
                                               pretty_response=pretty_response)
        return response

    def search_dataset_content(self, dataset_name, query={}, limit=10, skip=0,
                               pretty_response=False):
        """
        description:  This method is responsible for retrieving the dataset
        content

        pretty_response: If true return indented string, else return dict.
        dataset_name: Is the name of the dataset file.
        query: Query to make in MongoDB(default: empty query)
        limit: Number of rows to return in pagination(default: 10) (maximum is
        set at 20 rows per request)
        skip: Number of rows to skip in pagination(default: 0)

        return A page with some tuples or registers inside or an error if there
        is no such dataset. The current page is also returned to be used in
        future content requests.
        """

        cluster_url_dataset = self.cluster_url + "/" + dataset_name + \
                                                 "?query=" + str(query) + \
                                                 "&limit=" + str(limit) + \
                                                 "&skip=" + str(skip)
        response = requests.get(cluster_url_dataset)
        return self.response_treat.treatment(response, pretty_response)

    def delete_dataset(self, dataset_name, pretty_response=False):
        """
        description: This method is responsible for deleting the dataset. The
        delete operation is always synchronous because it is very fast, since
        the deletion is performed in background. If a dataset was used by
        another task (Ex. projection, histogram, pca, tuning and so forth), it
        cannot be deleted.

        pretty_response: If true return indented string, else return dict.
        dataset_name: Represents the dataset name.

        return: JSON object with an error message, a warning message or a
        correct delete message
        """
        cluster_url_dataset = self.cluster_url + "/" + dataset_name
        response = requests.delete(cluster_url_dataset)
        return self.response_treat.treatment(response, pretty_response)

    def verify_dataset_processing_done(self, dataset_name,
                                       pretty_response=False):
        """
        description: This method check from time to time using Time lib, if a
        dataset has finished being inserted
        into the Learning Orchestra storage mechanism.

        pretty_response: If true return indented string, else return dict.
        """
        if pretty_response:
            print("\n---------- WAITING " + dataset_name + " FINISH ----------")
        while True:
            time.sleep(self.WAIT_TIME)
            response = self.search_dataset_content(dataset_name, limit=1,
                                                   pretty_response=False)
            if len(response["result"]) == 0:
                continue
            if response["result"][self.METADATA_INDEX]["finished"]:
                break
