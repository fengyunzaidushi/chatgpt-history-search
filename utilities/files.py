import asyncio
import json
import os

import aiofiles
import pandas as pd


class IOFiles:
    @staticmethod
    def read_dir_contents(path: str, dtype: str = "json") -> dict:
        """
        Read all files in a directory with a specific dtype
        :param path:  Path to the directory
        :param dtype:  Data type of the files to read  (json, txt, csv, etc.)
        :return:  Dictionary of file contents with file name (without the dtype) as key and content as value
        """

        contents = {}
        if os.path.exists(path) and os.path.isdir(path):
            for file in os.listdir(path):
                if file.endswith(dtype):
                    ident = file.replace(f".{dtype}", "")

                    if dtype == "json":
                        contents[ident] = IOFiles.read_json(os.path.join(path, file))
                    elif dtype in ["csv", "xlsx", "pickle"]:
                        contents[ident] = IOFiles.read_df(os.path.join(path, file), dtype)
                    else:
                        contents[ident] = IOFiles.read_file(os.path.join(path, file))

        return contents

    @staticmethod
    async def read_dir_contents_async(path: str, dtype: str = "json") -> dict:
        """
        Read all files in a directory with a specific dtype asynchronously
        :param path:  Path to the directory
        :param dtype:  Data type of the files to read  (json, txt, etc.) [NOT SUPPORTED FOR DATAFRAMES]
        :return:  Dictionary of file contents with file name (without the dtype) as key and content as value
        """

        tasks, idents = [], []
        if os.path.exists(path) and os.path.isdir(path):
            for file in os.listdir(path):
                if file.endswith(dtype):
                    idents.append(file.replace(f".{dtype}", "") if dtype != "all" else file)

                    if dtype == "json":
                        tasks.append(IOFiles.read_json_async(os.path.join(path, file)))
                    else:
                        tasks.append(IOFiles.read_file_async(os.path.join(path, file)))

        results = await asyncio.gather(*tasks)
        contents = {ident: content for ident, content in zip(idents, results)}

        return contents

    @staticmethod
    def write_contents_to_dir(path: str, contents: dict, dtype: str) -> None:
        """
        Write contents to a directory with a specific dtype
        :param path:  Path to the directory
        :param contents:  Dictionary of file contents with file name as key and content as value
        :param dtype:  Data type of the files to write  (json, txt, csv, etc.)
        :return:  None
        """

        if not os.path.exists(path):
            os.makedirs(path)

        for ident, content in contents.items():
            file_path = os.path.join(path, f"{ident}.{dtype}")
            if dtype == "json":
                IOFiles.write_json(file_path, content)
            elif dtype in ["csv", "xlsx", "pickle"]:
                IOFiles.write_df(file_path, content, dtype)
            else:
                IOFiles.write_file(file_path, content)

    @staticmethod
    async def write_contents_to_dir_async(path: str, contents: dict, dtype: str) -> None:
        """
        Write contents to a directory with a specific dtype asynchronously
        :param path:  Path to the directory
        :param contents:  Dictionary of file contents with file name as key and content as value
        :param dtype:  Data type of the files to write  (json, txt, etc.) [NOT SUPPORTED FOR DATAFRAMES]
        :return:  None
        """

        if not os.path.exists(path):
            os.makedirs(path)

        tasks = []
        for ident, content in contents.items():
            file_path = os.path.join(path, f"{ident}.{dtype}")
            if dtype == "json":
                tasks.append(IOFiles.write_json_async(file_path, content))
            else:
                tasks.append(IOFiles.write_file_async(file_path, content))

        await asyncio.gather(*tasks)

    @staticmethod
    def read_file(path: str) -> str:
        """
        Read a file
        :param path:  Path to the file
        :return:  File content
        """

        try:
            with open(path, "r") as file:
                return file.read()
        except FileNotFoundError:
            print(f"File not found: {path}")
        except Exception as e:
            print(f"Error Reading File: {e}")

        return ""

    @staticmethod
    def write_file(path: str, data: str) -> None:
        """
        Write data to a file
        :param path:  Path to the file
        :param data:  Data to write
        :return: None
        """

        try:
            with open(path, "w") as file:
                file.write(data)
        except Exception as e:
            print(f"Error Writing File: {e}")

    @staticmethod
    async def read_file_async(path: str) -> str:
        """
        Read a file asynchronously
        :param path:  Path to the file
        :return:  File content
        """

        try:
            async with aiofiles.open(path, "r") as file:
                return await file.read()
        except FileNotFoundError:
            print(f"File not found: {path}")
        except Exception as e:
            print(f"Error Reading File: {e}")

        return ""

    @staticmethod
    async def write_file_async(path: str, data: str) -> None:
        """
        Write data to a file asynchronously
        :param path:  Path to the file
        :param data:  Data to write
        :return:  None
        """

        try:
            async with aiofiles.open(path, "w") as file:
                await file.write(data)
        except Exception as e:
            print(f"Error Writing File: {e}")

    @staticmethod
    def read_json(path: str) -> dict:
        """
        Read a JSON file
        :param path:  Path to the JSON file
        :return:  JSON data
        """

        try:
            with open(path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"File not found: {path}")
        except json.JSONDecodeError:
            print(f"File is corrupted: {path}")

        return {}

    @staticmethod
    def write_json(path: str, data: dict, indent: int = 4) -> None:
        """
        Write data to a JSON file
        :param path:  Path to the JSON file
        :param data:  Data to write
        :param indent:  Indentation level
        :return:  None
        """
        if not path.endswith(".json"):
            path += ".json"

        try:
            with open(path, "w") as file:
                json.dump(data, file, indent=indent)
        except Exception as e:
            print(f"Error Writing JSON: {e}")

    @staticmethod
    async def read_json_async(path: str) -> dict:
        """
        Read a JSON file asynchronously
        :param path:  Path to the JSON file
        :return:  JSON data
        """

        try:
            async with aiofiles.open(path, "r") as file:
                return json.loads(await file.read())
        except FileNotFoundError:
            print(f"File not found: {path}")
        except json.JSONDecodeError:
            print(f"File is corrupted: {path}")

        return {}

    @staticmethod
    async def write_json_async(path: str, data: dict, indent: int = 4) -> None:
        """
        Write data to a JSON file asynchronously
        :param path:  Path to the JSON file
        :param data:  Data to write
        :param indent:  Indentation level
        :return:  None
        """
        if not path.endswith(".json"):
            path += ".json"

        try:
            async with aiofiles.open(path, "w") as file:
                await file.write(json.dumps(data, indent=indent))
        except Exception as e:
            print(f"Error Writing JSON: {e}")

    @staticmethod
    def read_df(path: str, dtype: str = "csv") -> pd.DataFrame:
        """
        Read a dataframe from a file
        :param path:  Path to the file
        :param dtype:  Data type of the file  (csv, pickle, xlsx)
        :return:  Pandas DataFrame
        """

        try:
            if dtype == "csv":
                return pd.read_csv(path)
            elif dtype == "pickle":
                return pd.read_pickle(path)
            elif dtype == "xlsx":
                return pd.read_excel(path)
            else:
                raise ValueError(f"Invalid Dataframe dtype: {dtype}")
        except FileNotFoundError:
            print(f"File not found: {path}")
        except Exception as e:
            print(f"Error: {e}")

        return pd.DataFrame()

    @staticmethod
    def write_df(path: str, data: pd.DataFrame, dtype: str = "csv") -> None:
        """
        Write a dataframe to a file
        :param path:  Path to the file
        :param data:  Pandas DataFrame
        :param dtype:  Data type of the file  (csv, pickle, xlsx)
        :return:  None
        """

        try:
            if dtype == "csv":
                data.to_csv(path, index=False)
            elif dtype == "pickle":
                data.to_pickle(path)
            elif dtype == "xlsx":
                data.to_excel(path, index=False)
            else:
                raise ValueError(f"Invalid Dataframe dtype: {dtype}")
        except Exception as e:
            print(f"Error Writing CSV: {e}")
