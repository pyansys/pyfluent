"""Provides a module to search a word through the Fluent's object hierarchy.."""

from collections.abc import Mapping
import fnmatch
import os
from pathlib import Path
import pickle
from typing import Any, Optional
import warnings

from nltk.corpus import wordnet as wn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from spellchecker import SpellChecker

import ansys.fluent.core as pyfluent
from ansys.fluent.core.services.datamodel_se import PyMenu, PyNamedObjectContainer
from ansys.fluent.core.services.datamodel_tui import TUIMenu
from ansys.fluent.core.session_pure_meshing import PureMeshing
from ansys.fluent.core.session_solver import Solver
from ansys.fluent.core.solver import flobject
from ansys.fluent.core.utils.fluent_version import (
    FluentVersion,
    get_version_for_file_name,
)
from ansys.fluent.core.workflow import (
    BaseTask,
    ClassicWorkflow,
    TaskContainer,
    Workflow,
)

_THIS_DIRNAME = os.path.dirname(__file__)


class ValueConflict(ValueError):
    """Raised when both ``wildcard`` and ``match_whole_word`` are ``True``."""

    def __init__(self):
        super().__init__(
            "Provide either ``wildcard`` or ``match_whole_word`` as ``True``."
        )


def get_api_tree_file_name(
    version: Optional[str] = None,
    text: Optional[bool] = None,
    name: Optional[bool] = None,
    tui: Optional[bool] = None,
) -> Path:
    """Get API tree file name."""
    from ansys.fluent.core import CODEGEN_OUTDIR

    text_file_folder = Path(os.path.join(_THIS_DIRNAME, "api_tree"))
    if text:
        return (text_file_folder / "api_tree.txt").resolve()
    elif name:
        return (text_file_folder / "api_tree_names.txt").resolve()
    elif tui:
        return (text_file_folder / "api_tree_tui.txt").resolve()
    else:
        return (CODEGEN_OUTDIR / f"api_tree_{version}.pickle").resolve()


def _match(source: str, word: str, match_whole_word: bool, match_case: bool):
    if not match_case:
        source = source.lower()
        word = word.lower()
    if match_whole_word:
        return source == word
    else:
        return word in source


def _remove_suffix(input: str, suffix):
    if hasattr(input, "removesuffix"):
        return input.removesuffix(suffix)
    else:
        if suffix and input.endswith(suffix):
            return input[: -len(suffix)]
        return input


_meshing_rules = ["workflow", "meshing", "PartManagement", "PMFileManagement"]


def _get_version_path_prefix_from_obj(obj: Any):
    path = None
    version = None
    prefix = None
    if isinstance(obj, PureMeshing):
        path = ["<meshing_session>"]
        version = get_version_for_file_name(obj.get_fluent_version().value)
        prefix = "<search_root>"
    elif isinstance(obj, Solver):
        path = ["<solver_session>"]
        version = get_version_for_file_name(obj.get_fluent_version().value)
        prefix = "<search_root>"
    elif isinstance(obj, TUIMenu):
        path = ["<session>", "tui"]
        path.extend(obj._path)
        module = obj.__class__.__module__
        version = module.rsplit("_", 1)[-1]
        prefix = "<search_root>"
    elif isinstance(obj, (ClassicWorkflow, Workflow)):
        path = ["<meshing_session>", obj.rules]
        prefix = "<search_root>"
    elif isinstance(obj, BaseTask):
        path = ["<meshing_session>", obj.rules]
        path.extend([f"{k[0]}:<name>" if k[1] else k[0] for k in obj.path])
        prefix = "<search_root>"
    elif isinstance(obj, TaskContainer):
        path = ["<meshing_session>", obj.rules]
        path.extend([f"{k[0]}:<name>" if k[1] else k[0] for k in obj.path])
        path[-1] = f"{path[-1]}:<name>"
        prefix = '<search_root>["<name>"]'
    elif isinstance(obj, PyMenu):
        rules = obj.rules
        path = ["<meshing_session>" if rules in _meshing_rules else "<solver_session>"]
        path.append(rules)
        path.extend([f"{k[0]}:<name>" if k[1] else k[0] for k in obj.path])
        prefix = "<search_root>"
    elif isinstance(obj, PyNamedObjectContainer):
        rules = obj.rules
        path = ["<meshing_session>" if rules in _meshing_rules else "<solver_session>"]
        path.append(rules)
        path.extend([f"{k[0]}:<name>" if k[1] else k[0] for k in obj.path])
        path[-1] = f"{path[-1]}:<name>"
        prefix = '<search_root>["<name>"]'
    elif isinstance(obj, flobject.Group):
        module = obj.__class__.__module__
        version = module.split(".")[-2].rsplit("_", 1)[-1]
        prefix = "<search_root>"
        path = ["<solver_session>"]
        # Cannot deduce the whole path without api_tree
    elif isinstance(obj, flobject.NamedObject):
        module = obj.__class__.__module__
        version = module.split(".")[-2].rsplit("_", 1)[-1]
        prefix = '<search_root>["<name>"]'
        path = ["<solver_session>"]
        # Cannot deduce the whole path without api_tree
    return version, path, prefix


