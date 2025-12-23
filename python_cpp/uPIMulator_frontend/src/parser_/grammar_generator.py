import os
import subprocess
from typing import List

from util.path_collector import PathCollector


class GrammarGenerator:
    def __init__(self):
        pass

    @staticmethod
    def generate() -> bool:
        grammar_path = GrammarGenerator._grammar_path_in_local()
        cd = f"cd {grammar_path}"
        antlr = f"{GrammarGenerator._antlr()} -Dlanguage=Python3 {GrammarGenerator.grammar()}.g4"

        command = f"{cd} && {antlr}"
        try:
            subprocess.run(command, shell=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def clean() -> bool:
        grammar_path = GrammarGenerator._grammar_path_in_local()
        commands = []
        for filename in GrammarGenerator.generated_filenames():
            commands.append(f"rm -f {os.path.join(grammar_path, filename)}")
        
        command = " && ".join(commands)
        if not command:
            return True
            
        try:
            subprocess.run(command, shell=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def grammar() -> str:
        return "assembly"

    @staticmethod
    def generated_filenames() -> List[str]:
        return [
            f"{GrammarGenerator.grammar()}.interp",
            f"{GrammarGenerator.grammar()}.tokens",
            f"{GrammarGenerator.grammar()}Lexer.interp",
            f"{GrammarGenerator.grammar()}Lexer.py",
            f"{GrammarGenerator.grammar()}Lexer.tokens",
            f"{GrammarGenerator.grammar()}Listener.py",
            f"{GrammarGenerator.grammar()}Parser.py",
        ]

    @staticmethod
    def _grammar_path_in_local() -> str:
        return os.path.join(PathCollector.src_path_in_local(), "parser_", "grammar")

    @staticmethod
    def _class_path() -> str:
        return f"{os.environ.get('ANTLR_JAR', '/usr/local/lib/antlr-4.9.2-complete.jar')}:$CLASSPATH"

    @staticmethod
    def _antlr() -> str:
        return f'java -Xmx500M -cp "{GrammarGenerator._class_path()}" org.antlr.v4.Tool'

    @staticmethod
    def _grun() -> str:
        return f'java -Xmx500M -cp "{GrammarGenerator._class_path()}" org.antlr.v4.gui.TestRig'
