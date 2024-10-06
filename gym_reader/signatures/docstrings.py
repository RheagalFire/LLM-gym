FILE_DIFF_CONTENT_EXPLANATION = """
>> **General Instructions**\n
        This **file_diff_content** represents changes made to files in a version control system, such as Git.\n

        **Interpretation of the diff:**\n

        1. **File Information**:\n
            - Each section of the diff corresponds to a specific file.\n
            - The header of each section indicates the file path and the type of change (modification, addition, or deletion).\n

        2. **Change Types**:\n
            - **Modification**: Changes made to an existing file.\n
            - **Addition**: A new file has been created.\n
            - **Deletion**: An existing file has been removed.

        3. **File Hashes**:\n
            - The old and new file hashes represent the state of the file before and after the changes.\n
            - A hash of `0000000` typically indicates that the file did not exist previously (in the case of a new file).\n

        4. **Line Changes**:\n
            - Lines starting with `-` indicate content that was removed or replaced.\n
            - Lines starting with `+` indicate new content that was added.\n
            - Context lines (without `-` or `+`) provide additional information to understand the changes in the surrounding lines.\n

        **How to Interpret the Diff**:\n
        - The diff output is divided into sections, each representing changes to a specific file.\n
        - The lines prefixed with `-` and `+` show the exact changes made to the file content.\n
        - The context lines help in understanding the modifications in the context of the surrounding code or text.

            This diff helps in understanding what changes were made to the files, which lines were added, removed, or modified, and provides a clear view of the modifications in the repository.\n
"""
