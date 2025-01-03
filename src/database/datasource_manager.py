import logging
import os
import shutil


def format_ds_name(fn):
    def wrapper(instance, *args, **kwargs):
        if "ds_name" in kwargs:
            kwargs["ds_name"] = human_name_to_system_name(kwargs["ds_name"])
        print(
            f"Calling function {fn.__name__} with {instance} args {args} and kwargs {kwargs}"
        )
        result = fn(instance, *args, **kwargs)
        return result

    return wrapper


def human_name_to_system_name(name):
    return name.replace(" ", "_").lower()


def system_name_to_human_name(name):
    return name.replace("_", " ").capitalize()


def save_new_table(file, path):
    with open(path, "wb") as f:
        f.write(file.getbuffer())
    logging.info(f"Saved new datasource {file.name} to {path}")


class DatasourceManager:
    def __init__(self, path_to_data_folder):
        self.path_to_data_folder = path_to_data_folder

    @property
    def datasources(self):
        return get_data_sources(self.path_to_data_folder)

    def get_datasources(self, exclude=None):
        if exclude is None:
            exclude = []
        return [ds for ds in self.datasources if ds not in exclude]

    @property
    def datasources_human(self):
        return [system_name_to_human_name(name) for name in self.datasources]

    @format_ds_name
    def _create_new_datasource(self, *, ds_name):
        if ds_name not in self.datasources:
            os.mkdir(os.path.join(self.path_to_data_folder, ds_name))
            logging.info(f"Created new datasource {ds_name}")
        else:
            logging.info(f"Datasource {ds_name} already exists")

    @format_ds_name
    def new_table(self, table, *, ds_name="uploaded"):
        self._create_new_datasource(ds_name=ds_name)
        path = os.path.join(self.path_to_data_folder, ds_name, table.name)
        save_new_table(table, path)

    @format_ds_name
    def new_tables(self, tables: list, *, ds_name="custom_datasource"):
        for table in tables:
            self.new_table(table, ds_name=ds_name)

    def from_path(self, path_to_data_folder, *, ds_name):
        # Ensure the destination directory exists
        self._create_new_datasource(ds_name=ds_name)
        destination_folder = os.path.join(self.path_to_data_folder, ds_name)

        # Iterate over all files in the source directory
        for filename in os.listdir(path_to_data_folder):
            source_file = os.path.join(path_to_data_folder, filename)
            # Ensure we're only copying files, not directories
            if os.path.isfile(source_file):
                shutil.copy2(source_file, destination_folder)
        logging.info(
            f"Copied all files from {path_to_data_folder} to {destination_folder}"
        )


def get_data_sources(path_to_data_folder) -> list[str]:
    # Return all folder names in path_to_data_folder
    return [
        name
        for name in os.listdir(path_to_data_folder)
        if os.path.isdir(os.path.join(path_to_data_folder, name))
    ]
