import re


class Search:
    def __init__(self, file_name="sample.txt"):
        """
        Initialize the Search class with a filename. Reads the file content line by line.
        Args:
            file_name (str): The name of the file to search in.
            By default, sample.txt exist on server.
        """
        self.file_name = file_name
        try:
            with open(file_name, 'r') as filehandler:
                self.lines_lis = filehandler.readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"File '{file_name}' not found on server")

    @staticmethod
    def clean(line):
        """
        Removes special characters from a given line using regular expressions.
        Args:
            line (str): The line to be cleaned.
        Returns:
            str: The cleaned line.
        """
        clean_line = re.sub(r'\W+', ' ', line)
        return clean_line

    def getlines(self, user_pattern):
        """
        Searches the file for lines containing the user-specified word/pattern.
        Args:
            user_pattern (str): The word or pattern to search for.
        Returns:
            list: A list where the first element is the search word, followed by tuples of line number and content.
                  If the word is not found, an error message is returned.
        """
        if not user_pattern or not any(char.isalnum() for char in user_pattern):
            raise ValueError(
                "Invalid pattern: Please provide a non-empty word or pattern containing letters or numbers."
            )

        clean_pattern = user_pattern.lower()
        result_list = [clean_pattern]
        found_flag = False

        for ind, line in enumerate(self.lines_lis):
            clean_line = self.clean(line).lower()  # Clean and lowercase the line for case-insensitive search
            if clean_pattern in clean_line:
                result_list.append((ind + 1, line.strip()))
                found_flag = True

        if not found_flag:
            return {"ERROR": f"'{user_pattern}' not found in file '{self.file_name}'"}

        return result_list
