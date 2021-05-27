import requests
import datetime
import os
import json, gzip
from time import time
from requests.auth import HTTPBasicAuth


class Extractor:
    def __init__(self, start_date, end_date, thread_id, app_settings = None):

        self.settings = app_settings
        self.session = requests.Session()

        self.total_added = 0
        self.total_failed = 0
        self.offset = 0
        self.total_results = []
        self.response_size = 0
        self.maximum_trials_number = 2
        self.thread_params = None
        self.start_date = None
        self.end_date = None
        self.thread_id = None

        self.start_date = start_date
        self.end_date = end_date
        self.thread_id = thread_id


    def api_extract(self, params):
        """
        :param url:
        :param start_date:
        :param end_date:
        :param batch_size:
        :return:
        """

        try:

            message = f"Thread {self.thread_id}: starting. Start_date: {self.start_date}"
            print(message)
            self.settings.logger.info(message)

            params.headers = {
                'Content-type': 'application/json'
            }
            params.auth = HTTPBasicAuth(params.username, params.password)

            batch_start_date = self.start_date
            batch_end_date = batch_start_date + datetime.timedelta(hours=params.interval)
            while self.total_added < params.stop_limit and batch_start_date < batch_end_date:

                if batch_end_date >= self.end_date:
                    batch_end_date = self.end_date

                self.response_size = params.batch_size
                self.offset = 0

                while self.response_size >= params.batch_size and self.total_added < params.stop_limit:
                    url = params.url
                    url += f'^sys_created_on>{batch_start_date}^sys_created_on<{batch_end_date}&sysparm_offset={self.offset}&sysparm_limit={params.batch_size}'
                    message = f'Thread: {self.thread_id}, URL: {url}'
                    print(message)
                    self.settings.logger.info(message)

                    trial_number = 1

                    try:
                        self.handle_api_request(params, url, trial_number)

                    except Exception as error:

                        # Trials exceeded for this interval, jump to next interval
                        break


                batch_start_date = batch_start_date + datetime.timedelta(hours=params.interval)
                batch_end_date = batch_end_date + datetime.timedelta(hours=params.interval)

        except KeyboardInterrupt:
            message = f'Code Interrupted by User'
            print(message)
            self.settings.logger.error(message)
        except Exception as error:
            message = f"Error. Info: {error}"
            self.settings.logger.error(message)
            print(message)
        finally:

            # Save to file if any data is in buffer
            if len(self.total_results) > 0:
                self.save_data_to_file(self.total_results, params)


            message = f"Thread {self.thread_id}: finishing"
            print(message)
            self.settings.logger.info(message)

    def handle_api_request(self, params, url, trial_number):
        try:
            t1 = time()
            resp = self.session.get(url, headers=params.headers, auth = params.auth)
            response_time = round(time() - t1, 3)

            self.offset += params.batch_size
            resp_body = resp.json()

            if resp.status_code == 200 and resp_body.__contains__('result') and not resp_body.__contains__('error'):
                results = resp_body['result']

                # Validate results as json
                try:
                    json.dumps(results)
                except Exception as error:
                    raise Exception('Corrupted JSON from API')

                self.total_results += results
                self.response_size = len(results)
                self.total_added += self.response_size

                message = f'Added: {self.response_size}. (Total Added: {self.total_added}, Total Failed Approximated: {self.total_failed}), Response Time: {response_time} s'
                self.settings.logger.info(message)
                print(message)

                if len(self.total_results) >= params.file_limit:
                    message = 'File Split'
                    print(message)
                    self.settings.logger.info(message)
                    self.save_data_to_file(self.total_results, params)
                    self.total_results = []
            else:
                message = ''
                if resp.json().__contains__('error'):
                    message = f"{str(resp.json()['error'])}"
                else:
                    message = f"{str(resp.json())}"

                raise Exception(message)

        except Exception as error:

            if trial_number < self.maximum_trials_number:
                message = f"Error: Failed fetching from API. Trial: {trial_number} . Info: {error}"
                self.settings.logger.error(message)
                print(message)
                self.handle_api_request(params, url, trial_number + 1)

            if trial_number >= self.maximum_trials_number:
                message = f"Error: Totally Failed fetching from API. Trial: {trial_number} . Info: {error}"
                self.settings.logger.error(message)
                print(message)
                self.total_failed += params.batch_size
                raise Exception(message)

    def save_data_to_file(self, results, params):
        try:
            print(self.thread_id)

            output_filename = os.path.join(params.output_dir,'output_' + self.settings.reset_timestamp() +
                            '_' + str(self.thread_id) + '.' + params.extension)

            # Validate results as json
            try:
                json.dumps(results[-1])

            except Exception as error:
                deleted = results[-1]
                results.pop()
                message = f'Deleted data to maintain JSON format: {deleted}'
                self.settings.logger.error(message)
                print(message)

            try:
                if params.compress:
                    with gzip.open(output_filename, 'wt', encoding="utf-8") as zipfile:
                        json.dump(results, zipfile)
                else:
                    with open(output_filename, 'w', encoding='utf-8') as f:
                        json.dump(results, f)
            except Exception as e:
                print(e.__str__(), "\n", "Trying utf-8-sig encoding...")

                if params.compress:
                    with gzip.open(output_filename, 'wt', encoding="utf-8-sig") as zipfile:
                        json.dump(results, zipfile)
                else:
                    with open(output_filename, 'w', encoding='utf-8-sig') as f:
                        json.dump(results, f)

            message = f'Writing to file COMPLETED SUCCESSFULLY for file:{output_filename}'
            self.settings.logger.info(message)
            print(message)

        except Exception as e:
            message = f'Error while saving file. {e}'
            self.settings.logger.exception(message)
            raise Exception(message)