def _search(
    word: str,
    match_whole_word: bool = False,
    match_case: bool = False,
    version: Optional[str] = None,
    search_root: Optional[Any] = None,
):
    """Search for a word through the Fluent's object hierarchy.

    Parameters
    ----------
    word : str
        The word to search for.
    match_whole_word : bool, optional
        Whether to match whole word, by default False
    match_case : bool, optional
        Whether to match case, by default False
    version : str, optional
        Fluent version to search in, by default None in which case
        it will search in the latest version for which codegen was run.
    search_root : Any, optional
        The root object within which the search will be performed,
        can be a session object or any API object within a session,
        by default None in which case it will search everything.

    Examples
    --------
    >>> import ansys.fluent.core as pyfluent
    >>> pyfluent.search("geometry")
    <meshing_session>.tui.file.import_.cad_geometry (Command)
    <meshing_session>.tui.display.update_scene.select_geometry (Command)
    <meshing_session>.meshing.ImportGeometry (Command)
    <meshing_session>.meshing.LoadCADGeometry (Command)
    <solver_session>.tui.solve.initialize.compute_defaults.geometry (Command)
    <solver_session>.tui.report.reference_values.compute.geometry (Command)
    <solver_session>.tui.define.geometry (Command)
    <solver_session>.tui.mesh.geometry (Object)
    <solver_session>.setup.boundary_conditions.geometry["<name>"] (Object)
    <solver_session>.setup.geometry (Object)
    <solver_session>.solution.report_definitions.surface["<name>"].geometry (Parameter)
    <solver_session>.solution.report_definitions.volume["<name>"].geometry (Parameter)
    <solver_session>.results.graphics.mesh["<name>"].geometry (Parameter)
    <solver_session>.results.graphics.contour["<name>"].geometry (Parameter)
    """
    api_objects = []
    api_tui_objects = []
    api_object_names = set()
    if version:
        version = get_version_for_file_name(version)
    root_version, root_path, prefix = _get_version_path_prefix_from_obj(search_root)
    if search_root and not prefix:
        return
    if not version:
        version = root_version
    if not version:
        for fluent_version in FluentVersion:
            version = get_version_for_file_name(fluent_version.value)
            if get_api_tree_file_name(version).exists():
                break
    api_tree_file = get_api_tree_file_name(version)
    with open(api_tree_file, "rb") as f:
        api_tree = pickle.load(f)

    if isinstance(search_root, (flobject.Group, flobject.NamedObject)):
        path = root_path + [
            flobject.to_python_name(x) for x in search_root.path.split("/")
        ]
        root_path = []
        tree = api_tree
        while path:
            p = path.pop(0)
            if p in tree:
                tree = tree[p]
                root_path.append(p)
            elif f"{p}:<name>" in tree:
                tree = tree[f"{p}:<name>"]
                root_path.append(f"{p}:<name>")
                if path:
                    path.pop(0)
            else:
                return

    def inner(tree, path, root_path):
        if root_path:
            path = prefix
        while root_path:
            p = root_path.pop(0)
            # With the dynamic loading of generated api modules, we loose the filepath information
            # from which we were extracting the solver/meshing mode of the given object.
            # Anyway, we are planning to remove search_root in the newer version of search function.
            if p == "<session>":
                p = "<solver_session>"
            if p in tree:
                tree = tree[p]
            else:
                return

        for k, v in tree.items():
            if k in ("<meshing_session>", "<solver_session>"):
                next_path = k
            else:
                if k.endswith(":<name>"):
                    k = _remove_suffix(k, ":<name>")
                    next_path = f'{path}.{k}["<name>"]'
                else:
                    next_path = f"{path}.{k}"
                type_ = "Object" if isinstance(v, Mapping) else v
                api_object_names.add(k)
                if "tui" in next_path:
                    api_tui_objects.append(f"{next_path} ({type_})")
                else:
                    api_objects.append(f"{next_path} ({type_})")
                if _match(k, word, match_whole_word, match_case):
                    print(f"{next_path} ({type_})")
            if isinstance(v, Mapping):
                inner(v, next_path, root_path)

    inner(api_tree, "", root_path)

    def _write_file(
        api_objects: list,
        text: Optional[bool] = False,
        tui: Optional[bool] = False,
        name: Optional[bool] = None,
    ):
        api_tree_file = get_api_tree_file_name(text=text, name=name, tui=tui)
        api_tree_file.touch()
        with open(api_tree_file, "w") as file:
            for api_object in api_objects:
                file.write(f"{api_object}")
                file.write("\n")

    if pyfluent.WRITE_API_SEARCH_OBJECTS_FILE:

        text_file_folder = Path(os.path.join(_THIS_DIRNAME, "api_tree"))
        text_file_folder.mkdir(parents=True, exist_ok=True)

        _write_file(api_objects=api_objects, text=True)
        _write_file(api_objects=api_tui_objects, tui=True)
        _write_file(api_objects=api_object_names, name=True)


