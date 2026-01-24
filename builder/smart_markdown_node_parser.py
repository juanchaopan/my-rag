from calendar import c
from typing import Any, Callable, List, Sequence, cast
from exceptiongroup import catch
from llama_index.core.node_parser import NodeParser
from llama_index.core.schema import (
    BaseNode,
    TextNode,
    NodeRelationship,
    RelatedNodeInfo,
)
from llama_index.core.utils import get_tokenizer, get_tqdm_iterable
from marko.md_renderer import MarkdownRenderer
from marko import Markdown
from marko.block import Element, BlockElement, Quote, List, FencedCode
from pydantic import PrivateAttr, Field
from re import findall, DOTALL, split
from pygments.lexers import guess_lexer
from llama_index.core.node_parser import CodeSplitter, SentenceSplitter
from magika import Magika


class Pair:
    node: TextNode
    token_count: int

    def __init__(self, node: TextNode, token_count: int) -> None:
        self.node = node
        self.token_count = token_count


class SmartMarkdownNodeParser(NodeParser):
    chunk_size: int = Field(default=0)
    _tokenizer: Callable = PrivateAttr()
    _md: Markdown = PrivateAttr()
    _magika: Magika = PrivateAttr()
    _sentence_splitter: SentenceSplitter = PrivateAttr()

    def __init__(
        self,
        chunk_size: int = 512,
        tokenizer: Callable = get_tokenizer(),
    ) -> None:
        super().__init__()
        self.chunk_size = chunk_size
        self._tokenizer = tokenizer
        self._md = Markdown(renderer=MarkdownRenderer)
        self._magika = Magika()
        self._sentence_splitter = SentenceSplitter(chunk_size=self.chunk_size)

    def _parse_nodes(
        self,
        nodes: Sequence[BaseNode],
        show_progress: bool = False,  # TODO
        **kwargs: Any,
    ) -> list[BaseNode]:
        all_parsed_nodes = []
        nodes_with_progress = get_tqdm_iterable(nodes, show_progress, "Parsing nodes")
        for node in nodes_with_progress:
            parsed_nodes = self._parse_node(node)
            all_parsed_nodes += parsed_nodes
        return all_parsed_nodes

    def _parse_node(self, node: BaseNode) -> list[BaseNode]:
        text = node.get_content()
        document = self._md.parse(text)
        self._md.renderer.root_node = document
        pairs = self.traverse(document)
        nodes = [x.node for x in pairs]
        return nodes

    def traverse(self, element: Element) -> list[Pair]:
        if isinstance(element, Quote):
            pairs_list = self.traverse_quote_children(element)
        elif isinstance(element, List):
            pairs_list = self.traverse_list_children(element)
        elif isinstance(element, BlockElement):
            pairs_list = self.traverse_children(element)
        else:
            pairs_list: list[list[Pair]] = []
        pairs_list = self.merge_adjacent(pairs_list)
        pairs_list = self.link_adjacent(pairs_list)
        pairs_list = self.attach_head(element, pairs_list)
        flattened = self.flatten(pairs_list)
        return flattened

    def traverse_quote_children(self, element: Quote) -> list[list[Pair]]:
        children = [x for x in element.children if isinstance(x, BlockElement)]
        renderer = cast(MarkdownRenderer, self._md.renderer)
        with renderer.container("> ", "> "):
            return [self.traverse(x) for x in children]

    def traverse_list_children(self, element: List) -> list[list[Pair]]:
        pairs_list: list[list[Pair]] = []
        children = [x for x in element.children if isinstance(x, BlockElement)]
        renderer = cast(MarkdownRenderer, self._md.renderer)
        if element.ordered:
            for i, child in enumerate(children, element.start):
                with renderer.container(f"{i}. ", " " * (len(str(i)) + 2)):
                    pairs_list.append(self.traverse(child))
        else:
            for child in children:
                with renderer.container(f"{element.bullet} ", "  "):
                    pairs_list.append(self.traverse(child))
        return pairs_list

    def traverse_children(self, element: BlockElement) -> list[list[Pair]]:
        return [
            self.traverse(x) for x in element.children if isinstance(x, BlockElement)
        ]

    def merge_adjacent(self, pairs_list: list[list[Pair]]) -> list[list[Pair]]:
        merged_pairs_list: list[list[Pair]] = []
        if pairs_list:
            merged_pairs_list.append(pairs_list[0])
        for i in range(1, len(pairs_list)):
            pairs = pairs_list[i]
            if len(pairs) == 1:
                last_merged_pairs = merged_pairs_list[-1] if merged_pairs_list else None
                if (
                    last_merged_pairs
                    and len(last_merged_pairs) == 1
                    and last_merged_pairs[0].token_count + pairs[0].token_count
                    <= self.chunk_size
                ):
                    last_merged_pairs[0].node.text += pairs[0].node.text
                    last_merged_pairs[0].token_count += pairs[0].token_count
                else:
                    merged_pairs_list.append(pairs)
        return merged_pairs_list

    def link_adjacent(self, pairs_list: list[list[Pair]]) -> list[list[Pair]]:
        for i in range(len(pairs_list) - 1):
            curr_pairs = pairs_list[i]
            next_pairs = pairs_list[i + 1]
            curr_pairs[0].node.relationships[NodeRelationship.NEXT] = RelatedNodeInfo(
                node_id=next_pairs[0].node.node_id
            )
            next_pairs[0].node.relationships[NodeRelationship.PREVIOUS] = (
                RelatedNodeInfo(node_id=curr_pairs[0].node.node_id)
            )
        return pairs_list

    def attach_head(
        self, head: Element, pairs_list: list[list[Pair]]
    ) -> list[list[Pair]]:
        head_text = self.render_token(head)
        head_token_count = len(self._tokenizer(head_text))
        if (
            pairs_list
            and head_token_count + pairs_list[0][0].token_count <= self.chunk_size
        ):
            new_head = False
            head_pair = pairs_list[0][0]
            head_pair.node.text = head_text + head_pair.node.text
            head_pair.token_count += head_token_count
        elif head_token_count <= self.chunk_size:
            new_head = True
            head_pair = Pair(TextNode(text=head_text), head_token_count)
            head_pairs = [head_pair]
        else:
            new_head = True
            head_pairs = [
                Pair(x, len(self._tokenizer(x.text))) for x in self.code_nodes(head)
            ]
            head_pair = head_pairs[0]
        for pairs in pairs_list:
            if pairs[0].node != head_pair.node:
                if (
                    pairs[0].node.relationships.get(NodeRelationship.PREVIOUS).node_id
                    == head_pair.node.node_id
                ):
                    pairs[0].node.relationships.pop(NodeRelationship.PREVIOUS)
                pairs[0].node.relationships[NodeRelationship.PARENT] = RelatedNodeInfo(
                    node_id=head_pair.node.node_id
                )
        return [[head_pair]] + pairs_list if new_head else pairs_list

    def code_nodes(self, element: FencedCode) -> list[TextNode]:
        fenced_code_text = self._md.render(element)
        code_lines = findall(r"```(?:\n)?(.*?)(?:\n)?```", fenced_code_text, DOTALL)
        code_text = "\n".join(code_lines)
        result = self._magika.identify_bytes(code_text.encode()).output
        label = result.label
        language = self.map_language(label)
        split_code_texts = self.split_code(code_text, language)
        elements = [FencedCode((language, "", x)) for x in split_code_texts]
        split_code_mds = [self.render_token(x) for x in elements]
        nodes = [TextNode(text=x) for x in split_code_mds]
        for i in range(len(nodes) - 1):
            nodes[i].relationships[NodeRelationship.NEXT] = RelatedNodeInfo(
                node_id=nodes[i + 1].node_id
            )
            nodes[i + 1].relationships[NodeRelationship.PREVIOUS] = RelatedNodeInfo(
                node_id=nodes[i].node_id
            )
        return nodes

    def split_code(self, code_text: str, language: str) -> list[str]:
        if language:
            try:
                code_splitter = CodeSplitter(
                    count_mode="token",
                    max_tokens=self.chunk_size,
                    language=language,
                )
                split_code_texts = code_splitter.split_text(code_text)
                if not split_code_texts:
                    raise Exception("Empty split result")
            except Exception:
                split_code_texts = self._sentence_splitter.split_text(code_text)
        else:
            split_code_texts = self._sentence_splitter.split_text(code_text)
        return split_code_texts

    def map_language(self, pygments_name: str) -> str:
        match pygments_name:
            case "ada":
                return "ada"
            case "asm":
                return "asm"
            case "bib":
                return "bibtex"
            case "c":
                return "c"
            case "clojure":
                return "clojure"
            case "cmake":
                return "cmake"
            case "cobol":
                return "cobol"
            case "cpp":
                return "cpp"
            case "cs":
                return "csharp"
            case "css":
                return "css"
            case "csv":
                return "csv"
            case "dart":
                return "dart"
            case "dockerfile":
                return "dockerfile"
            case "elixir":
                return "elixir"
            case "erb":
                return "embeddedtemplate"
            case "erlang":
                return "erlang"
            case "fortran":
                return "fortran"
            case "gitattributes":
                return "gitattributes"
            case "go":
                return "go"
            case "graphql":
                return "graphql"
            case "groovy":
                return "groovy"
            case "haskell":
                return "haskell"
            case "hcl":
                return "hcl"
            case "html":
                return "html"
            case "ignorefile":
                return "gitignore"
            case "ini":
                return "ini"
            case "java":
                return "java"
            case "javascript":
                return "javascript"
            case "json":
                return "json"
            case "julia":
                return "julia"
            case "kotlin":
                return "kotlin"
            case "latex":
                return "latex"
            case "lisp":
                return "commonlisp"
            case "lua":
                return "lua"
            case "makefile":
                return "make"
            case "markdown":
                return "markdown"
            case "matlab":
                return "matlab"
            case "objectivec":
                return "objc"
            case "ocaml":
                return "ocaml"
            case "pascal":
                return "pascal"
            case "pem":
                return "pem"
            case "perl":
                return "perl"
            case "php":
                return "php"
            case "po":
                return "po"
            case "powershell":
                return "powershell"
            case "proto":
                return "proto"
            case "python":
                return "python"
            case "r":
                return "r"
            case "rst":
                return "rst"
            case "ruby":
                return "ruby"
            case "rust":
                return "rust"
            case "scala":
                return "scala"
            case "scss":
                return "scss"
            case "shell":
                return "bash"
            case "smali":
                return "smali"
            case "solidity":
                return "solidity"
            case "sql":
                return "sql"
            case "swift":
                return "swift"
            case "tcl":
                return "tcl"
            case "toml":
                return "toml"
            case "tsv":
                return "tsv"
            case "twig":
                return "twig"
            case "typescript":
                return "typescript"
            case "verilog":
                return "verilog"
            case "vhdl":
                return "vhdl"
            case "vue":
                return "vue"
            case "wasm":
                return "wat"
            case "xml":
                return "xml"
            case "yaml":
                return "yaml"
            case "zig":
                return "zig"
            case _:
                return ""

    def render_token(self, element: Element) -> str:
        if isinstance(element, BlockElement) and all(
            isinstance(x, BlockElement) for x in element.children
        ):
            children = element.children
            element.children = []
            text = self._md.renderer.render(element)
            element.children = children
        else:
            text = self._md.renderer.render(element)
        return text

    def flatten(self, pairs_list: list[list[Pair]]) -> list[Pair]:
        flat_pairs = []
        for pairs in pairs_list:
            flat_pairs += pairs
        return flat_pairs


if __name__ == "__main__":
    import marko
    import marko.md_renderer
    import jsonlines
    from marko.block import Element, BlockElement
    from marko.element import RawText

    with jsonlines.open("langchain-ai-docs.jsonl", "r") as f:
        for line in f:
            if line["id"] != "/langsmith/enqueue-concurrent":
                continue
            text = line["content"]

            md = marko.Markdown(renderer=marko.md_renderer.MarkdownRenderer)
            parse = md.parse
            render = md.render

            document = parse(text)
            markdown = render(document)
            markdown2 = render(document.children[1])
            pass
