import os
import subprocess


class CodingAgentFS:
    """
    A simple filesystem toolkit for coding agents.
    All operations are relative to the given working directory.
    """

    def __init__(self, workdir: str = "."):
        """
        Initialize the toolkit with a working directory.

        Args:
            workdir: Root directory for all operations. Defaults to current directory.
        """
        self.workdir = os.path.abspath(workdir)

    def _resolve(self, path: str) -> str:
        """Resolve a relative path against the working directory."""
        return os.path.join(self.workdir, path)

    def read_file(self, path: str) -> str:
        """
        Read and return the contents of a file.

        Args:
            path: Path to the file, relative to workdir.

        Returns:
            The file contents as a string.
        """
        with open(self._resolve(path), "r") as f:
            return f.read()

    def write_file(self, path: str, content: str) -> str:
        """
        Write content to a file, creating parent directories if needed.

        Args:
            path: Path to the file, relative to workdir.
            content: Text content to write.

        Returns:
            Confirmation message with the resolved path.
        """
        full_path = self._resolve(path)
        os.makedirs(os.path.dirname(full_path) or self.workdir, exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
        return f"Written to {full_path}"

    def file_tree(self, path: str = ".") -> str:
        """
        Return a tree view of the directory structure.

        Args:
            path: Subdirectory to tree, relative to workdir. Defaults to workdir root.

        Returns:
            A formatted string representing the directory tree.
        """
        root_path = self._resolve(path)
        result = []
        for root, dirs, files in os.walk(root_path):
            dirs[:] = [d for d in dirs if not d.startswith(".")]  # skip hidden
            depth = root.replace(root_path, "").count(os.sep)
            indent = "  " * depth
            result.append(f"{indent}{os.path.basename(root)}/")
            for file in files:
                result.append(f"{indent}  {file}")
        return "\n".join(result)

    def grep(self, pattern: str, path: str = ".") -> str:
        """
        Search for a pattern in a file or directory (recursive).

        Args:
            pattern: The string or regex pattern to search for.
            path: File or directory to search in, relative to workdir. Defaults to workdir root.

        Returns:
            Matching lines with filenames and line numbers, or a no-match message.
        """
        result = subprocess.run(
            ["grep", "-rn", pattern, self._resolve(path)],
            capture_output=True, text=True
        )
        return result.stdout or "No matches found."

    def run(self, command: str) -> str:
        """
        Execute a bash command inside the working directory.

        Args:
            command: The shell command to execute.

        Returns:
            Combined stdout and stderr output of the command.
        """
        result = subprocess.run(
            command, shell=True, capture_output=True,
            text=True, cwd=self.workdir
        )
        return result.stdout + result.stderr