def _process_wildcards(word: str, names: list):
    """Process wildcard pattern in the given word.

    Parameters
    ----------
    word: str
        The word to search for.
    names: list
        All API object names.

    Returns
    -------
    wildcard_matches: list
        Matched API object names.
    """
    wildcard_matches = []
    for name in names:
        if fnmatch.fnmatch(name, word):
            wildcard_matches.append(name)
    return wildcard_matches


def _process_misspelled(
    word: str,
    names_txt_file,
    names: list,
    match_whole_word: Optional[bool] = False,
    match_case: Optional[bool] = False,
):
    """Process misspelled word.

    Parameters
    ----------
    word: str
        The word to search for.
    names_txt_file:
        Text file containing all API object names.
    names: list
        All API object names.
    match_whole_word: bool
        Whether to match whole case.
    match_case: bool
        Whether to match case.

    Returns
    -------
    correct_spell: list
        List of corrected spell.
    """
    correct_spell = []
    possible_corrections = []
    spell = SpellChecker()
    spell.word_frequency.load_text_file(names_txt_file)
    spell.word_frequency.load_words(names)
    misspelled = spell.unknown([word])
    if misspelled:
        for name in misspelled:
            correct_spell.append(spell.correction(name))
            possible_corrections.extend(list(spell.candidates(name)))
        if match_whole_word and correct_spell == possible_corrections:
            return correct_spell
        elif match_case:
            corrections_in_tree = set()
            for correction in possible_corrections:
                for name in names:
                    if correction in name:
                        corrections_in_tree.add(correction)
            return list(corrections_in_tree)
    else:
        return [word]


