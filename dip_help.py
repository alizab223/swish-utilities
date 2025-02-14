from dataclasses import dataclass


@dataclass
class Help:
    mask: str = 'Mask existing data'
    extract: str = 'Extract data from ServiceNow'
    proccess: str = 'Process extracted data'
    stop_limit: str = 'Maximum total records count that can be extracted'
    file_limit: str = 'Maximum amount of files that will be created during extraction'
    interval: str = 'Hours for single extraction iteration'
    batch_size: str = 'Amount of records for single download'
    thread_id: str = ''
    extension: str = ''
    parallel: str = 'Specification of the number or extract rest API requests that will be invoked \
in parallel. The provided interval value is split based on this specification for achieving the concurrency.'
    username: str = 'ServiceNow acout username'
    password: str = 'ServiceNow acout password'
    start_date: str = 'Extraction start date in format YYYY-mm-dd'
    end_date: str = 'Extraction end date in format YYYY-mm-dd'
    url: str = 'Specification of ServiceNow table and filter in RestAPI terminology'
    output_format: str = 'Format of the created files'
    id_list_path: str = 'Path to filtering file in csv format'
    id_field_name: str = 'Name of field in the filtering file'
    data_id_name: str = 'Name of field in the source data'
    export_and_mask: str = 'Perform masking during extraction'
    out_props_csv_path: str = 'Path to output csv containig extracted field set'
    out_prop_name: str = 'Name of the extracted propery'
    mapping_path: str = 'Path to csv file containg masking methods for columns'
    custom_token_dir: str = 'Directory that contains files with custom names for masking'
    important_token_file: str = 'Path to file with names/tokens that will not be masked'
    compress: str = 'Use this flag for applying compression on the files in outpu_dir (during their creation)'
    input_sources: str = 'coma separated filenames or directories containing json'
    input_encoding: str = 'Encoding of the input data'
    input_dir: str = 'Directory that contains files for masking. The files should not be compressed.'
    output_dir: str = 'Directory that contains files that were created as part of --maks of --extract operation'
    version: str = 'Prints current version'
    authentication_file = 'Path to file containing authentication data in json format'
    config: str = 'Configuration file for execution with less parameters'
    pretty_json: str = 'Pretty output json'
    debug: str = 'Print some debug output'