def search(
    search_string: str,
    language: Optional[str] = "eng",
    wildcard: Optional[bool] = False,
    match_whole_word: Optional[bool] = False,
    match_case: Optional[bool] = True,
):
    """Search for a word through the Fluent's object hierarchy.

    Parameters
    ----------
    search_string: str
        The word to search for. Semantic search is default.
    language: str
        The language for the semantic search. English is default for the semantic search.
        'albanian':'als', 'arabic':'arb', 'bulgarian':'bul', 'chinese_simplified':'cmn', 'chinese_traditional':'qcn',
        'danish':'dan', 'greek':'ell', 'english':'eng', 'persian':'fas', 'finnish':'fin', 'french':'fra',
        'hebrew':'heb', 'croatian':'hrv', 'icelandic':'isl', 'italian':'ita', 'japanese':'jpn', 'catalan':'cat',
        'basque':'eus', 'galicain':'glg', 'spanish':'spa', 'indonesian':'ind', 'malay':'zsm', 'dutch':'nld',
        'polish':'pol', 'portuguese':'por', 'romanian':'ron', 'lithuanian':'lit', 'slovak':'slk', 'slovene':'slv',
        'swedish':'swe', 'thai':'tha'
    wildcard: bool
        Whether to use wildcard pattern. If ``True`` will match wildcard pattern based on ``fnmatch`` module and
        will turn off semantic matching.
    match_whole_word: bool
        Whether to get exact match. If ``True`` will match exact string and will turn off semantic matching.
    match_case: bool
        Whether to match case. If ``True`` will match case-insensitive case.

    Raises
    ------
    ValueConflict
        If both ``wildcard`` and ``match_whole_word`` are ``True``.

    Examples
    --------
    >>> import ansys.fluent.core as pyfluent
    >>> pyfluent.search("font", match_whole_word=True)
    >>> pyfluent.search("Font")
    >>> pyfluent.search("iter*", wildcard=True)
    >>> pyfluent.search("读", language="cmn")   # search 'read' in Chinese
    The most similar API objects are:
    <solver_session>.file.read (Command)
    <solver_session>.file.import_.read (Command)
    <solver_session>.mesh.surface_mesh.read (Command)
    <solver_session>.tui.display.display_states.read (Command)
    <meshing_session>.tui.display.display_states.read (Command)
    """
    if wildcard and match_whole_word:
        raise ValueConflict()
    elif language and match_whole_word:
        warnings.warn(
            "``match_whole_word=True`` will match exact string and will turn off semantic matching.",
            UserWarning,
        )
    elif match_whole_word:
        warnings.warn(
            "``match_whole_word=True`` will turn off semantic and wildcard matching.",
            UserWarning,
        )

    api_object_names = get_api_tree_file_name(name=True)
    names_txt = open(api_object_names, "r")
    names = [name.replace("\n", "") for name in names_txt.readlines()]
    synset_1 = wn.synsets(search_string, lang=language)

    if wildcard and not match_whole_word:
        queries = _process_wildcards(search_string, names)
    elif synset_1 and not match_whole_word and not wildcard:
        similar_keys = set()
        for name in names:
            synset_2 = wn.synsets(name, lang="eng")
            for s1 in synset_1:
                for s2 in synset_2:
                    name_s1 = s1.name().split(".")[0]
                    name_s2 = s2.name().split(".")[0]
                    if search_string in name_s2 or name_s1 in name_s2:
                        similar_keys.add(name_s2 + "*")
        queries = set()
        for key in similar_keys:
            queries.update(set(_process_wildcards(key, names)))
        queries = list(queries)
        wildcard = True
    elif match_whole_word and not wildcard:
        queries = _process_misspelled(
            word=search_string,
            names_txt_file=api_object_names,
            names=names,
            match_whole_word=match_whole_word,
        )
    elif match_case:
        queries = _process_misspelled(
            word=search_string,
            names_txt_file=api_object_names,
            names=names,
            match_case=match_case,
        )

    api_tree = get_api_tree_file_name(text=True)
    api_tui_tree = get_api_tree_file_name(tui=True)
    text_files = [api_tree, api_tui_tree]
    print("\n The most similar API objects are: \n")
    for text_file in text_files:
        text = open(text_file, "r")
        api_objects = [api_object.replace("\n", "") for api_object in text.readlines()]
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(api_objects)
        for query in queries:
            query_vector = tfidf_vectorizer.transform([query])
            cosine_similarities = cosine_similarity(query_vector, tfidf_matrix)
            if wildcard:
                most_similar_api_object_index = cosine_similarities.argmax()
                if query in api_objects[most_similar_api_object_index]:
                    print(api_objects[most_similar_api_object_index])
            else:
                most_similar_api_object_indices = cosine_similarities.argsort()
                for most_similar_api_object_index in reversed(
                    most_similar_api_object_indices[0][-3:]
                ):
                    if query in api_objects[most_similar_api_object_index]:
                        print(api_objects[most_similar_api_object_index])
